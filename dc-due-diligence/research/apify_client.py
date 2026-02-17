"""
Apify API wrapper for complex web scraping workflows.

Apify provides a marketplace of pre-built "actors" -- specialized scrapers
for specific sites and data types.  This wrapper handles authentication,
actor execution, status polling, and dataset retrieval.

Usage::

    client = ApifyScrapeClient()          # reads APIFY_TOKEN from env
    result = await client.run_actor(
        actor_id="apify/web-scraper",
        run_input={"startUrls": [{"url": "https://example.com"}]},
    )
    for item in result.items:
        print(item)
"""

from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

from apify_client import ApifyClientAsync

from research.models import ActorRunResult, SearchAPIError

logger = logging.getLogger(__name__)


class ApifyScrapeClient:
    """Async wrapper around the Apify platform API.

    Reads the API token from the ``APIFY_TOKEN`` environment variable
    unless one is passed explicitly.
    """

    API_NAME = "apify"

    # Terminal statuses from the Apify API
    _TERMINAL_STATUSES = frozenset({
        "SUCCEEDED",
        "FAILED",
        "TIMED-OUT",
        "ABORTED",
    })

    def __init__(self, token: str | None = None):
        self._token = token or os.environ.get("APIFY_TOKEN", "")
        if not self._token:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=(
                    "No API token found. Set the APIFY_TOKEN environment "
                    "variable or pass token to ApifyScrapeClient()."
                ),
            )

        self._client = ApifyClientAsync(token=self._token)

    async def run_actor(
        self,
        actor_id: str,
        *,
        run_input: dict[str, Any] | None = None,
        timeout_secs: int = 300,
        memory_mbytes: int | None = None,
        max_items: int | None = None,
        poll_interval: float = 2.0,
        dataset_limit: int | None = None,
    ) -> ActorRunResult:
        """Run an Apify marketplace actor and retrieve its results.

        This starts the actor, polls until it reaches a terminal status,
        then fetches items from its default dataset.

        Args:
            actor_id: The Apify actor identifier (e.g. ``"apify/web-scraper"``
                or ``"username/actor-name"``).
            run_input: Input parameters for the actor.  Structure depends on
                the specific actor being used.
            timeout_secs: Maximum seconds the actor is allowed to run on
                the Apify platform before timing out.
            memory_mbytes: Memory allocation for the actor run in MB.
                Defaults to the actor's default memory setting.
            max_items: Maximum number of dataset items the actor should
                produce (supported by some actors).
            poll_interval: Seconds between status checks while waiting
                for the actor to finish.
            dataset_limit: Maximum number of items to retrieve from the
                actor's default dataset.  None means retrieve all items.

        Returns:
            An ``ActorRunResult`` containing the run metadata and dataset items.

        Raises:
            SearchAPIError: On authentication failure, actor not found,
                rate limiting, timeout, or other API errors.
        """
        call_kwargs: dict[str, Any] = {
            "run_input": run_input or {},
            "timeout_secs": timeout_secs,
        }
        if memory_mbytes is not None:
            call_kwargs["memory_mbytes"] = memory_mbytes
        if max_items is not None:
            call_kwargs["max_items"] = max_items

        try:
            run_info = await asyncio.wait_for(
                self._start_and_wait(actor_id, call_kwargs, poll_interval),
                timeout=float(timeout_secs) + 30.0,
            )
        except asyncio.TimeoutError:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=(
                    f"Actor {actor_id} did not finish within "
                    f"{timeout_secs + 30}s (including polling overhead)"
                ),
                retryable=True,
            )
        except Exception as exc:
            status_code = _extract_status_code(exc)
            retryable = status_code in (429, 500, 502, 503, 504) if status_code else False

            if status_code == 429:
                logger.warning("Apify rate limit hit for actor: %s", actor_id)

            raise SearchAPIError(
                api_name=self.API_NAME,
                message=str(exc),
                status_code=status_code,
                retryable=retryable,
            ) from exc

        run_id = run_info.get("id", "")
        status = run_info.get("status", "FAILED")
        dataset_id = run_info.get("defaultDatasetId")

        if status != "SUCCEEDED":
            error_msg = (
                f"Actor {actor_id} finished with status: {status}"
            )
            logger.warning(error_msg)
            return ActorRunResult(
                actor_id=actor_id,
                run_id=run_id,
                status=status,
                items=[],
                dataset_id=dataset_id,
                error=error_msg,
            )

        items = await self._fetch_dataset_items(dataset_id, limit=dataset_limit)

        return ActorRunResult(
            actor_id=actor_id,
            run_id=run_id,
            status=status,
            items=items,
            dataset_id=dataset_id,
        )

    async def _start_and_wait(
        self,
        actor_id: str,
        call_kwargs: dict[str, Any],
        poll_interval: float,
    ) -> dict[str, Any]:
        """Start an actor run and poll until it finishes.

        The Apify SDK's ``call()`` method handles start + wait internally.
        """
        actor_client = self._client.actor(actor_id)
        result = await actor_client.call(**call_kwargs)
        if result is None:
            raise SearchAPIError(
                api_name=self.API_NAME,
                message=f"Actor {actor_id} call returned None (possibly not found or no permission)",
                status_code=404,
                retryable=False,
            )
        return result

    async def _fetch_dataset_items(
        self,
        dataset_id: str | None,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve items from an actor's default dataset."""
        if not dataset_id:
            return []

        dataset_client = self._client.dataset(dataset_id)
        list_kwargs: dict[str, Any] = {}
        if limit is not None:
            list_kwargs["limit"] = limit

        page = await dataset_client.list_items(**list_kwargs)
        return page.items if hasattr(page, "items") else []


def _extract_status_code(exc: Exception) -> int | None:
    """Try to pull an HTTP status code out of an exception.

    The Apify SDK may raise various exceptions wrapping HTTP errors.
    """
    if hasattr(exc, "response") and hasattr(exc.response, "status_code"):
        return int(exc.response.status_code)
    if hasattr(exc, "status_code"):
        return int(exc.status_code)

    exc_str = str(exc)
    for code in (401, 403, 404, 429, 500, 502, 503, 504):
        if str(code) in exc_str:
            return code

    return None
