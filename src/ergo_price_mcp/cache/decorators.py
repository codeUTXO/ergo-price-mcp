"""
Cache decorators and utilities for the Ergo Price MCP Server.

This module provides decorators and utilities to easily add caching
to API methods and functions.
"""

import functools
import hashlib
import json
from typing import Any, Callable, Optional, TypeVar, Union

from ..utils.config import get_settings
from ..utils.logging import get_logger
from .memory_cache import get_cache

logger = get_logger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def cache_key_from_args(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    
    Args:
        *args: Function positional arguments
        **kwargs: Function keyword arguments
        
    Returns:
        A hash-based cache key
    """
    try:
        # Create a stable representation of arguments
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        
        # Convert to JSON string (sorted for consistency)
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        
        # Generate hash
        hash_obj = hashlib.sha256(key_str.encode('utf-8'))
        return hash_obj.hexdigest()[:16]  # Use first 16 chars
        
    except Exception as e:
        logger.warning(
            "Failed to generate cache key from args",
            extra={"error": str(e)}
        )
        # Fallback to string representation
        return str(hash(str(args) + str(sorted(kwargs.items()))))


def cached(
    ttl: Optional[int] = None,
    prefix: Optional[str] = None,
    key_func: Optional[Callable[..., str]] = None,
    skip_cache: Optional[Callable[..., bool]] = None
):
    """
    Decorator to add caching to functions.
    
    Args:
        ttl: Cache TTL in seconds (None for default)
        prefix: Cache key prefix
        key_func: Function to generate cache key from arguments
        skip_cache: Function to determine if caching should be skipped
        
    Returns:
        Decorated function with caching
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Check if we should skip caching
            if skip_cache and skip_cache(*args, **kwargs):
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{cache_key_from_args(*args, **kwargs)}"
            
            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key, prefix=prefix)
            
            if cached_value is not None:
                logger.debug(
                    "Cache hit for function",
                    extra={
                        "function": func.__name__,
                        "cache_key": cache_key,
                        "prefix": prefix
                    }
                )
                return cached_value
            
            # Execute function and cache result
            try:
                result = await func(*args, **kwargs)
                
                # Cache the result
                cache.set(
                    key=cache_key,
                    value=result,
                    ttl=ttl,
                    prefix=prefix
                )
                
                logger.debug(
                    "Cached function result",
                    extra={
                        "function": func.__name__,
                        "cache_key": cache_key,
                        "prefix": prefix,
                        "ttl": ttl
                    }
                )
                
                return result
                
            except Exception as e:
                logger.error(
                    "Error executing cached function",
                    extra={
                        "function": func.__name__,
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Check if we should skip caching
            if skip_cache and skip_cache(*args, **kwargs):
                return func(*args, **kwargs)
            
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{cache_key_from_args(*args, **kwargs)}"
            
            # Try to get from cache
            cache = get_cache()
            cached_value = cache.get(cache_key, prefix=prefix)
            
            if cached_value is not None:
                logger.debug(
                    "Cache hit for function",
                    extra={
                        "function": func.__name__,
                        "cache_key": cache_key,
                        "prefix": prefix
                    }
                )
                return cached_value
            
            # Execute function and cache result
            try:
                result = func(*args, **kwargs)
                
                # Cache the result
                cache.set(
                    key=cache_key,
                    value=result,
                    ttl=ttl,
                    prefix=prefix
                )
                
                logger.debug(
                    "Cached function result",
                    extra={
                        "function": func.__name__,
                        "cache_key": cache_key,
                        "prefix": prefix,
                        "ttl": ttl
                    }
                )
                
                return result
                
            except Exception as e:
                logger.error(
                    "Error executing cached function",
                    extra={
                        "function": func.__name__,
                        "error": str(e)
                    },
                    exc_info=True
                )
                raise
        
        # Return appropriate wrapper based on whether function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def cache_price_data(ttl: Optional[int] = None):
    """
    Decorator specifically for price data caching.
    
    Args:
        ttl: Cache TTL in seconds (uses price TTL from config if None)
        
    Returns:
        Decorated function with price data caching
    """
    def get_ttl():
        if ttl is not None:
            return ttl
        settings = get_settings()
        return settings.cache.ttl_price
    
    return cached(
        ttl=get_ttl(),
        prefix="price",
        key_func=lambda *args, **kwargs: cache_key_from_args(*args, **kwargs)
    )


def cache_metadata(ttl: Optional[int] = None):
    """
    Decorator specifically for metadata caching.
    
    Args:
        ttl: Cache TTL in seconds (uses metadata TTL from config if None)
        
    Returns:
        Decorated function with metadata caching
    """
    def get_ttl():
        if ttl is not None:
            return ttl
        settings = get_settings()
        return settings.cache.ttl_metadata
    
    return cached(
        ttl=get_ttl(),
        prefix="metadata",
        key_func=lambda *args, **kwargs: cache_key_from_args(*args, **kwargs)
    )


def cache_history_data(ttl: Optional[int] = None):
    """
    Decorator specifically for historical data caching.
    
    Args:
        ttl: Cache TTL in seconds (uses history TTL from config if None)
        
    Returns:
        Decorated function with historical data caching
    """
    def get_ttl():
        if ttl is not None:
            return ttl
        settings = get_settings()
        return settings.cache.ttl_history
    
    return cached(
        ttl=get_ttl(),
        prefix="history",
        key_func=lambda *args, **kwargs: cache_key_from_args(*args, **kwargs)
    )


def cache_static_data(ttl: Optional[int] = None):
    """
    Decorator specifically for static data caching.
    
    Args:
        ttl: Cache TTL in seconds (uses static TTL from config if None)
        
    Returns:
        Decorated function with static data caching
    """
    def get_ttl():
        if ttl is not None:
            return ttl
        settings = get_settings()
        return settings.cache.ttl_static
    
    return cached(
        ttl=get_ttl(),
        prefix="static",
        key_func=lambda *args, **kwargs: cache_key_from_args(*args, **kwargs)
    )


class CacheManager:
    """
    Cache manager for complex caching operations.
    
    Provides high-level cache management methods for different data types.
    """
    
    def __init__(self):
        self.cache = get_cache()
        self.settings = get_settings()
    
    def cache_token_price(
        self,
        token_id: str,
        price_data: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache token price data.
        
        Args:
            token_id: Token ID
            price_data: Price data to cache
            ttl: Cache TTL in seconds
        """
        cache_ttl = ttl or self.settings.cache.ttl_price
        self.cache.set(
            key=token_id,
            value=price_data,
            ttl=cache_ttl,
            prefix="price"
        )
    
    def get_token_price(self, token_id: str) -> Optional[Any]:
        """
        Get cached token price data.
        
        Args:
            token_id: Token ID
            
        Returns:
            Cached price data if available, None otherwise
        """
        return self.cache.get(token_id, prefix="price")
    
    def cache_token_metadata(
        self,
        token_id: str,
        metadata: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache token metadata.
        
        Args:
            token_id: Token ID
            metadata: Metadata to cache
            ttl: Cache TTL in seconds
        """
        cache_ttl = ttl or self.settings.cache.ttl_metadata
        self.cache.set(
            key=token_id,
            value=metadata,
            ttl=cache_ttl,
            prefix="metadata"
        )
    
    def get_token_metadata(self, token_id: str) -> Optional[Any]:
        """
        Get cached token metadata.
        
        Args:
            token_id: Token ID
            
        Returns:
            Cached metadata if available, None otherwise
        """
        return self.cache.get(token_id, prefix="metadata")
    
    def cache_historical_data(
        self,
        key: str,
        data: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache historical data.
        
        Args:
            key: Cache key
            data: Historical data to cache
            ttl: Cache TTL in seconds
        """
        cache_ttl = ttl or self.settings.cache.ttl_history
        self.cache.set(
            key=key,
            value=data,
            ttl=cache_ttl,
            prefix="history"
        )
    
    def get_historical_data(self, key: str) -> Optional[Any]:
        """
        Get cached historical data.
        
        Args:
            key: Cache key
            
        Returns:
            Cached historical data if available, None otherwise
        """
        return self.cache.get(key, prefix="history")
    
    def invalidate_token_data(self, token_id: str) -> None:
        """
        Invalidate all cached data for a token.
        
        Args:
            token_id: Token ID
        """
        self.cache.delete(token_id, prefix="price")
        self.cache.delete(token_id, prefix="metadata")
        
        # Also clean up any historical data that includes this token
        history_keys = self.cache.get_keys(prefix="history")
        for key in history_keys:
            if token_id in key:
                self.cache.delete(key.split(":", 1)[1], prefix="history")
    
    def clear_all_data(self) -> None:
        """Clear all cached data."""
        self.cache.clear()
    
    def clear_by_type(self, data_type: str) -> int:
        """
        Clear cached data by type.
        
        Args:
            data_type: Type of data to clear (price, metadata, history, static)
            
        Returns:
            Number of entries cleared
        """
        return self.cache.clear(prefix=data_type)
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = self.cache.get_stats()
        return {
            "hits": stats.hits,
            "misses": stats.misses,
            "hit_rate": stats.hit_rate,
            "entries": stats.entries,
            "total_size_bytes": stats.total_size_bytes,
            "evictions": stats.evictions,
            "expirations": stats.expirations,
            "average_ttl": stats.average_ttl,
            "created_at": stats.created_at.isoformat()
        }


# Missing import for asyncio
import asyncio


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        The global CacheManager instance
    """
    global _cache_manager
    
    if _cache_manager is None:
        _cache_manager = CacheManager()
    
    return _cache_manager 