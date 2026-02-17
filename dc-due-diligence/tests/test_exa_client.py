"""Tests for the Exa semantic search API wrapper."""

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research.models import SearchAPIError, SearchResponse, SearchResult
from research.exa_client import ExaSearchClient, _normalize_results


# ------------------------------------------------------------------
# Helpers for building mock Exa response objects
# ------------------------------------------------------------------


def _make_exa_result(
    url="https://example.com",
    id="abc123",
    title="Test Page",
    score=0.85,
    published_date=None,
    author=None,
    text=None,
    highlights=None,
    highlight_scores=None,
    summary=None,
):
    """Build an object that mimics an Exa Result dataclass."""
    return SimpleNamespace(
        url=url,
        id=id,
        title=title,
        score=score,
        published_date=published_date,
        author=author,
        text=text,
        highlights=highlights,
        highlight_scores=highlight_scores,
        summary=summary,
    )


def _make_exa_response(results, resolved_search_type="neural", auto_date=None):
    """Build an object that mimics an Exa SearchResponse."""
    return SimpleNamespace(
        results=results,
        resolved_search_type=resolved_search_type,
        auto_date=auto_date,
    )


# ------------------------------------------------------------------
# Normalization tests (no API call needed)
# ------------------------------------------------------------------


class TestNormalizeResults:
    def test_normalizes_standard_response(self):
        raw = _make_exa_response(
            results=[
                _make_exa_result(
                    title="Zoning Record",
                    url="https://county.gov/zoning/123",
                    score=0.91,
                    text="This parcel is zoned for industrial use.",
                ),
                _make_exa_result(
                    title="Property Listing",
                    url="https://realty.com/listing/456",
                    score=0.74,
                    text="50 acre parcel available in Mesquite TX.",
                ),
            ]
        )
        results = _normalize_results(raw)

        assert len(results) == 2
        assert all(isinstance(r, SearchResult) for r in results)

        assert results[0].title == "Zoning Record"
        assert results[0].url == "https://county.gov/zoning/123"
        assert results[0].source_api == "exa"
        assert results[0].relevance_score == 0.91

    def test_snippet_from_text(self):
        long_text = "A" * 1000
        raw = _make_exa_response(
            results=[_make_exa_result(text=long_text)]
        )
        results = _normalize_results(raw)

        # Snippet should be first 500 chars
        assert len(results[0].snippet) == 500
        # Full text goes to raw_content
        assert results[0].raw_content == long_text

    def test_short_text_no_raw_content(self):
        short_text = "Brief content."
        raw = _make_exa_response(
            results=[_make_exa_result(text=short_text)]
        )
        results = _normalize_results(raw)

        assert results[0].snippet == short_text
        # Short text should NOT be duplicated in raw_content
        assert results[0].raw_content is None

    def test_clamps_scores_to_valid_range(self):
        raw = _make_exa_response(
            results=[
                _make_exa_result(title="High", score=1.5),
                _make_exa_result(title="Low", score=-0.2),
            ]
        )
        results = _normalize_results(raw)
        assert results[0].relevance_score == 1.0
        assert results[1].relevance_score == 0.0

    def test_handles_none_fields(self):
        raw = _make_exa_response(
            results=[
                _make_exa_result(
                    title=None,
                    url=None,
                    score=None,
                    text=None,
                )
            ]
        )
        results = _normalize_results(raw)

        assert results[0].title == ""
        assert results[0].url == ""
        assert results[0].snippet == ""
        assert results[0].relevance_score == 0.0

    def test_empty_results(self):
        raw = _make_exa_response(results=[])
        results = _normalize_results(raw)
        assert results == []

    def test_preserves_published_date(self):
        raw = _make_exa_response(
            results=[
                _make_exa_result(published_date="2026-01-15T00:00:00Z")
            ]
        )
        results = _normalize_results(raw)
        assert results[0].published_date == "2026-01-15T00:00:00Z"

    def test_metadata_includes_author_and_highlights(self):
        raw = _make_exa_response(
            results=[
                _make_exa_result(
                    author="County Clerk",
                    highlights=["zoning approved", "industrial use"],
                    highlight_scores=[0.95, 0.88],
                    summary="Property is zoned industrial.",
                )
            ]
        )
        results = _normalize_results(raw)

        assert results[0].metadata["author"] == "County Clerk"
        assert results[0].metadata["highlights"] == [
            "zoning approved",
            "industrial use",
        ]
        assert results[0].metadata["highlight_scores"] == [0.95, 0.88]
        assert results[0].metadata["summary"] == "Property is zoned industrial."

    def test_metadata_omits_none_values(self):
        raw = _make_exa_response(
            results=[
                _make_exa_result(
                    author=None,
                    highlights=None,
                    highlight_scores=None,
                    summary=None,
                )
            ]
        )
        results = _normalize_results(raw)
        assert results[0].metadata == {}


# ------------------------------------------------------------------
# Client construction tests
# ------------------------------------------------------------------


class TestClientConstruction:
    def test_raises_without_api_key(self):
        env = os.environ.copy()
        env.pop("EXA_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SearchAPIError) as exc_info:
                ExaSearchClient()
            assert "EXA_API_KEY" in str(exc_info.value)

    @patch("research.exa_client.AsyncExa")
    def test_accepts_explicit_api_key(self, _mock_cls):
        client = ExaSearchClient(api_key="test-key-123")
        assert client._api_key == "test-key-123"

    @patch("research.exa_client.AsyncExa")
    def test_reads_api_key_from_env(self, _mock_cls):
        with patch.dict(os.environ, {"EXA_API_KEY": "env-key-456"}):
            client = ExaSearchClient()
            assert client._api_key == "env-key-456"


# ------------------------------------------------------------------
# Search method tests (mocked API)
# ------------------------------------------------------------------


def _make_client():
    """Create an ExaSearchClient with a mocked underlying SDK client."""
    with patch("research.exa_client.AsyncExa") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        client = ExaSearchClient(api_key="test-key")
    return client, mock_instance


class TestSearch:
    def test_basic_search(self):
        client, mock = _make_client()
        mock_response = _make_exa_response(
            results=[
                _make_exa_result(
                    title="Data Center Site",
                    url="https://example.com/site",
                    score=0.88,
                    text="A 100-acre data center campus.",
                )
            ]
        )
        mock.search = AsyncMock(return_value=mock_response)

        response = asyncio.run(client.search("data center site Texas"))

        assert isinstance(response, SearchResponse)
        assert response.success is True
        assert response.source_api == "exa"
        assert response.query == "data center site Texas"
        assert len(response.results) == 1
        assert response.results[0].title == "Data Center Site"

    def test_search_passes_parameters(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            return_value=_make_exa_response(results=[])
        )

        asyncio.run(
            client.search(
                "test query",
                num_results=5,
                search_type="neural",
                include_domains=["county.gov"],
                exclude_domains=["spam.com"],
                start_published_date="2025-01-01",
                end_published_date="2026-01-01",
                category="news",
            )
        )

        call_kwargs = mock.search.call_args[1]
        assert call_kwargs["query"] == "test query"
        assert call_kwargs["num_results"] == 5
        assert call_kwargs["type"] == "neural"
        assert call_kwargs["include_domains"] == ["county.gov"]
        assert call_kwargs["exclude_domains"] == ["spam.com"]
        assert call_kwargs["start_published_date"] == "2025-01-01"
        assert call_kwargs["end_published_date"] == "2026-01-01"
        assert call_kwargs["category"] == "news"

    def test_search_with_contents_disabled(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            return_value=_make_exa_response(results=[])
        )

        asyncio.run(client.search("query", include_contents=False))

        call_kwargs = mock.search.call_args[1]
        assert call_kwargs["contents"] is False

    def test_search_api_error_wraps_exception(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            side_effect=Exception("Network error")
        )

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.search("failing query"))

        assert exc_info.value.api_name == "exa"
        assert "Network error" in str(exc_info.value)

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

    def test_search_empty_results_still_returns_response(self):
        client, mock = _make_client()
        mock.search = AsyncMock(
            return_value=_make_exa_response(results=[])
        )

        response = asyncio.run(client.search("obscure query"))

        assert isinstance(response, SearchResponse)
        assert response.result_count == 0
        assert response.success is False


# ------------------------------------------------------------------
# Live integration test (skipped without API key)
# ------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("EXA_API_KEY"),
    reason="EXA_API_KEY not set -- skipping live API test",
)
class TestExaLive:
    def test_live_search_returns_results(self):
        client = ExaSearchClient()
        response = asyncio.run(
            client.search(
                "data center development Texas",
                num_results=3,
                include_contents=True,
            )
        )

        assert isinstance(response, SearchResponse)
        assert response.source_api == "exa"
        assert response.result_count > 0

        for result in response.results:
            assert isinstance(result, SearchResult)
            assert result.title
            assert result.url
            assert 0.0 <= result.relevance_score <= 1.0
