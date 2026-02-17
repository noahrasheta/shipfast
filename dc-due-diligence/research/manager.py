"""
Unified web research manager with rate limiting, caching, and fallback.

Agents call ``research()`` or ``scrape()`` without knowing which API handles
the request.  The manager picks the best available API, checks the cache,
enforces rate limits, and falls back to an alternative when one API fails.

Usage::

    manager = WebResearchManager()
    response = await manager.search("data center zoning Dallas TX", data_type="general")
    result = await manager.scrape("https://county.gov/parcel/123", data_type="ownership")
    print(manager.stats())
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Sequence

from research.cache import CacheStats, ResponseCache
from research.models import (
    ActorRunResult,
    ScrapeResult,
    SearchAPIError,
    SearchResponse,
    SearchResult,
)
from research.rate_limiter import (
    RateLimiter,
    RateLimiterStats,
    RateLimitExceeded,
    create_default_limiters,
)

logger = logging.getLogger(__name__)

# Maps operation types to the ordered list of APIs that can handle them.
# The manager tries them in order, falling back on failure.
SEARCH_API_ORDER: list[str] = ["tavily", "exa"]
SCRAPE_API_ORDER: list[str] = ["firecrawl", "apify"]


@dataclass
class ManagerStats:
    """Combined stats from all sub-systems.

    Attributes:
        rate_limiters: Per-API rate limiter stats.
        cache: Cache usage stats.
        fallbacks_used: Number of times a fallback API was used after the
            primary failed.
        total_searches: Total search calls made through the manager.
        total_scrapes: Total scrape calls made through the manager.
    """

    rate_limiters: dict[str, RateLimiterStats]
    cache: CacheStats
    fallbacks_used: int
    total_searches: int
    total_scrapes: int


class WebResearchManager:
    """Orchestrates search and scrape calls with caching, rate limiting, and fallback.

    On construction the manager lazily initializes API clients -- it only
    creates a client when the corresponding API key is available in the
    environment.  This means the manager works even if some APIs aren't
    configured; it simply skips them during fallback.

    Args:
        cache: A ``ResponseCache`` instance.  If ``None``, a default one is
            created at ``~/.dc_due_diligence/research_cache.db``.
        rate_limiters: A dict of ``RateLimiter`` instances keyed by API name.
            If ``None``, default limiters are created for all four APIs.
        search_api_order: Ordered list of search API names to try.
        scrape_api_order: Ordered list of scrape API names to try.
    """

    def __init__(
        self,
        *,
        cache: ResponseCache | None = None,
        rate_limiters: dict[str, RateLimiter] | None = None,
        search_api_order: list[str] | None = None,
        scrape_api_order: list[str] | None = None,
    ):
        self._cache = cache or ResponseCache()
        self._limiters = rate_limiters or create_default_limiters()
        self._search_order = search_api_order or list(SEARCH_API_ORDER)
        self._scrape_order = scrape_api_order or list(SCRAPE_API_ORDER)

        # Lazily populated when first needed
        self._search_clients: dict[str, Any] = {}
        self._scrape_clients: dict[str, Any] = {}
        self._init_done = False

        # Counters
        self._fallbacks_used = 0
        self._total_searches = 0
        self._total_scrapes = 0

    def _ensure_clients(self) -> None:
        """Lazily create API clients for every API that has a key configured."""
        if self._init_done:
            return
        self._init_done = True

        # Search clients
        try:
            from research.tavily_client import TavilySearchClient
            self._search_clients["tavily"] = TavilySearchClient()
            logger.info("Tavily search client initialized")
        except (SearchAPIError, ImportError) as exc:
            logger.info("Tavily unavailable: %s", exc)

        try:
            from research.exa_client import ExaSearchClient
            self._search_clients["exa"] = ExaSearchClient()
            logger.info("Exa search client initialized")
        except (SearchAPIError, ImportError) as exc:
            logger.info("Exa unavailable: %s", exc)

        # Scrape clients
        try:
            from research.firecrawl_client import FirecrawlScrapeClient
            self._search_clients["firecrawl"] = FirecrawlScrapeClient()
            self._scrape_clients["firecrawl"] = self._search_clients["firecrawl"]
            logger.info("Firecrawl scrape client initialized")
        except (SearchAPIError, ImportError) as exc:
            logger.info("Firecrawl unavailable: %s", exc)

        try:
            from research.apify_client import ApifyScrapeClient
            self._search_clients["apify"] = ApifyScrapeClient()
            self._scrape_clients["apify"] = self._search_clients["apify"]
            logger.info("Apify scrape client initialized")
        except (SearchAPIError, ImportError) as exc:
            logger.info("Apify unavailable: %s", exc)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def search(
        self,
        query: str,
        *,
        data_type: str = "general",
        max_results: int = 5,
        preferred_api: str | None = None,
        timeout: float = 30.0,
    ) -> SearchResponse:
        """Search the web for a query, with caching, rate limiting, and fallback.

        The manager tries each search API in order.  If the first one fails
        or is rate-limited, it automatically tries the next one.  Successful
        results are cached so the same query won't hit the API again within
        the TTL window.

        Args:
            query: Natural-language search query.
            data_type: Determines cache TTL.  One of ``"ownership"``,
                ``"market"``, ``"news"``, or ``"general"``.
            max_results: Maximum results to return.
            preferred_api: Force a specific API (e.g. ``"tavily"``).
                Falls back to others if it fails.
            timeout: Maximum seconds per API attempt.

        Returns:
            A ``SearchResponse`` with normalized results.  If all APIs fail,
            returns a response with an error message and empty results.
        """
        self._ensure_clients()
        self._total_searches += 1

        # Build the API order: preferred first, then the rest
        api_order = self._build_api_order(self._search_order, preferred_api)

        errors: list[str] = []
        is_fallback = False

        for api_name in api_order:
            client = self._search_clients.get(api_name)
            if client is None:
                continue

            # Check cache first
            cache_key = ResponseCache.make_key(api_name, "search", query)
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit for %s search: %s", api_name, query[:60])
                return _deserialize_search_response(cached, query, api_name)

            # Acquire rate limit token
            limiter = self._limiters.get(api_name)
            if limiter is None:
                continue

            try:
                async with limiter.acquire(timeout=10.0):
                    response = await self._execute_search(
                        api_name, client, query, max_results=max_results, timeout=timeout
                    )
            except RateLimitExceeded:
                msg = f"{api_name}: rate limit exceeded"
                logger.warning(msg)
                errors.append(msg)
                is_fallback = True
                continue
            except SearchAPIError as exc:
                msg = f"{api_name}: {exc}"
                logger.warning("Search failed on %s: %s", api_name, exc)
                errors.append(msg)
                if exc.retryable:
                    is_fallback = True
                    continue
                # Non-retryable error -- still try fallback APIs
                is_fallback = True
                continue
            except Exception as exc:
                msg = f"{api_name}: unexpected error: {exc}"
                logger.error(msg)
                errors.append(msg)
                is_fallback = True
                continue

            if is_fallback:
                self._fallbacks_used += 1

            # Cache the successful response
            await self._cache.put(
                cache_key,
                _serialize_search_response(response),
                api_name=api_name,
                operation="search",
                query=query,
                data_type=data_type,
            )
            return response

        # All APIs failed
        error_summary = " | ".join(errors) if errors else "No search APIs available"
        logger.error("All search APIs failed for query: %s -- %s", query[:60], error_summary)
        return SearchResponse(
            query=query,
            results=[],
            source_api="none",
            error=error_summary,
        )

    async def scrape(
        self,
        url: str,
        *,
        data_type: str = "general",
        preferred_api: str | None = None,
        timeout: float = 60.0,
    ) -> ScrapeResult:
        """Scrape a URL, with caching, rate limiting, and fallback.

        Tries scraping APIs in order.  Firecrawl is preferred for its speed
        and markdown quality; Apify is the fallback for pages that need
        specialized actors.

        Args:
            url: The URL to scrape.
            data_type: Determines cache TTL.
            preferred_api: Force a specific scraping API.
            timeout: Maximum seconds per API attempt.

        Returns:
            A ``ScrapeResult`` with the page's markdown content.  If all
            APIs fail, returns a result with ``success=False`` and an error.
        """
        self._ensure_clients()
        self._total_scrapes += 1

        api_order = self._build_api_order(self._scrape_order, preferred_api)

        errors: list[str] = []
        is_fallback = False

        for api_name in api_order:
            client = self._scrape_clients.get(api_name)
            if client is None:
                continue

            # Check cache
            cache_key = ResponseCache.make_key(api_name, "scrape", url)
            cached = await self._cache.get(cache_key)
            if cached is not None:
                logger.debug("Cache hit for %s scrape: %s", api_name, url[:80])
                return _deserialize_scrape_result(cached, url, api_name)

            # Acquire rate limit token
            limiter = self._limiters.get(api_name)
            if limiter is None:
                continue

            try:
                async with limiter.acquire(timeout=10.0):
                    result = await self._execute_scrape(
                        api_name, client, url, timeout=timeout
                    )
            except RateLimitExceeded:
                msg = f"{api_name}: rate limit exceeded"
                logger.warning(msg)
                errors.append(msg)
                is_fallback = True
                continue
            except SearchAPIError as exc:
                msg = f"{api_name}: {exc}"
                logger.warning("Scrape failed on %s: %s", api_name, exc)
                errors.append(msg)
                is_fallback = True
                continue
            except Exception as exc:
                msg = f"{api_name}: unexpected error: {exc}"
                logger.error(msg)
                errors.append(msg)
                is_fallback = True
                continue

            if not result.success:
                msg = f"{api_name}: scrape returned error: {result.error}"
                errors.append(msg)
                is_fallback = True
                continue

            if is_fallback:
                self._fallbacks_used += 1

            # Cache the successful result
            await self._cache.put(
                cache_key,
                _serialize_scrape_result(result),
                api_name=api_name,
                operation="scrape",
                query=url,
                data_type=data_type,
            )
            return result

        # All APIs failed
        error_summary = " | ".join(errors) if errors else "No scrape APIs available"
        logger.error("All scrape APIs failed for URL: %s -- %s", url[:80], error_summary)
        return ScrapeResult(
            url=url,
            markdown="",
            source_api="none",
            success=False,
            error=error_summary,
        )

    def stats(self) -> ManagerStats:
        """Return combined stats from rate limiters, cache, and the manager itself."""
        return ManagerStats(
            rate_limiters={
                name: limiter.stats() for name, limiter in self._limiters.items()
            },
            cache=self._cache.stats(),
            fallbacks_used=self._fallbacks_used,
            total_searches=self._total_searches,
            total_scrapes=self._total_scrapes,
        )

    def close(self) -> None:
        """Close the cache database connection."""
        self._cache.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_api_order(default_order: list[str], preferred: str | None) -> list[str]:
        """Build the API try order, putting the preferred API first."""
        if preferred is None:
            return list(default_order)
        # Move preferred to front, keep remaining order
        order = [preferred]
        for api in default_order:
            if api != preferred:
                order.append(api)
        return order

    async def _execute_search(
        self,
        api_name: str,
        client: Any,
        query: str,
        *,
        max_results: int = 5,
        timeout: float = 30.0,
    ) -> SearchResponse:
        """Dispatch a search to the appropriate client."""
        if api_name == "tavily":
            return await client.search(
                query, max_results=max_results, timeout=timeout
            )
        elif api_name == "exa":
            return await client.search(
                query, num_results=max_results, timeout=timeout
            )
        else:
            raise SearchAPIError(
                api_name=api_name,
                message=f"Unknown search API: {api_name}",
            )

    async def _execute_scrape(
        self,
        api_name: str,
        client: Any,
        url: str,
        *,
        timeout: float = 60.0,
    ) -> ScrapeResult:
        """Dispatch a scrape to the appropriate client."""
        if api_name == "firecrawl":
            return await client.scrape(url, timeout=timeout)
        elif api_name == "apify":
            # Use the generic web-scraper actor for URL scraping
            actor_result: ActorRunResult = await client.run_actor(
                actor_id="apify/web-scraper",
                run_input={
                    "startUrls": [{"url": url}],
                    "pageFunction": (
                        "async function pageFunction(context) {\n"
                        "  const $ = context.jQuery;\n"
                        "  return { url: context.request.url, text: $('body').text() };\n"
                        "}"
                    ),
                },
                timeout_secs=int(timeout),
            )
            if actor_result.success and actor_result.items:
                text = actor_result.items[0].get("text", "")
                return ScrapeResult(
                    url=url,
                    markdown=text,
                    source_api="apify",
                    success=True,
                    metadata={"actor_id": actor_result.actor_id, "run_id": actor_result.run_id},
                )
            return ScrapeResult(
                url=url,
                markdown="",
                source_api="apify",
                success=False,
                error=actor_result.error or f"Actor finished with status: {actor_result.status}",
            )
        else:
            raise SearchAPIError(
                api_name=api_name,
                message=f"Unknown scrape API: {api_name}",
            )


# ------------------------------------------------------------------
# Serialization helpers for cache storage
# ------------------------------------------------------------------


def _serialize_search_response(response: SearchResponse) -> dict[str, Any]:
    """Convert a SearchResponse to a JSON-serializable dict."""
    return {
        "query": response.query,
        "source_api": response.source_api,
        "results": [
            {
                "title": r.title,
                "url": r.url,
                "snippet": r.snippet,
                "relevance_score": r.relevance_score,
                "source_api": r.source_api,
                "published_date": r.published_date,
                "raw_content": r.raw_content,
                "metadata": r.metadata,
            }
            for r in response.results
        ],
    }


def _deserialize_search_response(
    data: dict[str, Any], query: str, api_name: str
) -> SearchResponse:
    """Reconstruct a SearchResponse from cached data."""
    results = [
        SearchResult(
            title=r.get("title", ""),
            url=r.get("url", ""),
            snippet=r.get("snippet", ""),
            relevance_score=r.get("relevance_score", 0.0),
            source_api=r.get("source_api", api_name),
            published_date=r.get("published_date"),
            raw_content=r.get("raw_content"),
            metadata=r.get("metadata", {}),
        )
        for r in data.get("results", [])
    ]
    return SearchResponse(
        query=data.get("query", query),
        results=results,
        source_api=data.get("source_api", api_name),
        cached=True,
    )


def _serialize_scrape_result(result: ScrapeResult) -> dict[str, Any]:
    """Convert a ScrapeResult to a JSON-serializable dict."""
    return {
        "url": result.url,
        "markdown": result.markdown,
        "metadata": result.metadata,
        "source_api": result.source_api,
        "success": result.success,
        "error": result.error,
    }


def _deserialize_scrape_result(
    data: dict[str, Any], url: str, api_name: str
) -> ScrapeResult:
    """Reconstruct a ScrapeResult from cached data."""
    return ScrapeResult(
        url=data.get("url", url),
        markdown=data.get("markdown", ""),
        metadata=data.get("metadata", {}),
        source_api=data.get("source_api", api_name),
        success=data.get("success", True),
        error=data.get("error"),
    )
