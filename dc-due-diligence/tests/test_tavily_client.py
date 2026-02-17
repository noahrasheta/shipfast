"""Tests for the Tavily search API wrapper."""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research.models import SearchAPIError, SearchResponse, SearchResult
from research.tavily_client import TavilySearchClient, _normalize_results


# ------------------------------------------------------------------
# Normalization tests (no API call needed)
# ------------------------------------------------------------------


class TestNormalizeResults:
    def test_normalizes_standard_response(self):
        raw = {
            "results": [
                {
                    "title": "Data Center in Dallas",
                    "url": "https://example.com/dc-dallas",
                    "content": "A 50MW data center facility in Dallas.",
                    "score": 0.92,
                },
                {
                    "title": "Texas Power Grid",
                    "url": "https://example.com/ercot",
                    "content": "ERCOT manages the Texas power grid.",
                    "score": 0.78,
                },
            ]
        }
        results = _normalize_results(raw)

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)

        assert results[0].title == "Data Center in Dallas"
        assert results[0].url == "https://example.com/dc-dallas"
        assert results[0].snippet == "A 50MW data center facility in Dallas."
        assert results[0].relevance_score == 0.92
        assert results[0].source_api == "tavily"

    def test_clamps_scores_to_valid_range(self):
        raw = {
            "results": [
                {"title": "High", "url": "", "content": "", "score": 1.5},
                {"title": "Low", "url": "", "content": "", "score": -0.3},
            ]
        }
        results = _normalize_results(raw)
        assert results[0].relevance_score == 1.0
        assert results[1].relevance_score == 0.0

    def test_handles_missing_fields(self):
        raw = {"results": [{}]}
        results = _normalize_results(raw)

        assert len(results) == 1
        assert results[0].title == ""
        assert results[0].url == ""
        assert results[0].snippet == ""
        assert results[0].relevance_score == 0.0

    def test_empty_results_list(self):
        raw = {"results": []}
        results = _normalize_results(raw)
        assert results == []

    def test_missing_results_key(self):
        raw = {}
        results = _normalize_results(raw)
        assert results == []

    def test_preserves_raw_content(self):
        raw = {
            "results": [
                {
                    "title": "Page",
                    "url": "https://example.com",
                    "content": "snippet",
                    "score": 0.5,
                    "raw_content": "Full page markdown content...",
                }
            ]
        }
        results = _normalize_results(raw)
        assert results[0].raw_content == "Full page markdown content..."

    def test_extra_fields_go_to_metadata(self):
        raw = {
            "results": [
                {
                    "title": "Page",
                    "url": "https://example.com",
                    "content": "snippet",
                    "score": 0.5,
                    "published_date": "2026-01-01",
                    "favicon": "https://example.com/icon.png",
                }
            ]
        }
        results = _normalize_results(raw)
        assert "published_date" in results[0].metadata
        assert "favicon" in results[0].metadata
        # These fields should NOT be in metadata (they're in top-level fields):
        assert "title" not in results[0].metadata
        assert "url" not in results[0].metadata
        assert "content" not in results[0].metadata
        assert "score" not in results[0].metadata


# ------------------------------------------------------------------
# Client construction tests
# ------------------------------------------------------------------


class TestClientConstruction:
    def test_raises_without_api_key(self):
        env = os.environ.copy()
        env.pop("TAVILY_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SearchAPIError) as exc_info:
                TavilySearchClient()
            assert "TAVILY_API_KEY" in str(exc_info.value)

    @patch("research.tavily_client.AsyncTavilyClient")
    def test_accepts_explicit_api_key(self, _mock_cls):
        client = TavilySearchClient(api_key="test-key-123")
        assert client._api_key == "test-key-123"

    @patch("research.tavily_client.AsyncTavilyClient")
    def test_reads_api_key_from_env(self, _mock_cls):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "env-key-456"}):
            client = TavilySearchClient()
            assert client._api_key == "env-key-456"


# ------------------------------------------------------------------
# Search method tests (mocked API)
# ------------------------------------------------------------------


def _make_client():
    """Create a TavilySearchClient with a mocked underlying SDK client."""
    with patch("research.tavily_client.AsyncTavilyClient") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        client = TavilySearchClient(api_key="test-key")
    return client, mock_instance


class TestSearch:
    def test_basic_search(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            return_value={
                "results": [
                    {
                        "title": "Result One",
                        "url": "https://example.com/1",
                        "content": "First result snippet.",
                        "score": 0.95,
                    }
                ]
            }
        )

        response = asyncio.run(client.search("data center Texas"))

        assert isinstance(response, SearchResponse)
        assert response.success is True
        assert response.source_api == "tavily"
        assert response.query == "data center Texas"
        assert len(response.results) == 1
        assert response.results[0].title == "Result One"

    def test_search_passes_parameters(self):
        client, mock = _make_client()
        mock.search = AsyncMock(return_value={"results": []})

        asyncio.run(
            client.search(
                "test query",
                max_results=10,
                search_depth="advanced",
                topic="news",
                include_domains=["example.com"],
                exclude_domains=["bad.com"],
                time_range="week",
            )
        )

        call_kwargs = mock.search.call_args[1]
        assert call_kwargs["query"] == "test query"
        assert call_kwargs["max_results"] == 10
        assert call_kwargs["search_depth"] == "advanced"
        assert call_kwargs["topic"] == "news"
        assert call_kwargs["include_domains"] == ["example.com"]
        assert call_kwargs["exclude_domains"] == ["bad.com"]
        assert call_kwargs["time_range"] == "week"

    def test_search_api_error_wraps_exception(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            side_effect=Exception("Connection refused")
        )

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.search("failing query"))

        assert exc_info.value.api_name == "tavily"
        assert "Connection refused" in str(exc_info.value)

    def test_search_rate_limit_marked_retryable(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            side_effect=Exception("429 Too Many Requests")
        )

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.search("rate limited query"))

        assert exc_info.value.status_code == 429
        assert exc_info.value.retryable is True

    def test_search_timeout_marked_retryable(self):
        client, mock = _make_client()

        async def slow_search(**kwargs):
            await asyncio.sleep(100)

        mock.search = slow_search

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.search("slow query", timeout=0.1))

        assert exc_info.value.retryable is True
        assert "timed out" in str(exc_info.value)

    def test_search_raw_content_flag(self):
        client, mock = _make_client()
        mock.search = AsyncMock(return_value={"results": []})

        asyncio.run(client.search("query", include_raw_content=True))

        call_kwargs = mock.search.call_args[1]
        assert call_kwargs["include_raw_content"] == "markdown"

    def test_search_empty_results_still_returns_response(self):
        client, mock = _make_client()
        mock.search = AsyncMock(return_value={"results": []})

        response = asyncio.run(client.search("obscure query"))

        assert isinstance(response, SearchResponse)
        assert response.result_count == 0
        assert response.success is False  # no results = not success


# ------------------------------------------------------------------
# Live integration test (skipped without API key)
# ------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("TAVILY_API_KEY"),
    reason="TAVILY_API_KEY not set -- skipping live API test",
)
class TestTavilyLive:
    def test_live_search_returns_results(self):
        client = TavilySearchClient()
        response = asyncio.run(
            client.search("data center development Texas", max_results=3)
        )

        assert isinstance(response, SearchResponse)
        assert response.source_api == "tavily"
        assert response.result_count > 0

        for result in response.results:
            assert isinstance(result, SearchResult)
            assert result.title
            assert result.url
            assert 0.0 <= result.relevance_score <= 1.0
