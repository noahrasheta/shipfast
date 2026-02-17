"""
Tavily API wrapper for general web search.

Tavily provides fast, general-purpose web search suitable for broad
information gathering -- market data, news, company information, and
public records.  This wrapper handles authentication, query execution,
and normalization of results into the common ``SearchResult`` format.

Usage::

    client = TavilySearchClient()          # reads TAVILY_API_KEY from env
    response = await client.search("data center power capacity Texas")
    for result in response.results:
        print(result.title, result.url)
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Literal, Sequence

from tavily import AsyncTavilyClient

from research.models import SearchAPIError, SearchResponse, SearchResult

logger = logging.getLogger(__name__)


class TavilySearchClient:
    """Async wrapper around the Tavily search API.

    Reads the API key from the ``TAVILY_API_KEY`` environment variable
    unless one is passed explicitly.
    """

    API_NAME = "tavily"

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("TAVILY_API_KEY", "")
        if not self._api_key:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=(
                    "No API key found. Set the TAVILY_API_KEY environment "
                    "variable or pass api_key to TavilySearchClient()."
                ),
            )

        self._client = AsyncTavilyClient(api_key=self._api_key)

    async def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: Literal["general", "news", "finance"] = "general",
        include_domains: Sequence[str] | None = None,
        exclude_domains: Sequence[str] | None = None,
        time_range: Literal["day", "week", "month", "year"] | None = None,
        include_raw_content: bool = False,
        timeout: float = 30.0,
    ) -> SearchResponse:
        """Run a search query against the Tavily API.

        Args:
            query: Natural-language search query.
            max_results: Maximum number of results to return (1-20).
            search_depth: ``"basic"`` for fast results, ``"advanced"`` for
                deeper crawling.
            topic: Search topic category.
            include_domains: Only return results from these domains.
            exclude_domains: Never return results from these domains.
            time_range: Filter results by recency.
            include_raw_content: If True, request full page content in
                markdown format.
            timeout: Maximum seconds to wait for the API response.

        Returns:
            A ``SearchResponse`` containing normalized ``SearchResult`` items.

        Raises:
            SearchAPIError: On authentication failure, rate limiting (429),
                or other API errors.
        """
        kwargs: dict = {
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "topic": topic,
            "timeout": timeout,
        }
        if include_domains:
            kwargs["include_domains"] = list(include_domains)
        if exclude_domains:
            kwargs["exclude_domains"] = list(exclude_domains)
        if time_range:
            kwargs["time_range"] = time_range
        if include_raw_content:
            kwargs["include_raw_content"] = "markdown"

        try:
            raw = await asyncio.wait_for(
                self._client.search(**kwargs),
                timeout=timeout + 5.0,
            )
        except asyncio.TimeoutError:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=f"Request timed out after {timeout}s for query: {query}",
                retryable=True,
            )
        except Exception as exc:
            status_code = _extract_status_code(exc)
            retryable = status_code in (429, 500, 502, 503, 504) if status_code else False

            if status_code == 429:
                logger.warning("Tavily rate limit hit for query: %s", query)

            raise SearchAPIError(
                api_name=self.API_NAME,
                message=str(exc),
                status_code=status_code,
                retryable=retryable,
            ) from exc

        results = _normalize_results(raw)
        return SearchResponse(
            query=query,
            results=results,
            source_api=self.API_NAME,
        )


def _normalize_results(raw: dict) -> list[SearchResult]:
    """Convert raw Tavily API response dict into normalized SearchResult list."""
    items: list[dict] = raw.get("results", [])
    normalized: list[SearchResult] = []

    for item in items:
        score = item.get("score", 0.0)
        # Tavily scores are already in ~0-1 range.
        clamped_score = max(0.0, min(1.0, float(score)))

        normalized.append(
            SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                relevance_score=clamped_score,
                source_api="tavily",
                raw_content=item.get("raw_content"),
                metadata={
                    k: v
                    for k, v in item.items()
                    if k not in ("title", "url", "content", "score", "raw_content")
                },
            )
        )

    return normalized


def _extract_status_code(exc: Exception) -> int | None:
    """Try to pull an HTTP status code out of an exception.

    The Tavily SDK may wrap HTTP errors in its own exception types.
    We check common attribute names used by ``httpx`` and ``requests``.
    """
    # httpx.HTTPStatusError
    if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        return int(exc.response.status_code)
    # requests.HTTPError
    if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        return int(exc.response.status_code)
    # Generic attribute
    if hasattr(exc, "status_code"):
        return int(exc.status_code)

    # Check the string representation for common HTTP codes
    exc_str = str(exc)
    for code in (401, 403, 429, 500, 502, 503, 504):
        if str(code) in exc_str:
            return code

    return None
