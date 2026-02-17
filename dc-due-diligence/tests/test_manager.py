"""Tests for the WebResearchManager -- caching, rate limiting, and fallback."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research.cache import ResponseCache
from research.manager import (
    WebResearchManager,
    _serialize_search_response,
    _deserialize_search_response,
    _serialize_scrape_result,
    _deserialize_scrape_result,
)
from research.models import (
    ScrapeResult,
    SearchAPIError,
    SearchResponse,
    SearchResult,
)
from research.rate_limiter import RateLimiter, create_default_limiters


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------


def _make_search_response(query="test query", api="tavily", n_results=2):
    """Build a fake SearchResponse for testing."""
    results = [
        SearchResult(
            title=f"Result {i}",
            url=f"https://example.com/{i}",
            snippet=f"Snippet {i}",
            relevance_score=0.9 - i * 0.1,
            source_api=api,
        )
        for i in range(n_results)
    ]
    return SearchResponse(query=query, results=results, source_api=api)


def _make_scrape_result(url="https://example.com/page", api="firecrawl"):
    """Build a fake ScrapeResult for testing."""
    return ScrapeResult(
        url=url,
        markdown="# Page Title\n\nPage content here.",
        source_api=api,
        success=True,
    )


def _make_manager(search_clients=None, scrape_clients=None, cache=None):
    """Create a manager with mocked clients and a temp cache."""
    if cache is None:
        tmp = tempfile.mktemp(suffix=".db")
        cache = ResponseCache(db_path=tmp)

    limiters = {
        "tavily": RateLimiter("tavily", max_requests=100, period_seconds=3600, max_concurrent=3),
        "exa": RateLimiter("exa", max_requests=100, period_seconds=3600, max_concurrent=3),
        "firecrawl": RateLimiter("firecrawl", max_requests=100, period_seconds=3600, max_concurrent=2),
        "apify": RateLimiter("apify", max_requests=100, period_seconds=3600, max_concurrent=1),
    }

    manager = WebResearchManager(
        cache=cache,
        rate_limiters=limiters,
    )
    # Mark init as done and inject mock clients directly
    manager._init_done = True
    manager._search_clients = search_clients or {}
    manager._scrape_clients = scrape_clients or {}
    return manager


# ------------------------------------------------------------------
# Search tests
# ------------------------------------------------------------------


class TestSearch:
    def test_basic_search_returns_response(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(return_value=_make_search_response())

        manager = _make_manager(search_clients={"tavily": mock_tavily})

        async def run():
            response = await manager.search("data center Texas")
            assert isinstance(response, SearchResponse)
            assert response.success is True
            assert response.result_count == 2
            assert response.source_api == "tavily"

        asyncio.run(run())

    def test_search_uses_cache_on_second_call(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(return_value=_make_search_response())

        manager = _make_manager(search_clients={"tavily": mock_tavily})

        async def run():
            # First call hits the API
            r1 = await manager.search("data center Texas")
            # Second call should hit cache
            r2 = await manager.search("data center Texas")
            assert r2.cached is True
            # API should only be called once
            assert mock_tavily.search.call_count == 1

        asyncio.run(run())

    def test_search_falls_back_to_exa_on_tavily_failure(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(
            side_effect=SearchAPIError("tavily", "500 Internal Error", status_code=500, retryable=True)
        )
        mock_exa = MagicMock()
        mock_exa.search = AsyncMock(return_value=_make_search_response(api="exa"))

        manager = _make_manager(search_clients={"tavily": mock_tavily, "exa": mock_exa})

        async def run():
            response = await manager.search("test query")
            assert response.success is True
            assert response.source_api == "exa"

        asyncio.run(run())
        assert manager.stats().fallbacks_used == 1

    def test_search_preferred_api(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(return_value=_make_search_response(api="tavily"))
        mock_exa = MagicMock()
        mock_exa.search = AsyncMock(return_value=_make_search_response(api="exa"))

        manager = _make_manager(search_clients={"tavily": mock_tavily, "exa": mock_exa})

        async def run():
            response = await manager.search("test", preferred_api="exa")
            assert response.source_api == "exa"
            # Tavily should not have been called
            assert mock_tavily.search.call_count == 0

        asyncio.run(run())

    def test_search_all_apis_fail_returns_error_response(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(
            side_effect=SearchAPIError("tavily", "down", retryable=True)
        )
        mock_exa = MagicMock()
        mock_exa.search = AsyncMock(
            side_effect=SearchAPIError("exa", "also down", retryable=True)
        )

        manager = _make_manager(search_clients={"tavily": mock_tavily, "exa": mock_exa})

        async def run():
            response = await manager.search("hopeless query")
            assert response.success is False
            assert response.error is not None
            assert "tavily" in response.error
            assert "exa" in response.error

        asyncio.run(run())

    def test_search_no_clients_available(self):
        manager = _make_manager(search_clients={})

        async def run():
            response = await manager.search("no apis query")
            assert response.success is False
            assert "No search APIs available" in response.error

        asyncio.run(run())

    def test_search_increments_total_counter(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(return_value=_make_search_response())
        manager = _make_manager(search_clients={"tavily": mock_tavily})

        async def run():
            await manager.search("query 1")
            await manager.search("query 2")

        asyncio.run(run())
        assert manager.stats().total_searches == 2


# ------------------------------------------------------------------
# Scrape tests
# ------------------------------------------------------------------


class TestScrape:
    def test_basic_scrape_returns_result(self):
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape = AsyncMock(return_value=_make_scrape_result())

        manager = _make_manager(scrape_clients={"firecrawl": mock_firecrawl})

        async def run():
            result = await manager.scrape("https://example.com/page")
            assert isinstance(result, ScrapeResult)
            assert result.success is True
            assert result.source_api == "firecrawl"
            assert "Page content" in result.markdown

        asyncio.run(run())

    def test_scrape_uses_cache(self):
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape = AsyncMock(return_value=_make_scrape_result())

        manager = _make_manager(scrape_clients={"firecrawl": mock_firecrawl})

        async def run():
            await manager.scrape("https://example.com/page")
            r2 = await manager.scrape("https://example.com/page")
            assert mock_firecrawl.scrape.call_count == 1

        asyncio.run(run())

    def test_scrape_falls_back_on_failure(self):
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape = AsyncMock(
            side_effect=SearchAPIError("firecrawl", "timeout", retryable=True)
        )
        mock_apify = MagicMock()
        mock_apify.run_actor = AsyncMock(return_value=MagicMock(
            success=True,
            items=[{"text": "Scraped via Apify"}],
            actor_id="apify/web-scraper",
            run_id="run123",
            status="SUCCEEDED",
            error=None,
        ))

        manager = _make_manager(scrape_clients={"firecrawl": mock_firecrawl, "apify": mock_apify})

        async def run():
            result = await manager.scrape("https://example.com/tough-page")
            assert result.success is True
            assert result.source_api == "apify"

        asyncio.run(run())
        assert manager.stats().fallbacks_used == 1

    def test_scrape_all_fail_returns_error(self):
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape = AsyncMock(
            side_effect=SearchAPIError("firecrawl", "down", retryable=True)
        )

        manager = _make_manager(scrape_clients={"firecrawl": mock_firecrawl})

        async def run():
            result = await manager.scrape("https://broken.example.com")
            assert result.success is False
            assert result.error is not None
            assert "firecrawl" in result.error

        asyncio.run(run())

    def test_scrape_no_clients_available(self):
        manager = _make_manager(scrape_clients={})

        async def run():
            result = await manager.scrape("https://example.com")
            assert result.success is False
            assert "No scrape APIs available" in result.error

        asyncio.run(run())

    def test_scrape_unsuccessful_result_triggers_fallback(self):
        """When firecrawl returns success=False, the manager tries the next API."""
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape = AsyncMock(return_value=ScrapeResult(
            url="https://example.com",
            markdown="",
            source_api="firecrawl",
            success=False,
            error="Page blocked by firewall",
        ))
        mock_apify = MagicMock()
        mock_apify.run_actor = AsyncMock(return_value=MagicMock(
            success=True,
            items=[{"text": "Got it via Apify"}],
            actor_id="apify/web-scraper",
            run_id="run456",
            status="SUCCEEDED",
            error=None,
        ))

        manager = _make_manager(scrape_clients={"firecrawl": mock_firecrawl, "apify": mock_apify})

        async def run():
            result = await manager.scrape("https://example.com")
            assert result.success is True
            assert result.source_api == "apify"

        asyncio.run(run())


# ------------------------------------------------------------------
# Stats tests
# ------------------------------------------------------------------


class TestManagerStats:
    def test_stats_aggregates_all_subsystems(self):
        mock_tavily = MagicMock()
        mock_tavily.search = AsyncMock(return_value=_make_search_response())
        mock_firecrawl = MagicMock()
        mock_firecrawl.scrape = AsyncMock(return_value=_make_scrape_result())

        manager = _make_manager(
            search_clients={"tavily": mock_tavily},
            scrape_clients={"firecrawl": mock_firecrawl},
        )

        async def run():
            await manager.search("query 1")
            await manager.search("query 2")
            await manager.scrape("https://example.com")

        asyncio.run(run())

        stats = manager.stats()
        assert stats.total_searches == 2
        assert stats.total_scrapes == 1
        assert "tavily" in stats.rate_limiters
        assert stats.cache.stores >= 2  # at least 2 search + 1 scrape stored


# ------------------------------------------------------------------
# Serialization tests
# ------------------------------------------------------------------


class TestSerializationRoundtrip:
    def test_search_response_roundtrip(self):
        original = _make_search_response("roundtrip query", "tavily", 3)
        serialized = _serialize_search_response(original)
        deserialized = _deserialize_search_response(serialized, "roundtrip query", "tavily")

        assert deserialized.query == original.query
        assert deserialized.source_api == original.source_api
        assert deserialized.cached is True
        assert len(deserialized.results) == len(original.results)
        for orig, deser in zip(original.results, deserialized.results):
            assert deser.title == orig.title
            assert deser.url == orig.url
            assert deser.snippet == orig.snippet
            assert deser.relevance_score == orig.relevance_score

    def test_scrape_result_roundtrip(self):
        original = _make_scrape_result()
        serialized = _serialize_scrape_result(original)
        deserialized = _deserialize_scrape_result(serialized, original.url, "firecrawl")

        assert deserialized.url == original.url
        assert deserialized.markdown == original.markdown
        assert deserialized.source_api == original.source_api
        assert deserialized.success == original.success


# ------------------------------------------------------------------
# API order tests
# ------------------------------------------------------------------


class TestBuildApiOrder:
    def test_default_order_preserved(self):
        order = WebResearchManager._build_api_order(["a", "b", "c"], None)
        assert order == ["a", "b", "c"]

    def test_preferred_moved_to_front(self):
        order = WebResearchManager._build_api_order(["a", "b", "c"], "c")
        assert order == ["c", "a", "b"]

    def test_preferred_not_in_default_added_first(self):
        order = WebResearchManager._build_api_order(["a", "b"], "x")
        assert order == ["x", "a", "b"]
