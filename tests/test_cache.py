"""
Tests for the cache layer implementation.

Tests memory cache functionality, decorators, and cache manager.
"""

import asyncio
import pytest
import time
from datetime import datetime, timedelta
from unittest.mock import patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ergo_price_mcp.cache import (
    CacheEntry,
    CacheManager,
    CacheStats,
    MemoryCache,
    cache_metadata,
    cache_price_data,
    cached,
    get_cache,
    get_cache_manager,
    initialize_cache,
    shutdown_cache,
)


class TestCacheEntry:
    """Tests for CacheEntry class."""
    
    def test_cache_entry_creation(self):
        """Test cache entry creation and basic properties."""
        value = {"test": "data"}
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=60)
        
        entry = CacheEntry(
            value=value,
            created_at=created_at,
            expires_at=expires_at
        )
        
        assert entry.value == value
        assert entry.created_at == created_at
        assert entry.expires_at == expires_at
        assert entry.access_count == 0
        assert entry.last_accessed is None
        assert entry.size_bytes > 0
    
    def test_cache_entry_expiration(self):
        """Test cache entry expiration logic."""
        value = "test"
        created_at = datetime.now()
        expires_at = created_at - timedelta(seconds=1)  # Already expired
        
        entry = CacheEntry(
            value=value,
            created_at=created_at,
            expires_at=expires_at
        )
        
        assert entry.is_expired() is True
        assert entry.is_valid() is False
        
        # Test future expiration
        entry.expires_at = datetime.now() + timedelta(seconds=60)
        assert entry.is_expired() is False
        assert entry.is_valid() is True
    
    def test_cache_entry_access(self):
        """Test cache entry access tracking."""
        value = "test"
        created_at = datetime.now()
        expires_at = created_at + timedelta(seconds=60)
        
        entry = CacheEntry(
            value=value,
            created_at=created_at,
            expires_at=expires_at
        )
        
        # First access
        result = entry.access()
        assert result == value
        assert entry.access_count == 1
        assert entry.last_accessed is not None
        
        # Second access
        entry.access()
        assert entry.access_count == 2
    
    def test_cache_entry_access_expired(self):
        """Test accessing expired cache entry."""
        value = "test"
        created_at = datetime.now()
        expires_at = created_at - timedelta(seconds=1)  # Already expired
        
        entry = CacheEntry(
            value=value,
            created_at=created_at,
            expires_at=expires_at
        )
        
        with pytest.raises(ValueError, match="Cache entry has expired"):
            entry.access()
    
    def test_cache_entry_size_estimation(self):
        """Test size estimation for different value types."""
        # String
        entry_str = CacheEntry(
            value="hello",
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        assert entry_str.size_bytes == 5  # len("hello")
        
        # Number
        entry_int = CacheEntry(
            value=42,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        assert entry_int.size_bytes == 8  # Rough estimate for int
        
        # List
        entry_list = CacheEntry(
            value=[1, 2, 3],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=60)
        )
        assert entry_list.size_bytes > 0


class TestMemoryCache:
    """Tests for MemoryCache class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.cache = MemoryCache(max_size=10, cleanup_interval=1)
    
    def teardown_method(self):
        """Cleanup after each test method."""
        if hasattr(self, 'cache'):
            self.cache.clear()
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations."""
        key = "test_key"
        value = {"data": "test"}
        
        # Set value
        self.cache.set(key, value, ttl=60)
        
        # Get value
        result = self.cache.get(key)
        assert result == value
        
        # Check cache stats
        stats = self.cache.get_stats()
        assert stats.hits == 1
        assert stats.misses == 0
        assert stats.entries == 1
    
    def test_cache_miss(self):
        """Test cache miss behavior."""
        result = self.cache.get("nonexistent_key")
        assert result is None
        
        stats = self.cache.get_stats()
        assert stats.hits == 0
        assert stats.misses == 1
    
    def test_cache_expiration(self):
        """Test cache entry expiration."""
        key = "test_key"
        value = "test_value"
        
        # Set with very short TTL
        self.cache.set(key, value, ttl=1)
        
        # Should be available immediately
        result = self.cache.get(key)
        assert result == value
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Should be expired now
        result = self.cache.get(key)
        assert result is None
        
        stats = self.cache.get_stats()
        assert stats.expirations >= 1
    
    def test_cache_with_prefix(self):
        """Test cache operations with key prefixes."""
        key = "test_key"
        value1 = "value1"
        value2 = "value2"
        
        # Set values with different prefixes
        self.cache.set(key, value1, prefix="prefix1")
        self.cache.set(key, value2, prefix="prefix2")
        
        # Get values
        result1 = self.cache.get(key, prefix="prefix1")
        result2 = self.cache.get(key, prefix="prefix2")
        
        assert result1 == value1
        assert result2 == value2
        assert result1 != result2
    
    def test_cache_delete(self):
        """Test cache deletion."""
        key = "test_key"
        value = "test_value"
        
        self.cache.set(key, value)
        assert self.cache.get(key) == value
        
        # Delete the entry
        deleted = self.cache.delete(key)
        assert deleted is True
        
        # Should be gone now
        assert self.cache.get(key) is None
        
        # Deleting again should return False
        deleted = self.cache.delete(key)
        assert deleted is False
    
    def test_cache_exists(self):
        """Test cache existence checking."""
        key = "test_key"
        value = "test_value"
        
        # Should not exist initially
        assert self.cache.exists(key) is False
        
        # Set value
        self.cache.set(key, value, ttl=60)
        assert self.cache.exists(key) is True
        
        # Should not exist after expiration
        self.cache.set(key, value, ttl=1)
        time.sleep(1.1)
        assert self.cache.exists(key) is False
    
    def test_cache_clear(self):
        """Test cache clearing."""
        # Add some entries
        self.cache.set("key1", "value1")
        self.cache.set("key2", "value2", prefix="prefix")
        self.cache.set("key3", "value3", prefix="prefix")
        
        assert len(self.cache) == 3
        
        # Clear by prefix
        cleared = self.cache.clear(prefix="prefix")
        assert cleared == 2
        assert len(self.cache) == 1
        
        # Clear all
        cleared = self.cache.clear()
        assert cleared == 1
        assert len(self.cache) == 0
    
    def test_cache_cleanup_expired(self):
        """Test manual cleanup of expired entries."""
        # Add entries with different TTLs
        self.cache.set("key1", "value1", ttl=60)  # Long TTL
        self.cache.set("key2", "value2", ttl=1)   # Short TTL
        self.cache.set("key3", "value3", ttl=1)   # Short TTL
        
        assert len(self.cache) == 3
        
        # Wait for some to expire
        time.sleep(1.1)
        
        # Manual cleanup
        expired_count = self.cache.cleanup_expired()
        assert expired_count == 2
        assert len(self.cache) == 1
    
    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        # Fill cache to capacity
        for i in range(10):
            self.cache.set(f"key{i}", f"value{i}")
        
        assert len(self.cache) == 10
        
        # Access some entries to affect LRU order
        self.cache.get("key0")  # Make key0 recently used
        self.cache.get("key5")  # Make key5 recently used
        
        # Add one more entry (should evict LRU)
        self.cache.set("new_key", "new_value")
        
        assert len(self.cache) == 10  # Still at max capacity
        
        # key0 and key5 should still be there (recently accessed)
        assert self.cache.get("key0") == "value0"
        assert self.cache.get("key5") == "value5"
        
        # new_key should be there
        assert self.cache.get("new_key") == "new_value"
        
        stats = self.cache.get_stats()
        assert stats.evictions >= 1


class TestCacheDecorators:
    """Tests for cache decorators."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Clear cache before each test
        cache = get_cache()
        cache.clear()
    
    def test_cached_decorator_sync(self):
        """Test cached decorator with synchronous function."""
        call_count = 0
        
        @cached(ttl=60, prefix="test")
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y
        
        # First call
        result1 = expensive_function(1, 2)
        assert result1 == 3
        assert call_count == 1
        
        # Second call (should use cache)
        result2 = expensive_function(1, 2)
        assert result2 == 3
        assert call_count == 1  # Function not called again
        
        # Different arguments (should call function)
        result3 = expensive_function(2, 3)
        assert result3 == 5
        assert call_count == 2
    
    @pytest.mark.asyncio
    async def test_cached_decorator_async(self):
        """Test cached decorator with asynchronous function."""
        call_count = 0
        
        @cached(ttl=60, prefix="test")
        async def expensive_async_function(x, y):
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.001)  # Simulate async work
            return x * y
        
        # First call
        result1 = await expensive_async_function(2, 3)
        assert result1 == 6
        assert call_count == 1
        
        # Second call (should use cache)
        result2 = await expensive_async_function(2, 3)
        assert result2 == 6
        assert call_count == 1  # Function not called again
    
    def test_cache_price_data_decorator(self):
        """Test price data caching decorator."""
        call_count = 0
        
        @cache_price_data()
        def get_token_price(token_id):
            nonlocal call_count
            call_count += 1
            return {"price": 100.0, "token_id": token_id}
        
        # First call
        result1 = get_token_price("token123")
        assert result1["price"] == 100.0
        assert call_count == 1
        
        # Second call (should use cache)
        result2 = get_token_price("token123")
        assert result2["price"] == 100.0
        assert call_count == 1
    
    def test_cache_metadata_decorator(self):
        """Test metadata caching decorator."""
        call_count = 0
        
        @cache_metadata()
        def get_token_info(token_id):
            nonlocal call_count
            call_count += 1
            return {"name": "Test Token", "symbol": "TEST", "token_id": token_id}
        
        # First call
        result1 = get_token_info("token123")
        assert result1["name"] == "Test Token"
        assert call_count == 1
        
        # Second call (should use cache)
        result2 = get_token_info("token123")
        assert result2["name"] == "Test Token"
        assert call_count == 1


class TestCacheManager:
    """Tests for CacheManager class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.manager = CacheManager()
        self.manager.clear_all_data()
    
    def test_token_price_caching(self):
        """Test token price caching and retrieval."""
        token_id = "token123"
        price_data = {"price": 50.0, "volume": 1000.0}
        
        # Cache price data
        self.manager.cache_token_price(token_id, price_data)
        
        # Retrieve price data
        result = self.manager.get_token_price(token_id)
        assert result == price_data
    
    def test_token_metadata_caching(self):
        """Test token metadata caching and retrieval."""
        token_id = "token123"
        metadata = {"name": "Test Token", "symbol": "TEST", "decimals": 8}
        
        # Cache metadata
        self.manager.cache_token_metadata(token_id, metadata)
        
        # Retrieve metadata
        result = self.manager.get_token_metadata(token_id)
        assert result == metadata
    
    def test_historical_data_caching(self):
        """Test historical data caching and retrieval."""
        key = "erg_price_7d"
        data = [{"date": "2023-01-01", "price": 2.5}]
        
        # Cache historical data
        self.manager.cache_historical_data(key, data)
        
        # Retrieve historical data
        result = self.manager.get_historical_data(key)
        assert result == data
    
    def test_invalidate_token_data(self):
        """Test invalidating all data for a token."""
        token_id = "token123"
        
        # Cache different types of data for the token
        self.manager.cache_token_price(token_id, {"price": 50.0})
        self.manager.cache_token_metadata(token_id, {"name": "Test Token"})
        
        # Verify data is cached
        assert self.manager.get_token_price(token_id) is not None
        assert self.manager.get_token_metadata(token_id) is not None
        
        # Invalidate all data for the token
        self.manager.invalidate_token_data(token_id)
        
        # Verify data is gone
        assert self.manager.get_token_price(token_id) is None
        assert self.manager.get_token_metadata(token_id) is None
    
    def test_clear_by_type(self):
        """Test clearing cache by data type."""
        # Cache different types of data
        self.manager.cache_token_price("token1", {"price": 50.0})
        self.manager.cache_token_price("token2", {"price": 60.0})
        self.manager.cache_token_metadata("token1", {"name": "Token 1"})
        
        # Clear only price data
        cleared = self.manager.clear_by_type("price")
        assert cleared == 2
        
        # Metadata should still be there
        assert self.manager.get_token_metadata("token1") is not None
        assert self.manager.get_token_price("token1") is None
    
    def test_cache_stats(self):
        """Test cache statistics retrieval."""
        # Add some data to generate stats
        self.manager.cache_token_price("token1", {"price": 50.0})
        self.manager.get_token_price("token1")  # Generate a hit
        self.manager.get_token_price("nonexistent")  # Generate a miss
        
        stats = self.manager.get_cache_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "hit_rate" in stats
        assert "entries" in stats
        assert stats["hits"] >= 1
        assert stats["misses"] >= 1


@pytest.mark.asyncio
async def test_cache_initialization():
    """Test cache initialization and shutdown."""
    # Initialize cache
    cache = await initialize_cache()
    assert cache is not None
    
    # Verify cleanup task is running
    assert cache._cleanup_task is not None
    assert not cache._cleanup_task.done()
    
    # Shutdown cache
    await shutdown_cache()


def test_global_cache_singleton():
    """Test that get_cache returns the same instance."""
    cache1 = get_cache()
    cache2 = get_cache()
    
    assert cache1 is cache2


def test_global_cache_manager_singleton():
    """Test that get_cache_manager returns the same instance."""
    manager1 = get_cache_manager()
    manager2 = get_cache_manager()
    
    assert manager1 is manager2 