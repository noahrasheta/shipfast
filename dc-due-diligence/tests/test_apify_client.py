"""Tests for the Apify web scraping API wrapper."""

import asyncio
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from research.models import ActorRunResult, SearchAPIError
from research.apify_client import ApifyScrapeClient


# ------------------------------------------------------------------
# Client construction tests
# ------------------------------------------------------------------


class TestClientConstruction:
    def test_raises_without_token(self):
        env = os.environ.copy()
        env.pop("APIFY_TOKEN", None)
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(SearchAPIError) as exc_info:
                ApifyScrapeClient()
            assert "APIFY_TOKEN" in str(exc_info.value)

    @patch("research.apify_client.ApifyClientAsync")
    def test_accepts_explicit_token(self, _mock_cls):
        client = ApifyScrapeClient(token="test-token-123")
        assert client._token == "test-token-123"

    @patch("research.apify_client.ApifyClientAsync")
    def test_reads_token_from_env(self, _mock_cls):
        with patch.dict(os.environ, {"APIFY_TOKEN": "env-token-456"}):
            client = ApifyScrapeClient()
            assert client._token == "env-token-456"


# ------------------------------------------------------------------
# Helpers for mocking the Apify client
# ------------------------------------------------------------------


def _make_client():
    """Create an ApifyScrapeClient with a mocked underlying SDK client."""
    with patch("research.apify_client.ApifyClientAsync") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance
        client = ApifyScrapeClient(token="test-token")
    return client, mock_instance


def _make_run_info(
    run_id="run-abc123",
    status="SUCCEEDED",
    dataset_id="dataset-xyz789",
):
    """Build a dict mimicking an Apify actor run result."""
    return {
        "id": run_id,
        "status": status,
        "defaultDatasetId": dataset_id,
    }


def _make_dataset_page(items):
    """Build an object mimicking an Apify ListPage result."""
    return SimpleNamespace(items=items)


# ------------------------------------------------------------------
# run_actor tests (mocked API)
# ------------------------------------------------------------------


class TestRunActor:
    def test_successful_actor_run(self):
        client, mock = _make_client()

        # Mock actor().call() to return run info
        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(return_value=_make_run_info())
        mock.actor.return_value = mock_actor

        # Mock dataset().list_items() to return items
        mock_dataset = MagicMock()
        mock_dataset.list_items = AsyncMock(
            return_value=_make_dataset_page([
                {"title": "Result 1", "url": "https://example.com/1"},
                {"title": "Result 2", "url": "https://example.com/2"},
            ])
        )
        mock.dataset.return_value = mock_dataset

        result = asyncio.run(
            client.run_actor(
                "apify/web-scraper",
                run_input={"startUrls": [{"url": "https://example.com"}]},
            )
        )

        assert isinstance(result, ActorRunResult)
        assert result.success is True
        assert result.actor_id == "apify/web-scraper"
        assert result.run_id == "run-abc123"
        assert result.status == "SUCCEEDED"
        assert result.item_count == 2
        assert result.items[0]["title"] == "Result 1"
        assert result.dataset_id == "dataset-xyz789"
        assert result.source_api == "apify"
        assert result.error is None

    def test_failed_actor_run(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(
            return_value=_make_run_info(status="FAILED")
        )
        mock.actor.return_value = mock_actor

        result = asyncio.run(
            client.run_actor("apify/bad-actor")
        )

        assert isinstance(result, ActorRunResult)
        assert result.success is False
        assert result.status == "FAILED"
        assert result.item_count == 0
        assert result.error is not None
        assert "FAILED" in result.error

    def test_timed_out_actor_run(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(
            return_value=_make_run_info(status="TIMED-OUT")
        )
        mock.actor.return_value = mock_actor

        result = asyncio.run(
            client.run_actor("apify/slow-actor", timeout_secs=60)
        )

        assert result.success is False
        assert result.status == "TIMED-OUT"

    def test_passes_run_input(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(return_value=_make_run_info())
        mock.actor.return_value = mock_actor

        mock_dataset = MagicMock()
        mock_dataset.list_items = AsyncMock(
            return_value=_make_dataset_page([])
        )
        mock.dataset.return_value = mock_dataset

        input_data = {
            "startUrls": [{"url": "https://county.gov/parcels"}],
            "maxRequestsPerCrawl": 10,
        }

        asyncio.run(
            client.run_actor("apify/web-scraper", run_input=input_data)
        )

        call_kwargs = mock_actor.call.call_args[1]
        assert call_kwargs["run_input"] == input_data

    def test_passes_memory_and_timeout(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(return_value=_make_run_info())
        mock.actor.return_value = mock_actor

        mock_dataset = MagicMock()
        mock_dataset.list_items = AsyncMock(
            return_value=_make_dataset_page([])
        )
        mock.dataset.return_value = mock_dataset

        asyncio.run(
            client.run_actor(
                "apify/web-scraper",
                timeout_secs=120,
                memory_mbytes=512,
                max_items=50,
            )
        )

        call_kwargs = mock_actor.call.call_args[1]
        assert call_kwargs["timeout_secs"] == 120
        assert call_kwargs["memory_mbytes"] == 512
        assert call_kwargs["max_items"] == 50

    def test_dataset_limit(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(return_value=_make_run_info())
        mock.actor.return_value = mock_actor

        mock_dataset = MagicMock()
        mock_dataset.list_items = AsyncMock(
            return_value=_make_dataset_page([
                {"title": "Item 1"},
            ])
        )
        mock.dataset.return_value = mock_dataset

        asyncio.run(
            client.run_actor("apify/web-scraper", dataset_limit=5)
        )

        list_kwargs = mock_dataset.list_items.call_args[1]
        assert list_kwargs["limit"] == 5

    def test_api_error_wraps_exception(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        mock.actor.return_value = mock_actor

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(
                client.run_actor("apify/web-scraper")
            )

        assert exc_info.value.api_name == "apify"
        assert "Connection refused" in str(exc_info.value)

    def test_rate_limit_marked_retryable(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(
            side_effect=Exception("429 Too Many Requests")
        )
        mock.actor.return_value = mock_actor

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(
                client.run_actor("apify/web-scraper")
            )

        assert exc_info.value.status_code == 429
        assert exc_info.value.retryable is True

    def test_actor_call_returns_none(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(return_value=None)
        mock.actor.return_value = mock_actor

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(
                client.run_actor("apify/nonexistent-actor")
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.retryable is False

    def test_no_dataset_id_returns_empty_items(self):
        client, mock = _make_client()

        mock_actor = MagicMock()
        mock_actor.call = AsyncMock(
            return_value=_make_run_info(dataset_id=None)
        )
        mock.actor.return_value = mock_actor

        # Even though SUCCEEDED, no dataset means no items
        result = asyncio.run(
            client.run_actor("apify/web-scraper")
        )

        assert result.success is True  # Status is SUCCEEDED
        assert result.item_count == 0
        assert result.dataset_id is None

    def test_overall_timeout_raises_error(self):
        client, mock = _make_client()

        mock_actor = MagicMock()

        async def slow_call(**kwargs):
            await asyncio.sleep(100)

        mock_actor.call = slow_call
        mock.actor.return_value = mock_actor

        with pytest.raises(SearchAPIError) as exc_info:
            asyncio.run(
                client.run_actor(
                    "apify/web-scraper",
                    timeout_secs=0,
                )
            )

        assert exc_info.value.retryable is True
        assert "did not finish" in str(exc_info.value)


# ------------------------------------------------------------------
# ActorRunResult model tests
# ------------------------------------------------------------------


class TestActorRunResult:
    def test_success_property(self):
        result = ActorRunResult(
            actor_id="apify/test",
            run_id="run-1",
            status="SUCCEEDED",
            items=[{"data": "value"}],
        )
        assert result.success is True

    def test_failure_property(self):
        result = ActorRunResult(
            actor_id="apify/test",
            run_id="run-1",
            status="FAILED",
        )
        assert result.success is False

    def test_item_count(self):
        result = ActorRunResult(
            actor_id="apify/test",
            run_id="run-1",
            status="SUCCEEDED",
            items=[{"a": 1}, {"b": 2}, {"c": 3}],
        )
        assert result.item_count == 3

    def test_default_source_api(self):
        result = ActorRunResult(
            actor_id="apify/test",
            run_id="run-1",
            status="SUCCEEDED",
        )
        assert result.source_api == "apify"


# ------------------------------------------------------------------
# Live integration test (skipped without API token)
# ------------------------------------------------------------------


@pytest.mark.skipif(
    not os.environ.get("APIFY_TOKEN"),
    reason="APIFY_TOKEN not set -- skipping live API test",
)
class TestApifyLive:
    def test_live_actor_run(self):
        """Run a simple, fast Apify actor to verify the integration works.

        Uses the 'apify/hello-world' actor which completes quickly and
        produces a small dataset.
        """
        client = ApifyScrapeClient()
        result = asyncio.run(
            client.run_actor(
                "apify/hello-world",
                timeout_secs=60,
            )
        )

        assert isinstance(result, ActorRunResult)
        assert result.source_api == "apify"
        assert result.status == "SUCCEEDED"
        assert result.success is True
        assert result.run_id
