"""
Exa API wrapper for semantic / AI-native web search.

Exa excels at finding specific documents and understanding natural-language
queries.  It is better than general search engines for research-oriented
retrieval such as finding government records, permit databases, property
listings, and technical reports.

Usage::

    client = ExaSearchClient()             # reads EXA_API_KEY from env
    response = await client.search(
        "Pioneer Park data center zoning approval Mesquite TX"
    )
    for result in response.results:
        print(result.title, result.snippet)
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Literal

from exa_py import AsyncExa
from exa_py.api import ContentsOptions, TextContentsOptions

from research.models import SearchAPIError, SearchResponse, SearchResult

logger = logging.getLogger(__name__)


class ExaSearchClient:
    """Async wrapper around the Exa semantic search API.

    Reads the API key from the ``EXA_API_KEY`` environment variable
    unless one is passed explicitly.
    """

    API_NAME = "exa"

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("EXA_API_KEY", "")
        if not self._api_key:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=(
                    "No API key found. Set the EXA_API_KEY environment "
                    "variable or pass api_key to ExaSearchClient()."
                ),
            )

        self._client = AsyncExa(api_key=self._api_key)

    async def search(
        self,
        query: str,
        *,
        num_results: int = 10,
        search_type: Literal["auto", "fast", "deep", "neural"] = "auto",
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        start_published_date: str | None = None,
        end_published_date: str | None = None,
        include_text: list[str] | None = None,
        exclude_text: list[str] | None = None,
        category: str | None = None,
        include_contents: bool = True,
        max_content_chars: int = 10_000,
        timeout: float = 30.0,
    ) -> SearchResponse:
        """Run a semantic search query against the Exa API.

        Args:
            query: Natural-language search query.
            num_results: Maximum results to return (1-30).
            search_type: Search mode -- ``"auto"`` lets Exa decide,
                ``"neural"`` uses embedding-based search,
                ``"deep"`` uses LLM-expanded queries.
            include_domains: Only return results from these domains.
            exclude_domains: Never return results from these domains.
            start_published_date: ISO-8601 date string -- only include
                pages published on or after this date.
            end_published_date: ISO-8601 date string -- only include
                pages published on or before this date.
            include_text: Strings that must appear in the result text.
            exclude_text: Strings that must not appear in the result text.
            category: Content category filter (e.g. ``"company"``,
                ``"news"``, ``"research paper"``).
            include_contents: Whether to fetch page text content.
            max_content_chars: Max characters of page text to return per
                result.
            timeout: Maximum seconds to wait for the API response.

        Returns:
            A ``SearchResponse`` with normalized ``SearchResult`` items.

        Raises:
            SearchAPIError: On authentication failure, rate limiting, or
                other API errors.
        """
        kwargs: dict = {
            "query": query,
            "num_results": num_results,
            "type": search_type,
        }

        if include_contents:
            kwargs["contents"] = ContentsOptions(
                text=TextContentsOptions(max_characters=max_content_chars),
            )
        else:
            kwargs["contents"] = False

        if include_domains:
            kwargs["include_domains"] = include_domains
        if exclude_domains:
            kwargs["exclude_domains"] = exclude_domains
        if start_published_date:
            kwargs["start_published_date"] = start_published_date
        if end_published_date:
            kwargs["end_published_date"] = end_published_date
        if include_text:
            kwargs["include_text"] = include_text
        if exclude_text:
            kwargs["exclude_text"] = exclude_text
        if category:
            kwargs["category"] = category

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
                logger.warning("Exa rate limit hit for query: %s", query)

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


def _normalize_results(raw) -> list[SearchResult]:
    """Convert an Exa ``SearchResponse`` object into normalized SearchResult list."""
    normalized: list[SearchResult] = []

    for item in raw.results:
        score = getattr(item, "score", None) or 0.0
        # Exa scores can exceed 1.0; clamp to 0-1 range for consistency.
        clamped_score = max(0.0, min(1.0, float(score)))

        text = getattr(item, "text", None) or ""
        # Use the first 500 characters of text as snippet if available.
        snippet = text[:500] if text else ""

        published = getattr(item, "published_date", None)

        metadata: dict = {}
        if getattr(item, "author", None):
            metadata["author"] = item.author
        if getattr(item, "highlights", None):
            metadata["highlights"] = item.highlights
        if getattr(item, "highlight_scores", None):
            metadata["highlight_scores"] = item.highlight_scores
        if getattr(item, "summary", None):
            metadata["summary"] = item.summary

        normalized.append(
            SearchResult(
                title=getattr(item, "title", None) or "",
                url=getattr(item, "url", "") or "",
                snippet=snippet,
                relevance_score=clamped_score,
                source_api="exa",
                published_date=published,
                raw_content=text if len(text) > 500 else None,
                metadata=metadata,
            )
        )

    return normalized


def _extract_status_code(exc: Exception) -> int | None:
    """Try to pull an HTTP status code out of an exception.

    The Exa SDK may wrap HTTP errors in its own exception types or
    raise ``httpx`` / ``httpcore`` exceptions directly.
    """
    if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        return int(exc.response.status_code)
    if hasattr(exc, "status_code"):
        return int(exc.status_code)

    exc_str = str(exc)
    for code in (401, 403, 429, 500, 502, 503, 504):
        if str(code) in exc_str:
            return code

    return None
