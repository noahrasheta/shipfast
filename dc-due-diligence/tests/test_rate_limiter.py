"""Tests for the token-bucket rate limiter."""

import asyncio
import time

import pytest

from research.rate_limiter import (
    RateLimiter,
    RateLimiterStats,
    RateLimitExceeded,
    create_default_limiters,
)


class TestRateLimiterConstruction:
    def test_initializes_with_full_bucket(self):
        limiter = RateLimiter("test", max_requests=100, period_seconds=3600)
        assert limiter.tokens_remaining >= 99.0  # allow small float drift
        assert limiter.api_name == "test"
        assert limiter.max_tokens == 100.0

    def test_stats_initial_state(self):
        limiter = RateLimiter("test", max_requests=50, period_seconds=3600)
        stats = limiter.stats()
        assert isinstance(stats, RateLimiterStats)
        assert stats.api_name == "test"
        assert stats.requests_made == 0
        assert stats.requests_throttled == 0
        assert stats.requests_rejected == 0
        assert stats.max_tokens == 50.0
        assert stats.tokens_remaining >= 49.0


class TestTokenConsumption:
    def test_acquire_consumes_token(self):
        limiter = RateLimiter("test", max_requests=10, period_seconds=3600)

        async def run():
            async with limiter.acquire():
                pass

        asyncio.run(run())
        stats = limiter.stats()
        assert stats.requests_made == 1
        assert stats.tokens_remaining < 10.0

    def test_multiple_acquires_consume_multiple_tokens(self):
        limiter = RateLimiter("test", max_requests=10, period_seconds=3600)

        async def run():
            for _ in range(5):
                async with limiter.acquire():
                    pass

        asyncio.run(run())
        stats = limiter.stats()
        assert stats.requests_made == 5

    def test_concurrent_acquires_respect_semaphore(self):
        # max_concurrent=2, so only 2 can be in flight at once
        limiter = RateLimiter(
            "test", max_requests=100, period_seconds=3600, max_concurrent=2
        )
        max_concurrent_seen = 0
        current_concurrent = 0

        async def worker():
            nonlocal max_concurrent_seen, current_concurrent
            async with limiter.acquire():
                current_concurrent += 1
                if current_concurrent > max_concurrent_seen:
                    max_concurrent_seen = current_concurrent
                await asyncio.sleep(0.05)
                current_concurrent -= 1

        async def run():
            await asyncio.gather(*[worker() for _ in range(6)])

        asyncio.run(run())
        assert max_concurrent_seen <= 2
        assert limiter.stats().requests_made == 6


class TestRateLimitExhaustion:
    def test_rejects_when_bucket_empty_and_timeout(self):
        # Very low bucket, very slow refill
        limiter = RateLimiter("test", max_requests=1, period_seconds=3600)

        async def run():
            # First request succeeds
            async with limiter.acquire(timeout=1.0):
                pass

            # Second request should fail (no tokens, timeout too short for refill)
            with pytest.raises(RateLimitExceeded) as exc_info:
                async with limiter.acquire(timeout=0.1):
                    pass
            assert "rate limit exceeded" in str(exc_info.value)

        asyncio.run(run())
        stats = limiter.stats()
        assert stats.requests_made == 1
        assert stats.requests_rejected == 1


class TestTokenRefill:
    def test_tokens_refill_over_time(self):
        # 10 tokens per second = refill very fast
        limiter = RateLimiter("test", max_requests=10, period_seconds=1)

        async def run():
            # Consume all tokens
            for _ in range(10):
                async with limiter.acquire():
                    pass

            # Wait for some refill
            await asyncio.sleep(0.2)

            # Should be able to acquire at least 1 more
            async with limiter.acquire():
                pass

        asyncio.run(run())
        assert limiter.stats().requests_made == 11


class TestCreateDefaultLimiters:
    def test_creates_all_four_apis(self):
        limiters = create_default_limiters()
        assert "tavily" in limiters
        assert "exa" in limiters
        assert "firecrawl" in limiters
        assert "apify" in limiters

    def test_limiters_have_correct_quotas(self):
        limiters = create_default_limiters()
        assert limiters["tavily"].max_tokens == 1000.0
        assert limiters["exa"].max_tokens == 1000.0
        assert limiters["firecrawl"].max_tokens == 500.0
        assert limiters["apify"].max_tokens == 100.0

    def test_each_limiter_is_independent(self):
        limiters = create_default_limiters()

        async def run():
            async with limiters["tavily"].acquire():
                pass

        asyncio.run(run())
        # Only tavily should show the request
        assert limiters["tavily"].stats().requests_made == 1
        assert limiters["exa"].stats().requests_made == 0
