"""
Shared data models for web research results.

All API wrappers normalize their responses into these common types so
downstream agents receive a consistent structure regardless of which
search API produced the data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class SearchResult:
    """A single search result returned by any search API.

    Attributes:
        title: Title of the search result page.
        url: URL of the search result.
        snippet: Short text excerpt or description from the result.
        relevance_score: Relevance score (0.0 to 1.0) as reported by the API.
            Different APIs use different scoring schemes; values are
            normalized to this range where possible.
        source_api: Name of the API that produced this result
            (e.g. "tavily", "exa").
        published_date: Publication date if available, None otherwise.
        raw_content: Full page content when requested and available.
        metadata: Additional API-specific data that doesn't fit the
            common schema.
    """

    title: str
    url: str
    snippet: str
    relevance_score: float
    source_api: str
    published_date: str | None = None
    raw_content: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResponse:
    """Aggregated response from a search query.

    Attributes:
        query: The original search query string.
        results: List of normalized search results.
        source_api: Name of the API that produced these results.
        cached: True if the response was served from cache.
        retrieved_at: UTC timestamp of when the response was obtained.
        error: Error message if the search partially or fully failed.
    """

    query: str
    results: list[SearchResult]
    source_api: str
    cached: bool = False
    retrieved_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    error: str | None = None

    @property
    def success(self) -> bool:
        """True when the search returned at least one result with no error."""
        return self.error is None and len(self.results) > 0

    @property
    def result_count(self) -> int:
        return len(self.results)


@dataclass
class ScrapeResult:
    """A single web-scrape result returned by a scraping API.

    Attributes:
        url: The URL that was scraped.
        markdown: Page content converted to markdown.
        metadata: Additional page metadata (title, description, status code,
            language, Open Graph fields, etc.).
        source_api: Name of the API that produced this result
            (e.g. "firecrawl", "apify").
        success: True if the scrape completed without errors.
        error: Error message if the scrape failed or partially failed.
    """

    url: str
    markdown: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_api: str = ""
    success: bool = True
    error: str | None = None


@dataclass
class ActorRunResult:
    """Result from an Apify actor run.

    Attributes:
        actor_id: The Apify actor that was executed.
        run_id: Unique identifier for this run.
        status: Final run status (e.g. "SUCCEEDED", "FAILED", "TIMED-OUT").
        items: List of result items from the actor's default dataset.
        source_api: Always "apify".
        dataset_id: ID of the default dataset for this run.
        error: Error message if the run failed.
    """

    actor_id: str
    run_id: str
    status: str
    items: list[dict[str, Any]] = field(default_factory=list)
    source_api: str = "apify"
    dataset_id: str | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        """True when the actor run finished successfully."""
        return self.status == "SUCCEEDED"

    @property
    def item_count(self) -> int:
        return len(self.items)


class SearchAPIError(Exception):
    """Raised when a search API call fails.

    Attributes:
        api_name: Which API failed (e.g. "tavily", "exa").
        status_code: HTTP status code if available.
        message: Human-readable error description.
        retryable: Whether the caller should retry the request.
    """

    def __init__(
        self,
        api_name: str,
        message: str,
        status_code: int | None = None,
        retryable: bool = False,
    ):
        self.api_name = api_name
        self.status_code = status_code
        self.retryable = retryable
        super().__init__(f"{api_name} error ({status_code}): {message}")
