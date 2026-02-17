"""
SQLite-backed response cache with per-data-type TTLs.

Persists successful API responses so repeated lookups for the same query
across CLI runs skip the API entirely.  Each cached entry has a TTL that
depends on how quickly the underlying data changes:

- **ownership** -- property records change infrequently: 7-day TTL
- **market** -- market comps and pricing shift often: 1-day TTL
- **news** -- news is perishable: 1-hour TTL
- **general** -- default bucket: 4-hour TTL

Usage::

    cache = ResponseCache()  # creates ~/.dc_due_diligence/research_cache.db
    key = cache.make_key("tavily", "search", "data center Dallas TX")
    hit = await cache.get(key)
    if hit is None:
        result = await tavily_client.search(query)
        await cache.put(key, result_json, data_type="market")
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# TTLs in seconds
DEFAULT_TTLS: dict[str, int] = {
    "ownership": 7 * 24 * 60 * 60,   # 7 days
    "market": 1 * 24 * 60 * 60,      # 1 day
    "news": 1 * 60 * 60,             # 1 hour
    "general": 4 * 60 * 60,          # 4 hours
}


@dataclass
class CacheStats:
    """Snapshot of cache usage counters.

    Attributes:
        hits: Number of successful cache lookups.
        misses: Number of cache lookups that returned no result.
        stores: Number of entries written to the cache.
        evictions: Number of expired entries cleaned up.
        total_entries: Current number of entries in the database.
    """

    hits: int
    misses: int
    stores: int
    evictions: int
    total_entries: int


class ResponseCache:
    """SQLite-backed response cache with TTLs.

    The database file is created at ``db_path``.  If not provided, it
    defaults to ``~/.dc_due_diligence/research_cache.db``.

    The cache is safe for concurrent reads from multiple threads or async
    tasks because SQLite handles locking at the file level.  Writes are
    serialized through a single connection.

    Args:
        db_path: Path to the SQLite database file.  Created if it doesn't
            exist.  Parent directories are created automatically.
        ttls: Mapping of data-type names to TTL in seconds.  Merged with
            ``DEFAULT_TTLS`` so you only need to override the ones you
            want to change.
    """

    def __init__(
        self,
        db_path: str | Path | None = None,
        ttls: dict[str, int] | None = None,
    ):
        if db_path is None:
            cache_dir = Path.home() / ".dc_due_diligence"
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / "research_cache.db"

        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

        self._ttls = {**DEFAULT_TTLS, **(ttls or {})}

        self._hits = 0
        self._misses = 0
        self._stores = 0
        self._evictions = 0

        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._create_table()

    def _create_table(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS response_cache (
                cache_key   TEXT PRIMARY KEY,
                api_name    TEXT NOT NULL,
                operation   TEXT NOT NULL,
                query       TEXT NOT NULL,
                data_type   TEXT NOT NULL DEFAULT 'general',
                response    TEXT NOT NULL,
                created_at  REAL NOT NULL,
                expires_at  REAL NOT NULL
            )
            """
        )
        self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_expires ON response_cache(expires_at)"
        )
        self._conn.commit()

    @staticmethod
    def make_key(api_name: str, operation: str, query: str) -> str:
        """Build a deterministic cache key from the API name, operation, and query.

        The key is a SHA-256 hex digest so it's safe as a database primary key
        regardless of query length or special characters.

        Args:
            api_name: e.g. ``"tavily"``, ``"firecrawl"``
            operation: e.g. ``"search"``, ``"scrape"``
            query: The query string or URL being looked up.

        Returns:
            A 64-character hex string.
        """
        raw = f"{api_name}:{operation}:{query}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    async def get(self, cache_key: str) -> dict[str, Any] | None:
        """Look up a cached response.

        Returns the deserialized JSON response if the entry exists and has
        not expired, or ``None`` on a miss.

        Expired entries are deleted on access.
        """
        now = time.time()
        row = self._conn.execute(
            "SELECT response, expires_at FROM response_cache WHERE cache_key = ?",
            (cache_key,),
        ).fetchone()

        if row is None:
            self._misses += 1
            return None

        response_json, expires_at = row

        if now > expires_at:
            # Entry has expired -- delete it and count as a miss
            self._conn.execute(
                "DELETE FROM response_cache WHERE cache_key = ?",
                (cache_key,),
            )
            self._conn.commit()
            self._misses += 1
            self._evictions += 1
            return None

        self._hits += 1
        return json.loads(response_json)

    async def put(
        self,
        cache_key: str,
        response: dict[str, Any],
        *,
        api_name: str = "",
        operation: str = "",
        query: str = "",
        data_type: str = "general",
    ) -> None:
        """Store a response in the cache.

        Args:
            cache_key: The key returned by ``make_key()``.
            response: The API response to cache (must be JSON-serializable).
            api_name: API that produced this response (for debugging).
            operation: Operation type (for debugging).
            query: Original query string (for debugging).
            data_type: Determines the TTL.  One of ``"ownership"``,
                ``"market"``, ``"news"``, or ``"general"``.
        """
        ttl = self._ttls.get(data_type, self._ttls["general"])
        now = time.time()
        expires_at = now + ttl

        self._conn.execute(
            """
            INSERT OR REPLACE INTO response_cache
                (cache_key, api_name, operation, query, data_type, response, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cache_key,
                api_name,
                operation,
                query,
                data_type,
                json.dumps(response),
                now,
                expires_at,
            ),
        )
        self._conn.commit()
        self._stores += 1

    async def evict_expired(self) -> int:
        """Remove all expired entries from the cache.

        Returns:
            Number of entries deleted.
        """
        now = time.time()
        cursor = self._conn.execute(
            "DELETE FROM response_cache WHERE expires_at < ?", (now,)
        )
        self._conn.commit()
        count = cursor.rowcount
        self._evictions += count
        return count

    async def clear(self) -> int:
        """Delete all entries from the cache.

        Returns:
            Number of entries deleted.
        """
        cursor = self._conn.execute("DELETE FROM response_cache")
        self._conn.commit()
        return cursor.rowcount

    def stats(self) -> CacheStats:
        """Return a snapshot of cache usage counters."""
        total = self._conn.execute(
            "SELECT COUNT(*) FROM response_cache"
        ).fetchone()[0]

        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            stores=self._stores,
            evictions=self._evictions,
            total_entries=total,
        )

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
