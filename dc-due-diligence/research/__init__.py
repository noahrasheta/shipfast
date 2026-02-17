"""
Web research tools for data center due diligence.

Provides search and scraping API wrappers that normalize results into
common formats so downstream agents can query the web and scrape pages
without worrying about which API is handling the request.

- ``tavily_client`` -- Tavily for general web search
- ``exa_client`` -- Exa for semantic / AI-native search
- ``firecrawl_client`` -- Firecrawl for JavaScript-heavy page scraping
- ``apify_client`` -- Apify for complex scraping workflows via marketplace actors
- ``rate_limiter`` -- Token-bucket rate limiting with concurrency caps
- ``cache`` -- SQLite-backed response cache with per-data-type TTLs
- ``manager`` -- Unified WebResearchManager with routing, caching, and fallback
"""

from research.models import (
    ActorRunResult,
    ScrapeResult,
    SearchAPIError,
    SearchResponse,
    SearchResult,
)
from research.rate_limiter import (
    RateLimiter,
    RateLimiterStats,
    RateLimitExceeded,
    create_default_limiters,
)
from research.cache import CacheStats, ResponseCache
from research.manager import ManagerStats, WebResearchManager
from research.tavily_client import TavilySearchClient
from research.exa_client import ExaSearchClient
from research.firecrawl_client import FirecrawlScrapeClient
from research.apify_client import ApifyScrapeClient

__all__ = [
    "ActorRunResult",
    "ApifyScrapeClient",
    "CacheStats",
    "ExaSearchClient",
    "FirecrawlScrapeClient",
    "ManagerStats",
    "RateLimiter",
    "RateLimiterStats",
    "RateLimitExceeded",
    "ResponseCache",
    "ScrapeResult",
    "SearchAPIError",
    "SearchResponse",
    "SearchResult",
    "TavilySearchClient",
    "WebResearchManager",
    "create_default_limiters",
]
