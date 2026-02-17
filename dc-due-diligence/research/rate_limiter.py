"""
Token-bucket rate limiter with asyncio.Semaphore for concurrent request control.

Each API gets its own rate limiter that enforces both:
  - **Sustained rate**: tokens replenish over time up to a monthly budget.
  - **Burst concurrency**: an asyncio.Semaphore caps how many requests can be
    in flight at once so a wave of parallel agents doesn't overwhelm one API.

Usage::

    limiter = RateLimiter(api_name="tavily", max_requests=1000, period_seconds=2_592_000, max_concurrent=3)
    async with limiter.acquire():
        response = await tavily_client.search(query)
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RateLimiterStats:
    """Snapshot of a rate limiter's counters for debugging.

    Attributes:
        api_name: Which API this tracks.
        requests_made: Total requests that passed through the limiter.
        requests_throttled: Requests that had to wait for a token.
        requests_rejected: Requests rejected because the bucket was empty
            and the caller chose not to wait.
        tokens_remaining: Approximate tokens left in the bucket right now.
        max_tokens: Bucket capacity.
    """

    api_name: str
    requests_made: int
    requests_throttled: int
    requests_rejected: int
    tokens_remaining: float
    max_tokens: float


class RateLimiter:
    """Token-bucket rate limiter with concurrency cap.

    Args:
        api_name: Human-readable name (e.g. ``"tavily"``) for logging.
        max_requests: Maximum requests allowed per period (bucket capacity).
        period_seconds: Length of the rate-limit window in seconds.
            Tokens refill at ``max_requests / period_seconds`` per second.
        max_concurrent: Maximum simultaneous in-flight requests.
    """

    def __init__(
        self,
        api_name: str,
        max_requests: int,
        period_seconds: float,
        max_concurrent: int = 3,
    ):
        self.api_name = api_name
        self.max_tokens = float(max_requests)
        self._tokens = float(max_requests)
        self._refill_rate = max_requests / period_seconds  # tokens per second
        self._last_refill = time.monotonic()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrent)

        # Counters
        self._requests_made = 0
        self._requests_throttled = 0
        self._requests_rejected = 0

    def _refill(self) -> None:
        """Add tokens based on elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        self._tokens = min(self.max_tokens, self._tokens + elapsed * self._refill_rate)
        self._last_refill = now

    async def _wait_for_token(self, timeout: float | None = None) -> bool:
        """Wait until a token is available or timeout expires.

        Returns True if a token was acquired, False if timed out.
        """
        deadline = (time.monotonic() + timeout) if timeout is not None else None

        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True

            # If there's a deadline and we've passed it, reject
            if deadline is not None and time.monotonic() >= deadline:
                return False

            # Wait for a fraction of the time it takes to generate one token,
            # but at least 0.05s to avoid busy-spinning.
            wait_time = max(0.05, min(1.0 / self._refill_rate if self._refill_rate > 0 else 1.0, 5.0))
            if deadline is not None:
                wait_time = min(wait_time, deadline - time.monotonic())
                if wait_time <= 0:
                    return False
            await asyncio.sleep(wait_time)

    def acquire(self, timeout: float | None = 30.0) -> _AcquireContext:
        """Return an async context manager that acquires both a token and a semaphore slot.

        Args:
            timeout: Maximum seconds to wait for a token. None means wait
                indefinitely. The semaphore wait is not subject to this timeout.

        Usage::

            async with limiter.acquire():
                await do_api_call()
        """
        return _AcquireContext(self, timeout)

    @property
    def tokens_remaining(self) -> float:
        """Approximate tokens available right now (without consuming any)."""
        elapsed = time.monotonic() - self._last_refill
        return min(self.max_tokens, self._tokens + elapsed * self._refill_rate)

    def stats(self) -> RateLimiterStats:
        """Return a snapshot of this limiter's counters."""
        return RateLimiterStats(
            api_name=self.api_name,
            requests_made=self._requests_made,
            requests_throttled=self._requests_throttled,
            requests_rejected=self._requests_rejected,
            tokens_remaining=self.tokens_remaining,
            max_tokens=self.max_tokens,
        )


class _AcquireContext:
    """Async context manager returned by ``RateLimiter.acquire()``."""

    def __init__(self, limiter: RateLimiter, timeout: float | None):
        self._limiter = limiter
        self._timeout = timeout

    async def __aenter__(self) -> None:
        # First acquire the concurrency semaphore (no timeout -- just queue)
        await self._limiter._semaphore.acquire()

        # Then acquire a token from the bucket
        got_token = await self._limiter._wait_for_token(self._timeout)
        if not got_token:
            # Release the semaphore since we won't make the request
            self._limiter._semaphore.release()
            self._limiter._requests_rejected += 1
            raise RateLimitExceeded(
                f"{self._limiter.api_name}: rate limit exceeded "
                f"(waited {self._timeout}s for a token)"
            )

        # Check if we had to wait at all (approximation: if tokens were < 1 before refill)
        if self._limiter._tokens < self._limiter.max_tokens - 1:
            self._limiter._requests_throttled += 1

        self._limiter._requests_made += 1

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self._limiter._semaphore.release()
        return None


class RateLimitExceeded(Exception):
    """Raised when a rate limiter cannot provide a token within the timeout."""
    pass


# ----------------------------------------------------------------
# Pre-configured limiters for each API tier
# ----------------------------------------------------------------

# Monthly seconds: 30 days * 24h * 60m * 60s = 2,592,000
_MONTH_SECONDS = 30 * 24 * 60 * 60


def create_default_limiters() -> dict[str, RateLimiter]:
    """Create rate limiters with default quotas for each supported API.

    These quotas match the free / starter tiers:
      - Tavily: 1,000 requests/month, 3 concurrent
      - Exa: 1,000 requests/month, 3 concurrent
      - Firecrawl: 500 requests/month, 2 concurrent
      - Apify: 100 requests/month, 1 concurrent (actors are expensive)

    Returns:
        A dict keyed by API name with configured RateLimiter instances.
    """
    return {
        "tavily": RateLimiter(
            api_name="tavily",
            max_requests=1000,
            period_seconds=_MONTH_SECONDS,
            max_concurrent=3,
        ),
        "exa": RateLimiter(
            api_name="exa",
            max_requests=1000,
            period_seconds=_MONTH_SECONDS,
            max_concurrent=3,
        ),
        "firecrawl": RateLimiter(
            api_name="firecrawl",
            max_requests=500,
            period_seconds=_MONTH_SECONDS,
            max_concurrent=2,
        ),
        "apify": RateLimiter(
            api_name="apify",
            max_requests=100,
            period_seconds=_MONTH_SECONDS,
            max_concurrent=1,
        ),
    }
