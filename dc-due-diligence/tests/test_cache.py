"""Tests for the SQLite-backed response cache."""

import asyncio
import tempfile
import time
from pathlib import Path

import pytest

from research.cache import DEFAULT_TTLS, CacheStats, ResponseCache


def _make_cache(ttls=None):
    """Create a cache backed by a temp file."""
    tmp = tempfile.mktemp(suffix=".db")
    return ResponseCache(db_path=tmp, ttls=ttls)


class TestCacheConstruction:
    def test_creates_database_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "test_cache.db"
            cache = ResponseCache(db_path=db_path)
            assert db_path.exists()
            cache.close()

    def test_creates_parent_directories(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "nested" / "dir" / "cache.db"
            cache = ResponseCache(db_path=db_path)
            assert db_path.exists()
            cache.close()

    def test_default_ttls_are_set(self):
        cache = _make_cache()
        assert cache._ttls["ownership"] == 7 * 24 * 60 * 60
        assert cache._ttls["market"] == 1 * 24 * 60 * 60
        assert cache._ttls["news"] == 1 * 60 * 60
        assert cache._ttls["general"] == 4 * 60 * 60
        cache.close()

    def test_custom_ttls_override_defaults(self):
        cache = _make_cache(ttls={"ownership": 999, "custom_type": 42})
        assert cache._ttls["ownership"] == 999
        assert cache._ttls["custom_type"] == 42
        # Others keep defaults
        assert cache._ttls["general"] == DEFAULT_TTLS["general"]
        cache.close()


class TestMakeKey:
    def test_deterministic(self):
        key1 = ResponseCache.make_key("tavily", "search", "data center Dallas")
        key2 = ResponseCache.make_key("tavily", "search", "data center Dallas")
        assert key1 == key2

    def test_different_inputs_produce_different_keys(self):
        k1 = ResponseCache.make_key("tavily", "search", "query A")
        k2 = ResponseCache.make_key("tavily", "search", "query B")
        k3 = ResponseCache.make_key("exa", "search", "query A")
        k4 = ResponseCache.make_key("tavily", "scrape", "query A")
        assert len({k1, k2, k3, k4}) == 4

    def test_key_is_hex_string(self):
        key = ResponseCache.make_key("api", "op", "q")
        assert len(key) == 64
        assert all(c in "0123456789abcdef" for c in key)


class TestGetAndPut:
    def test_miss_returns_none(self):
        cache = _make_cache()

        async def run():
            result = await cache.get("nonexistent_key")
            assert result is None

        asyncio.run(run())
        cache.close()

    def test_put_then_get(self):
        cache = _make_cache()

        async def run():
            key = ResponseCache.make_key("tavily", "search", "test query")
            data = {"results": [{"title": "Test", "url": "https://example.com"}]}

            await cache.put(
                key, data,
                api_name="tavily", operation="search",
                query="test query", data_type="general",
            )

            result = await cache.get(key)
            assert result is not None
            assert result["results"][0]["title"] == "Test"
            assert result["results"][0]["url"] == "https://example.com"

        asyncio.run(run())
        cache.close()

    def test_overwrite_existing_entry(self):
        cache = _make_cache()

        async def run():
            key = "test_key_overwrite"
            await cache.put(key, {"version": 1}, api_name="x", operation="y", query="z")
            await cache.put(key, {"version": 2}, api_name="x", operation="y", query="z")

            result = await cache.get(key)
            assert result["version"] == 2

        asyncio.run(run())
        cache.close()


class TestTTLExpiry:
    def test_expired_entry_returns_none(self):
        # Set a 1-second TTL for the "general" type
        cache = _make_cache(ttls={"general": 1})

        async def run():
            key = "expiry_test"
            await cache.put(key, {"data": "perishable"}, data_type="general")

            # Should be there immediately
            assert await cache.get(key) is not None

            # Wait for expiry
            await asyncio.sleep(1.1)

            # Should be gone now
            result = await cache.get(key)
            assert result is None

        asyncio.run(run())
        cache.close()

    def test_different_data_types_have_different_ttls(self):
        cache = _make_cache(ttls={"news": 1, "ownership": 3600})

        async def run():
            key_news = "news_key"
            key_own = "ownership_key"

            await cache.put(key_news, {"type": "news"}, data_type="news")
            await cache.put(key_own, {"type": "ownership"}, data_type="ownership")

            await asyncio.sleep(1.1)

            # News should have expired
            assert await cache.get(key_news) is None
            # Ownership should still be there
            assert await cache.get(key_own) is not None

        asyncio.run(run())
        cache.close()


class TestEvictExpired:
    def test_evict_removes_expired_entries(self):
        cache = _make_cache(ttls={"general": 1})

        async def run():
            await cache.put("a", {"x": 1}, data_type="general")
            await cache.put("b", {"x": 2}, data_type="general")

            await asyncio.sleep(1.1)

            evicted = await cache.evict_expired()
            assert evicted == 2

            assert await cache.get("a") is None
            assert await cache.get("b") is None

        asyncio.run(run())
        cache.close()


class TestClear:
    def test_clear_removes_all(self):
        cache = _make_cache()

        async def run():
            await cache.put("a", {"x": 1})
            await cache.put("b", {"x": 2})
            await cache.put("c", {"x": 3})

            deleted = await cache.clear()
            assert deleted == 3

            assert await cache.get("a") is None
            assert await cache.get("b") is None
            assert await cache.get("c") is None

        asyncio.run(run())
        cache.close()


class TestCacheStats:
    def test_stats_track_hits_and_misses(self):
        cache = _make_cache()

        async def run():
            key = "stats_test"
            # Miss
            await cache.get(key)
            # Store
            await cache.put(key, {"data": "value"})
            # Hit
            await cache.get(key)
            # Another miss
            await cache.get("nonexistent")

        asyncio.run(run())

        stats = cache.stats()
        assert isinstance(stats, CacheStats)
        assert stats.hits == 1
        assert stats.misses == 2
        assert stats.stores == 1
        assert stats.total_entries == 1
        cache.close()

    def test_eviction_counter(self):
        cache = _make_cache(ttls={"general": 1})

        async def run():
            await cache.put("a", {"x": 1}, data_type="general")
            await asyncio.sleep(1.1)
            # Accessing triggers eviction
            await cache.get("a")

        asyncio.run(run())
        assert cache.stats().evictions == 1
        cache.close()


class TestPersistence:
    def test_data_persists_across_instances(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "persist.db"

            # Write with one instance
            cache1 = ResponseCache(db_path=db_path)

            async def write():
                await cache1.put("persist_key", {"saved": True})

            asyncio.run(write())
            cache1.close()

            # Read with a new instance
            cache2 = ResponseCache(db_path=db_path)

            async def read():
                result = await cache2.get("persist_key")
                assert result is not None
                assert result["saved"] is True

            asyncio.run(read())
            cache2.close()
