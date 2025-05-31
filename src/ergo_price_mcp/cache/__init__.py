"""
Caching layer for Ergo Price MCP Server.

This package provides in-memory caching with TTL support for price data,
asset metadata, and market information to optimize performance and reduce
API calls to external services.
"""

from .decorators import (
    CacheManager,
    cache_history_data,
    cache_metadata,
    cache_price_data,
    cache_static_data,
    cached,
    get_cache_manager,
)
from .memory_cache import (
    CacheEntry,
    CacheStats,
    MemoryCache,
    get_cache,
    initialize_cache,
    shutdown_cache,
)

__all__ = [
    # Core cache components
    "MemoryCache",
    "CacheEntry", 
    "CacheStats",
    "get_cache",
    "initialize_cache",
    "shutdown_cache",
    # Decorators and utilities
    "cached",
    "cache_price_data",
    "cache_metadata",
    "cache_history_data",
    "cache_static_data",
    "CacheManager",
    "get_cache_manager",
]
