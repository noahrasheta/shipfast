"""Tests for the Firecrawl web scraping API wrapper."""

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research.models import ScrapeResult, SearchAPIError
from research.firecrawl_client import FirecrawlScrapeClient, _normalize_document


# ------------------------------------------------------------------
# Helpers for building mock Firecrawl Document objects
# ------------------------------------------------------------------


def _make_document(
    markdown="# Page Title\n\nSome content here.",
    html=None,
    metadata=None,
    warning=None,
):
    """Build an object that mimics a Firecrawl Document."""
    if metadata is None:
        metadata = SimpleNamespace(
            title="Page Title",
            description="A page description.",
            url="https://example.com",
            status_code=200,
            language="en",
            error=None,
        )
        metadata.model_dump = lambda: {
            "title": "Page Title",
            "description": "A page description.",
            "url": "https://example.com",
            "status_code": 200,
            "language": "en",
            "error": None,
        }
    return SimpleNamespace(
        markdown=markdown,
        html=html,
        metadata=metadata,
        warning=warning,
    )


# ------------------------------------------------------------------
# Normalization tests (no API call needed)
# ------------------------------------------------------------------


class TestNormalizeDocument:
    def test_normalizes_standard_document(self):
        doc = _make_document()
        result = _normalize_document("https://example.com", doc)

        assert isinstance(result, ScrapeResult)
        assert result.url == "https://example.com"
        assert result.markdown == "# Page Title\n\nSome content here."
        assert result.source_api == "firecrawl"
        assert result.success is True
        assert result.error is None

    def test_extracts_metadata(self):
        doc = _make_document()
        result = _normalize_document("https://example.com", doc)

        assert result.metadata["title"] == "Page Title"
        assert result.metadata["description"] == "A page description."
        assert result.metadata["status_code"] == 200

    def test_excludes_none_metadata_values(self):
        doc = _make_document()
        result = _normalize_document("https://example.com", doc)

        # language is "en" so it should be present
        assert "language" in result.metadata
        # error was None so should be excluded
        assert "error" not in result.metadata

    def test_handles_empty_markdown(self):
        doc = _make_document(markdown="")
        result = _normalize_document("https://example.com", doc)

        assert result.markdown == ""
        assert result.success is False

    def test_handles_none_markdown(self):
        doc = _make_document(markdown=None)
        result = _normalize_document("https://example.com", doc)

        assert result.markdown == ""
        assert result.success is False

    def test_handles_warning(self):
        doc = _make_document(warning="Page loaded slowly")
        result = _normalize_document("https://example.com", doc)

        assert result.success is False
        assert result.error == "Page loaded slowly"

    def test_handles_error_in_metadata(self):
        metadata = SimpleNamespace(
            title="Error Page",
            error="403 Forbidden",
        )
        metadata.model_dump = lambda: {
            "title": "Error Page",
            "error": "403 Forbidden",
        }
        doc = _make_document(metadata=metadata)
        result = _normalize_document("https://example.com", doc)

        assert result.success is False
        assert result.error == "403 Forbidden"
        # error should not be in metadata dict
        assert "error" not in result.metadata

    def test_handles_dict_metadata(self):
        metadata = {
            "title": "Dict Metadata",
            "status_code": 200,
            "language": None,
        }
        doc = SimpleNamespace(
            markdown="Content here.",
            metadata=metadata,
            warning=None,
        )
        result = _normalize_document("https://example.com", doc)

        assert result.metadata["title"] == "Dict Metadata"
        assert result.metadata["status_code"] == 200
        assert "language" not in result.metadata  # None excluded

    def test_handles_no_metadata(self):
        doc = SimpleNamespace(
            markdown="Content.",
            metadata=None,
            warning=None,
        )
        result = _normalize_document("https://example.com", doc)

        assert result.metadata == {}
        assert result.success is True


# ------------------------------------------------------------------
# Client construction tests
# ------------------------------------------------------------------


class TestClientConstruction:
    def test_raises_without_api_key(self):
        env = os.environ.copy()
        env.pop("FIRECRAWL_API_KEY", None)
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SearchAPIError) as exc_info:
                FirecrawlScrapeClient()
            assert "FIRECRAWL_API_KEY" in str(exc_info.value)

    @patch("research.firecrawl_client.AsyncFirecrawl")
    def test_accepts_explicit_api_key(self, _mock_cls):
        client = FirecrawlScrapeClient(api_key="test-key-123")
        assert client._api_key == "test-key-123"

    @patch("research.firecrawl_client.AsyncFirecrawl")
    def test_reads_api_key_from_env(self, _mock_cls):
        with patch.dict(os.environ, {"FIRECRAWL_API_KEY": "env-key-456"}):
            client = FirecrawlScrapeClient()
            assert client._api_key == "env-key-456"


# ------------------------------------------------------------------
# Scrape method tests (mocked API)
# ------------------------------------------------------------------


def _make_client():
    """Create a FirecrawlScrapeClient with a mocked underlying SDK client."""
    with patch("research.firecrawl_client.AsyncFirecrawl") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        client = FirecrawlScrapeClient(api_key="test-key")
    return client, mock_instance


class TestScrape:
    def test_basic_scrape(self):
        client, mock = _make_client()
        doc = _make_document()
        mock.scrape = AsyncMock(return_value=doc)

        result = asyncio.run(client.scrape("https://example.com"))

        assert isinstance(result, ScrapeResult)
        assert result.success is True
        assert result.source_api == "firecrawl"
        assert result.url == "https://example.com"
        assert "Page Title" in result.markdown

    def test_scrape_passes_only_main_content(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(return_value=_make_document())

        asyncio.run(client.scrape("https://example.com", only_main_content=True))

        call_kwargs = mock.scrape.call_args[1]
        assert call_kwargs["only_main_content"] is True

    def test_scrape_passes_formats(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(return_value=_make_document())

        asyncio.run(client.scrape("https://example.com"))

        call_kwargs = mock.scrape.call_args[1]
        assert "markdown" in call_kwargs["formats"]

    def test_scrape_passes_wait_for(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(return_value=_make_document())

        asyncio.run(client.scrape("https://example.com", wait_for=3000))

        call_kwargs = mock.scrape.call_args[1]
        assert call_kwargs["wait_for"] == 3000

    def test_scrape_passes_tag_filters(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(return_value=_make_document())

        asyncio.run(
            client.scrape(
                "https://example.com",
                include_tags=["main", "article"],
                exclude_tags=["nav", "footer"],
            )
        )

        call_kwargs = mock.scrape.call_args[1]
        assert call_kwargs["include_tags"] == ["main", "article"]
        assert call_kwargs["exclude_tags"] == ["nav", "footer"]

    def test_scrape_api_error_wraps_exception(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(side_effect=Exception("Connection refused"))

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.scrape("https://example.com"))

        assert exc_info.value.api_name == "firecrawl"
        assert "Connection refused" in str(exc_info.value)

    def test_scrape_rate_limit_marked_retryable(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(
            side_effect=Exception("429 Too Many Requests")
        )

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.scrape("https://example.com"))

        assert exc_info.value.status_code == 429
        assert exc_info.value.retryable is True

    def test_scrape_timeout_marked_retryable(self):
        client, mock = _make_client()

        async def slow_scrape(url, **kwargs):
            await asyncio.sleep(100)

        mock.scrape = slow_scrape

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.scrape("https://example.com", timeout=0.1))

        assert exc_info.value.retryable is True
        assert "timed out" in str(exc_info.value)

    def test_scrape_value_error_maps_to_401(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(
            side_effect=ValueError("API key is required")
        )

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(client.scrape("https://example.com"))

        assert exc_info.value.status_code == 401
        assert exc_info.value.retryable is False


class TestScrapeMainContent:
    def test_convenience_method_calls_scrape(self):
        client, mock = _make_client()
        mock.scrape = AsyncMock(return_value=_make_document())

        result = asyncio.run(
            client.scrape_main_content("https://county.gov/assessor")
        )

        assert isinstance(result, ScrapeResult)
        call_kwargs = mock.scrape.call_args[1]
        assert call_kwargs["only_main_content"] is True


# ------------------------------------------------------------------
# Live integration test (skipped without API key)
# ------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("FIRECRAWL_API_KEY"),
    reason="FIRECRAWL_API_KEY not set -- skipping live API test",
)
class TestFirecrawlLive:
    def test_live_scrape_returns_markdown(self):
        client = FirecrawlScrapeClient()
        result = asyncio.run(
            client.scrape("https://example.com", only_main_content=True)
        )

        assert isinstance(result, ScrapeResult)
        assert result.source_api == "firecrawl"
        assert result.success is True
        assert len(result.markdown) > 0
        assert result.url == "https://example.com"
