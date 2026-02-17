"""Tests for the shared web research data models."""

from datetime import datetime, timezone

from research.models import SearchAPIError, SearchResponse, SearchResult


class TestSearchResult:
    def test_basic_construction(self):
        result = SearchResult(
            title="Test Page",
            url="https://example.com",
            snippet="A short description.",
            relevance_score=0.85,
            source_api="tavily",
        )
        assert result.title == "Test Page"
        assert result.url == "https://example.com"
        assert result.snippet == "A short description."
        assert result.relevance_score == 0.85
        assert result.source_api == "tavily"
        assert result.published_date is None
        assert result.raw_content is None
        assert result.metadata == {}

    def test_with_optional_fields(self):
        result = SearchResult(
            title="News Article",
            url="https://news.example.com/article",
            snippet="Breaking news content.",
            relevance_score=0.92,
            source_api="exa",
            published_date="2026-01-15",
            raw_content="Full article text here...",
            metadata={"author": "Jane Doe"},
        )
        assert result.published_date == "2026-01-15"
        assert result.raw_content == "Full article text here..."
        assert result.metadata["author"] == "Jane Doe"


class TestSearchResponse:
    def test_successful_response(self):
        results = [
            SearchResult(
                title="Page 1",
                url="https://example.com/1",
                snippet="First result.",
                relevance_score=0.9,
                source_api="tavily",
            ),
            SearchResult(
                title="Page 2",
                url="https://example.com/2",
                snippet="Second result.",
                relevance_score=0.7,
                source_api="tavily",
            ),
        ]
        response = SearchResponse(
            query="test query",
            results=results,
            source_api="tavily",
        )
        assert response.success is True
        assert response.result_count == 2
        assert response.error is None
        assert response.cached is False
        assert isinstance(response.retrieved_at, datetime)

    def test_empty_results_not_success(self):
        response = SearchResponse(
            query="no results query",
            results=[],
            source_api="exa",
        )
        assert response.success is False
        assert response.result_count == 0

    def test_error_response(self):
        response = SearchResponse(
            query="bad query",
            results=[],
            source_api="tavily",
            error="Rate limit exceeded",
        )
        assert response.success is False
        assert response.error == "Rate limit exceeded"

    def test_cached_flag(self):
        response = SearchResponse(
            query="cached query",
            results=[
                SearchResult(
                    title="Cached",
                    url="https://example.com",
                    snippet="From cache.",
                    relevance_score=0.8,
                    source_api="tavily",
                )
            ],
            source_api="tavily",
            cached=True,
        )
        assert response.cached is True
        assert response.success is True


class TestSearchAPIError:
    def test_basic_error(self):
        err = SearchAPIError(
            api_name="tavily",
            message="Unauthorized",
            status_code=401,
        )
        assert err.api_name == "tavily"
        assert err.status_code == 401
        assert err.retryable is False
        assert "tavily" in str(err)
        assert "401" in str(err)
        assert "Unauthorized" in str(err)

    def test_retryable_error(self):
        err = SearchAPIError(
            api_name="exa",
            message="Too many requests",
            status_code=429,
            retryable=True,
        )
        assert err.retryable is True

    def test_error_without_status_code(self):
        err = SearchAPIError(
            api_name="tavily",
            message="Connection refused",
        )
        assert err.status_code is None
        assert "None" in str(err)

    def test_is_exception(self):
        err = SearchAPIError(api_name="exa", message="fail")
        assert isinstance(err, Exception)
