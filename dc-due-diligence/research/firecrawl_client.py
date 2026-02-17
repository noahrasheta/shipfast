"""
Firecrawl API wrapper for JavaScript-heavy web scraping.

Firecrawl renders pages in a headless browser and returns clean markdown,
making it ideal for scraping county assessor sites, government portals,
and other JavaScript-heavy pages that simple HTTP requests cannot handle.

Usage::

    client = FirecrawlScrapeClient()     # reads FIRECRAWL_API_KEY from env
    result = await client.scrape("https://county.gov/assessor/parcel/12345")
    print(result.markdown)
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Sequence

from firecrawl import AsyncFirecrawl

from research.models import ScrapeResult, SearchAPIError

logger = logging.getLogger(__name__)


class FirecrawlScrapeClient:
    """Async wrapper around the Firecrawl scraping API.

    Reads the API key from the ``FIRECRAWL_API_KEY`` environment variable
    unless one is passed explicitly.
    """

    API_NAME = "firecrawl"

    def __init__(self, api_key: str | None = None):
        self._api_key = api_key or os.environ.get("FIRECRAWL_API_KEY", "")
        if not self._api_key:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=(
                    "No API key found. Set the FIRECRAWL_API_KEY environment "
                    "variable or pass api_key to FirecrawlScrapeClient()."
                ),
            )

        self._client = AsyncFirecrawl(api_key=self._api_key)

    async def scrape(
        self,
        url: str,
        *,
        only_main_content: bool = True,
        wait_for: int | None = None,
        timeout: float = 60.0,
        include_tags: Sequence[str] | None = None,
        exclude_tags: Sequence[str] | None = None,
    ) -> ScrapeResult:
        """Scrape a single URL and return the page as markdown.

        Args:
            url: The URL to scrape.
            only_main_content: If True, strip navigation, ads, footers, and
                other boilerplate. Keeps only the main article/page content.
            wait_for: Milliseconds to wait after page load before extracting
                content. Useful for pages that load content via JavaScript
                after the initial render.
            timeout: Maximum seconds to wait for the scrape to complete.
            include_tags: Only include content from these HTML tags.
            exclude_tags: Exclude content from these HTML tags.

        Returns:
            A ``ScrapeResult`` with the page's markdown content and metadata.

        Raises:
            SearchAPIError: On authentication failure, rate limiting,
                timeout, or other API errors.
        """
        kwargs: dict[str, Any] = {
            "only_main_content": only_main_content,
            "formats": ["markdown"],
        }
        if wait_for is not None:
            kwargs["wait_for"] = wait_for
        if include_tags:
            kwargs["include_tags"] = list(include_tags)
        if exclude_tags:
            kwargs["exclude_tags"] = list(exclude_tags)

        try:
            document = await asyncio.wait_for(
                self._client.scrape(url, **kwargs),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=f"Scrape timed out after {timeout}s for URL: {url}",
                retryable=True,
            )
        except ValueError as exc:
            # Firecrawl SDK raises ValueError for missing API key
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=str(exc),
                status_code=401,
                retryable=False,
            ) from exc
        except Exception as exc:
            status_code = _extract_status_code(exc)
            retryable = status_code in (429, 500, 502, 503, 504) if status_code else False

            if status_code == 429:
                logger.warning("Firecrawl rate limit hit for URL: %s", url)

            raise SearchAPIError(
                api_name=self.API_NAME,
                message=str(exc),
                status_code=status_code,
                retryable=retryable,
            ) from exc

        return _normalize_document(url, document)

    async def scrape_main_content(
        self,
        url: str,
        *,
        timeout: float = 60.0,
        wait_for: int | None = None,
    ) -> ScrapeResult:
        """Convenience method: scrape only the main content of a page.

        Equivalent to ``scrape(url, only_main_content=True)`` with sensible
        defaults for government and property record pages.

        Args:
            url: The URL to scrape.
            timeout: Maximum seconds to wait.
            wait_for: Milliseconds to wait after page load.

        Returns:
            A ``ScrapeResult`` with only the main body content.
        """
        return await self.scrape(
            url,
            only_main_content=True,
            timeout=timeout,
            wait_for=wait_for,
        )


def _normalize_document(url: str, document: Any) -> ScrapeResult:
    """Convert a Firecrawl Document object into a normalized ScrapeResult."""
    markdown = getattr(document, "markdown", None) or ""

    metadata: dict[str, Any] = {}
    doc_metadata = getattr(document, "metadata", None)
    if doc_metadata is not None:
        # Firecrawl metadata is a Pydantic model; convert to dict
        if hasattr(doc_metadata, "model_dump"):
            metadata = {
                k: v
                for k, v in doc_metadata.model_dump().items()
                if v is not None
            }
        elif isinstance(doc_metadata, dict):
            metadata = {k: v for k, v in doc_metadata.items() if v is not None}

    warning = getattr(document, "warning", None)
    error_in_meta = metadata.pop("error", None)

    has_error = bool(warning or error_in_meta)
    error_msg = warning or error_in_meta

    return ScrapeResult(
        url=url,
        markdown=markdown,
        metadata=metadata,
        source_api="firecrawl",
        success=not has_error and len(markdown) > 0,
        error=error_msg,
    )


def _extract_status_code(exc: Exception) -> int | None:
    """Try to pull an HTTP status code out of an exception.

    The Firecrawl SDK may wrap HTTP errors or raise them directly.
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
