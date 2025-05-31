"""
In-memory cache implementation with TTL support.

This module provides a thread-safe in-memory cache with time-to-live (TTL)
support for caching API responses and computed data.
"""

import asyncio
import hashlib
import json
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Generic, Optional, Set, TypeVar, Union

from pydantic import BaseModel

from ..utils.config import get_settings
from ..utils.logging import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    """
    Represents a single cache entry with TTL and metadata.
    
    Attributes:
        value: The cached value
        created_at: When the entry was created
        expires_at: When the entry expires
        access_count: Number of times the entry has been accessed
        last_accessed: When the entry was last accessed
        size_bytes: Estimated size of the entry in bytes
    """
    value: T
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    size_bytes: int = 0

    def __post_init__(self):
        """Calculate the estimated size of the entry."""
        self.size_bytes = self._estimate_size(self.value)

    def is_expired(self) -> bool:
        """Check if the cache entry has expired."""
        return datetime.now() > self.expires_at

    def is_valid(self) -> bool:
        """Check if the cache entry is valid (not expired)."""
        return not self.is_expired()

    def access(self) -> T:
        """
        Access the cached value and update access statistics.
        
        Returns:
            The cached value
            
        Raises:
            ValueError: If the entry has expired
        """
        if self.is_expired():
            raise ValueError("Cache entry has expired")
        
        self.access_count += 1
        self.last_accessed = datetime.now()
        return self.value

    def time_to_expire(self) -> timedelta:
        """Get the time remaining until expiration."""
        now = datetime.now()
        if now >= self.expires_at:
            return timedelta(0)
        return self.expires_at - now

    @staticmethod
    def _estimate_size(value: Any) -> int:
        """
        Estimate the size of a value in bytes.
        
        Args:
            value: The value to estimate size for
            
        Returns:
            Estimated size in bytes
        """
        try:
            if isinstance(value, str):
                return len(value.encode('utf-8'))
            elif isinstance(value, (int, float)):
                return 8  # Rough estimate
            elif isinstance(value, bool):
                return 1
            elif isinstance(value, BaseModel):
                return len(value.model_dump_json().encode('utf-8'))
            elif isinstance(value, (list, tuple)):
                return sum(CacheEntry._estimate_size(item) for item in value)
            elif isinstance(value, dict):
                return sum(
                    CacheEntry._estimate_size(k) + CacheEntry._estimate_size(v)
                    for k, v in value.items()
                )
            else:
                # Fall back to JSON serialization for size estimation
                return len(json.dumps(value, default=str).encode('utf-8'))
        except Exception:
            # If we can't estimate, return a reasonable default
            return 100


@dataclass
class CacheStats:
    """
    Cache statistics for monitoring and optimization.
    
    Attributes:
        hits: Number of cache hits
        misses: Number of cache misses  
        entries: Current number of entries
        total_size_bytes: Total estimated size of all entries
        evictions: Number of entries evicted
        expirations: Number of entries that expired naturally
        average_ttl: Average TTL of current entries
        hit_rate: Cache hit rate as a percentage
    """
    hits: int = 0
    misses: int = 0
    entries: int = 0
    total_size_bytes: int = 0
    evictions: int = 0
    expirations: int = 0
    average_ttl: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate the cache hit rate as a percentage."""
        total_requests = self.hits + self.misses
        if total_requests == 0:
            return 0.0
        return (self.hits / total_requests) * 100

    @property
    def total_requests(self) -> int:
        """Get total number of cache requests."""
        return self.hits + self.misses

    def reset(self):
        """Reset all statistics."""
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expirations = 0
        self.created_at = datetime.now()


class MemoryCache:
    """
    Thread-safe in-memory cache with TTL support and LRU eviction.
    
    Features:
    - TTL-based expiration
    - LRU eviction when max size is reached
    - Thread-safe operations
    - Cache statistics and monitoring
    - Automatic cleanup of expired entries
    - Key prefix support for namespacing
    """

    def __init__(self, max_size: Optional[int] = None, cleanup_interval: int = 300):
        """
        Initialize the memory cache.
        
        Args:
            max_size: Maximum number of entries (None for unlimited)
            cleanup_interval: Interval in seconds for automatic cleanup
        """
        settings = get_settings()
        
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: Dict[str, float] = {}  # key -> timestamp for LRU
        self._max_size = max_size or settings.cache.max_size
        self._cleanup_interval = cleanup_interval
        self._lock = threading.RLock()
        self._stats = CacheStats()
        self._cleanup_task: Optional[asyncio.Task] = None
        self._stop_cleanup = threading.Event()

        logger.info(
            "Initialized MemoryCache",
            extra={
                "max_size": self._max_size,
                "cleanup_interval": self._cleanup_interval
            }
        )

    async def start_cleanup_task(self):
        """Start the automatic cleanup task."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._stop_cleanup.clear()
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            logger.info("Started cache cleanup task")

    async def stop_cleanup_task(self):
        """Stop the automatic cleanup task."""
        self._stop_cleanup.set()
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            logger.info("Stopped cache cleanup task")

    async def _cleanup_loop(self):
        """Background task to periodically clean up expired entries."""
        while not self._stop_cleanup.is_set():
            try:
                expired_count = self.cleanup_expired()
                if expired_count > 0:
                    logger.debug(
                        "Cleaned up expired cache entries",
                        extra={"expired_count": expired_count}
                    )
                
                # Wait for cleanup interval or until stop is set
                for _ in range(self._cleanup_interval):
                    if self._stop_cleanup.is_set():
                        break
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(
                    "Error in cache cleanup loop",
                    extra={"error": str(e)},
                    exc_info=True
                )
                await asyncio.sleep(5)  # Brief pause before retrying

    def _generate_key(self, key: str, prefix: Optional[str] = None) -> str:
        """
        Generate a cache key with optional prefix.
        
        Args:
            key: The base key
            prefix: Optional prefix for namespacing
            
        Returns:
            The final cache key
        """
        if prefix:
            return f"{prefix}:{key}"
        return key

    def _generate_hash_key(self, data: Any, prefix: Optional[str] = None) -> str:
        """
        Generate a hash-based cache key from arbitrary data.
        
        Args:
            data: The data to generate a key for
            prefix: Optional prefix for namespacing
            
        Returns:
            A hash-based cache key
        """
        try:
            # Create a stable string representation
            if isinstance(data, dict):
                # Sort dict keys for consistent hashing
                data_str = json.dumps(data, sort_keys=True, default=str)
            elif isinstance(data, BaseModel):
                data_str = data.model_dump_json()
            else:
                data_str = json.dumps(data, default=str, sort_keys=True)
            
            # Generate SHA256 hash
            hash_obj = hashlib.sha256(data_str.encode('utf-8'))
            hash_key = hash_obj.hexdigest()[:16]  # Use first 16 chars
            
            return self._generate_key(hash_key, prefix)
            
        except Exception as e:
            logger.warning(
                "Failed to generate hash key, using string representation",
                extra={"error": str(e)}
            )
            return self._generate_key(str(data), prefix)

    def set(
        self,
        key: str,
        value: T,
        ttl: Optional[int] = None,
        prefix: Optional[str] = None
    ) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None for default)
            prefix: Optional key prefix for namespacing
        """
        with self._lock:
            settings = get_settings()
            
            # Use default TTL if not specified
            if ttl is None:
                ttl = settings.cache.ttl_metadata
            
            full_key = self._generate_key(key, prefix)
            now = datetime.now()
            expires_at = now + timedelta(seconds=ttl)
            
            # Create cache entry
            entry = CacheEntry(
                value=value,
                created_at=now,
                expires_at=expires_at
            )
            
            # Check if we need to evict entries
            if len(self._cache) >= self._max_size and full_key not in self._cache:
                self._evict_lru()
            
            # Store the entry
            self._cache[full_key] = entry
            self._access_order[full_key] = time.time()
            
            # Update stats
            self._stats.entries = len(self._cache)
            self._stats.total_size_bytes += entry.size_bytes
            
            logger.debug(
                "Cached value",
                extra={
                    "key": full_key,
                    "ttl": ttl,
                    "size_bytes": entry.size_bytes,
                    "expires_at": expires_at.isoformat()
                }
            )

    def get(self, key: str, prefix: Optional[str] = None) -> Optional[T]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key
            prefix: Optional key prefix for namespacing
            
        Returns:
            The cached value if found and valid, None otherwise
        """
        with self._lock:
            full_key = self._generate_key(key, prefix)
            entry = self._cache.get(full_key)
            
            if entry is None:
                self._stats.misses += 1
                logger.debug("Cache miss", extra={"key": full_key})
                return None
            
            if entry.is_expired():
                # Remove expired entry
                del self._cache[full_key]
                self._access_order.pop(full_key, None)
                self._stats.misses += 1
                self._stats.expirations += 1
                self._stats.entries = len(self._cache)
                self._stats.total_size_bytes -= entry.size_bytes
                
                logger.debug("Cache entry expired", extra={"key": full_key})
                return None
            
            # Update access information
            try:
                value = entry.access()
                self._access_order[full_key] = time.time()
                self._stats.hits += 1
                
                logger.debug(
                    "Cache hit",
                    extra={
                        "key": full_key,
                        "access_count": entry.access_count,
                        "time_to_expire": entry.time_to_expire().total_seconds()
                    }
                )
                return value
                
            except ValueError:
                # Entry expired between checks
                del self._cache[full_key]
                self._access_order.pop(full_key, None)
                self._stats.misses += 1
                self._stats.expirations += 1
                self._stats.entries = len(self._cache)
                self._stats.total_size_bytes -= entry.size_bytes
                return None

    def delete(self, key: str, prefix: Optional[str] = None) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key
            prefix: Optional key prefix for namespacing
            
        Returns:
            True if the key was found and deleted, False otherwise
        """
        with self._lock:
            full_key = self._generate_key(key, prefix)
            entry = self._cache.pop(full_key, None)
            
            if entry is not None:
                self._access_order.pop(full_key, None)
                self._stats.entries = len(self._cache)
                self._stats.total_size_bytes -= entry.size_bytes
                
                logger.debug("Deleted cache entry", extra={"key": full_key})
                return True
            
            return False

    def exists(self, key: str, prefix: Optional[str] = None) -> bool:
        """
        Check if a key exists and is valid in the cache.
        
        Args:
            key: Cache key
            prefix: Optional key prefix for namespacing
            
        Returns:
            True if the key exists and is valid, False otherwise
        """
        with self._lock:
            full_key = self._generate_key(key, prefix)
            entry = self._cache.get(full_key)
            
            if entry is None:
                return False
            
            if entry.is_expired():
                # Clean up expired entry
                del self._cache[full_key]
                self._access_order.pop(full_key, None)
                self._stats.expirations += 1
                self._stats.entries = len(self._cache)
                self._stats.total_size_bytes -= entry.size_bytes
                return False
            
            return True

    def clear(self, prefix: Optional[str] = None) -> int:
        """
        Clear cache entries, optionally by prefix.
        
        Args:
            prefix: Optional prefix to filter entries to clear
            
        Returns:
            Number of entries cleared
        """
        with self._lock:
            if prefix is None:
                # Clear everything
                count = len(self._cache)
                self._cache.clear()
                self._access_order.clear()
                self._stats.entries = 0
                self._stats.total_size_bytes = 0
                
                logger.info("Cleared all cache entries", extra={"count": count})
                return count
            else:
                # Clear entries with specific prefix
                prefix_key = f"{prefix}:"
                keys_to_delete = [
                    key for key in self._cache.keys()
                    if key.startswith(prefix_key)
                ]
                
                count = 0
                for key in keys_to_delete:
                    entry = self._cache.pop(key)
                    self._access_order.pop(key, None)
                    self._stats.total_size_bytes -= entry.size_bytes
                    count += 1
                
                self._stats.entries = len(self._cache)
                
                logger.info(
                    "Cleared cache entries by prefix",
                    extra={"prefix": prefix, "count": count}
                )
                return count

    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from the cache.
        
        Returns:
            Number of expired entries removed
        """
        with self._lock:
            expired_keys = []
            
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            count = 0
            for key in expired_keys:
                entry = self._cache.pop(key)
                self._access_order.pop(key, None)
                self._stats.total_size_bytes -= entry.size_bytes
                count += 1
            
            self._stats.expirations += count
            self._stats.entries = len(self._cache)
            
            if count > 0:
                logger.debug(
                    "Cleaned up expired entries",
                    extra={"expired_count": count}
                )
            
            return count

    def _evict_lru(self) -> None:
        """Evict the least recently used entry."""
        if not self._access_order:
            return
        
        # Find the least recently used key
        lru_key = min(self._access_order.keys(), key=lambda k: self._access_order[k])
        
        # Remove the entry
        entry = self._cache.pop(lru_key)
        self._access_order.pop(lru_key)
        self._stats.total_size_bytes -= entry.size_bytes
        self._stats.evictions += 1
        
        logger.debug("Evicted LRU cache entry", extra={"key": lru_key})

    def get_stats(self) -> CacheStats:
        """
        Get current cache statistics.
        
        Returns:
            Current cache statistics
        """
        with self._lock:
            # Calculate average TTL of current entries
            if self._cache:
                total_ttl = sum(
                    entry.time_to_expire().total_seconds()
                    for entry in self._cache.values()
                )
                avg_ttl = total_ttl / len(self._cache)
            else:
                avg_ttl = 0.0
            
            # Update dynamic stats
            self._stats.entries = len(self._cache)
            self._stats.average_ttl = avg_ttl
            
            return self._stats

    def get_keys(self, prefix: Optional[str] = None) -> Set[str]:
        """
        Get all cache keys, optionally filtered by prefix.
        
        Args:
            prefix: Optional prefix to filter keys
            
        Returns:
            Set of cache keys
        """
        with self._lock:
            if prefix is None:
                return set(self._cache.keys())
            else:
                prefix_key = f"{prefix}:"
                return {
                    key for key in self._cache.keys()
                    if key.startswith(prefix_key)
                }

    def get_size_bytes(self) -> int:
        """
        Get the total estimated size of the cache in bytes.
        
        Returns:
            Total size in bytes
        """
        with self._lock:
            return self._stats.total_size_bytes

    def __len__(self) -> int:
        """Get the number of entries in the cache."""
        return len(self._cache)

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the cache."""
        return self.exists(key)

    def __del__(self):
        """Cleanup when the cache is destroyed."""
        if hasattr(self, '_cleanup_task') and self._cleanup_task:
            self._stop_cleanup.set()


# Global cache instance
_cache_instance: Optional[MemoryCache] = None
_cache_lock = threading.Lock()


def get_cache() -> MemoryCache:
    """
    Get the global cache instance (singleton pattern).
    
    Returns:
        The global MemoryCache instance
    """
    global _cache_instance
    
    if _cache_instance is None:
        with _cache_lock:
            if _cache_instance is None:
                _cache_instance = MemoryCache()
                logger.info("Created global cache instance")
    
    return _cache_instance


async def initialize_cache() -> MemoryCache:
    """
    Initialize the global cache and start cleanup tasks.
    
    Returns:
        The initialized cache instance
    """
    cache = get_cache()
    await cache.start_cleanup_task()
    logger.info("Initialized cache with cleanup task")
    return cache


async def shutdown_cache():
    """Shutdown the global cache and cleanup tasks."""
    global _cache_instance
    
    if _cache_instance is not None:
        await _cache_instance.stop_cleanup_task()
        _cache_instance = None
        logger.info("Shutdown cache") 