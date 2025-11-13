"""
Cache management for expensive operations
Implements file-based and memory caching with TTL
"""
import hashlib
import json
import pickle
import time
from pathlib import Path
from typing import Any, Optional, Callable
from datetime import datetime, timedelta
from functools import wraps

from config.settings import CACHE_DIR, CACHE_TTL, CACHE_MAX_SIZE
from utils.logger import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Manages caching of analysis results and processed data"""

    def __init__(self, cache_dir: Path = CACHE_DIR, ttl: int = CACHE_TTL, max_size: int = CACHE_MAX_SIZE):
        """
        Initialize cache manager

        Args:
            cache_dir: Directory for cache files
            ttl: Time-to-live in seconds
            max_size: Maximum number of cached items
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        self.max_size = max_size
        self.memory_cache = {}
        self.cache_metadata = self._load_metadata()

        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)
        logger.info(f"Cache manager initialized: dir={cache_dir}, ttl={ttl}s, max_size={max_size}")

    def _load_metadata(self) -> dict:
        """Load cache metadata from disk"""
        metadata_file = self.cache_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache metadata: {e}")
        return {}

    def _save_metadata(self):
        """Save cache metadata to disk"""
        metadata_file = self.cache_dir / "metadata.json"
        try:
            with open(metadata_file, 'w') as f:
                json.dump(self.cache_metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache metadata: {e}")

    def _generate_key(self, *args, **kwargs) -> str:
        """
        Generate cache key from arguments

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Hash key for cache
        """
        key_data = {
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _is_expired(self, cache_key: str) -> bool:
        """
        Check if cache entry is expired

        Args:
            cache_key: Cache key to check

        Returns:
            True if expired, False otherwise
        """
        if cache_key not in self.cache_metadata:
            return True

        metadata = self.cache_metadata[cache_key]
        created_at = datetime.fromisoformat(metadata['created_at'])
        expiry_time = created_at + timedelta(seconds=self.ttl)

        return datetime.now() > expiry_time

    def _cleanup_old_entries(self):
        """Remove expired cache entries"""
        expired_keys = []

        for cache_key in list(self.cache_metadata.keys()):
            if self._is_expired(cache_key):
                expired_keys.append(cache_key)

        for cache_key in expired_keys:
            self.delete(cache_key)

        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

    def _enforce_size_limit(self):
        """Enforce maximum cache size by removing oldest entries"""
        if len(self.cache_metadata) <= self.max_size:
            return

        # Sort by creation time
        sorted_entries = sorted(
            self.cache_metadata.items(),
            key=lambda x: x[1]['created_at']
        )

        # Remove oldest entries
        entries_to_remove = len(sorted_entries) - self.max_size
        for cache_key, _ in sorted_entries[:entries_to_remove]:
            self.delete(cache_key)

        logger.info(f"Removed {entries_to_remove} cache entries to enforce size limit")

    def get(self, cache_key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from cache

        Args:
            cache_key: Cache key
            default: Default value if not found

        Returns:
            Cached value or default
        """
        # Check memory cache first
        if cache_key in self.memory_cache:
            if not self._is_expired(cache_key):
                logger.debug(f"Cache hit (memory): {cache_key}")
                return self.memory_cache[cache_key]

        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists() and not self._is_expired(cache_key):
            try:
                with open(cache_file, 'rb') as f:
                    value = pickle.load(f)
                    self.memory_cache[cache_key] = value  # Populate memory cache
                    logger.debug(f"Cache hit (file): {cache_key}")
                    return value
            except Exception as e:
                logger.error(f"Failed to read cache file {cache_key}: {e}")
                self.delete(cache_key)

        logger.debug(f"Cache miss: {cache_key}")
        return default

    def set(self, cache_key: str, value: Any, metadata: Optional[dict] = None):
        """
        Set value in cache

        Args:
            cache_key: Cache key
            value: Value to cache
            metadata: Additional metadata
        """
        try:
            # Store in memory
            self.memory_cache[cache_key] = value

            # Store in file
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump(value, f)

            # Update metadata
            self.cache_metadata[cache_key] = {
                'created_at': datetime.now().isoformat(),
                'size': cache_file.stat().st_size,
                'metadata': metadata or {}
            }
            self._save_metadata()

            # Cleanup and enforce limits
            self._cleanup_old_entries()
            self._enforce_size_limit()

            logger.debug(f"Cache set: {cache_key}")

        except Exception as e:
            logger.error(f"Failed to set cache for {cache_key}: {e}")

    def delete(self, cache_key: str):
        """
        Delete cache entry

        Args:
            cache_key: Cache key to delete
        """
        # Remove from memory
        self.memory_cache.pop(cache_key, None)

        # Remove file
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"Failed to delete cache file {cache_key}: {e}")

        # Remove metadata
        self.cache_metadata.pop(cache_key, None)
        self._save_metadata()

        logger.debug(f"Cache deleted: {cache_key}")

    def clear(self):
        """Clear all cache entries"""
        # Clear memory cache
        self.memory_cache.clear()

        # Remove all cache files
        for cache_file in self.cache_dir.glob("*.pkl"):
            try:
                cache_file.unlink()
            except Exception as e:
                logger.error(f"Failed to delete {cache_file}: {e}")

        # Clear metadata
        self.cache_metadata.clear()
        self._save_metadata()

        logger.info("Cache cleared")

    def get_stats(self) -> dict:
        """
        Get cache statistics

        Returns:
            Dictionary with cache stats
        """
        total_size = sum(
            (self.cache_dir / f"{key}.pkl").stat().st_size
            for key in self.cache_metadata.keys()
            if (self.cache_dir / f"{key}.pkl").exists()
        )

        return {
            'total_entries': len(self.cache_metadata),
            'memory_entries': len(self.memory_cache),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'max_size': self.max_size,
            'ttl_seconds': self.ttl
        }


# Global cache instance
_cache_manager = CacheManager()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results

    Args:
        ttl: Custom TTL for this cache (uses default if None)
        key_prefix: Prefix for cache key

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = _cache_manager._generate_key(key_prefix + func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_result = _cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            _cache_manager.set(cache_key, result, metadata={'function': func.__name__})

            return result

        # Add cache management methods to function
        wrapper.cache_clear = lambda: _cache_manager.clear()
        wrapper.cache_info = lambda: _cache_manager.get_stats()

        return wrapper
    return decorator


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance"""
    return _cache_manager
