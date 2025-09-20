"""
Caching utilities for validation operations.

Provides TTL-based caching for expensive operations like network requests.
"""

import time
from typing import Any


class TTLCache:
    """
    Time-to-live cache for validation results.

    Stores values with expiration timestamps to avoid redundant
    expensive operations within a time window.
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize TTL cache.

        Args:
            ttl_seconds: Time to live in seconds (default: 1 hour)
        """
        self.cache: dict[str, tuple[Any, float]] = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Any | None:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value if exists and not expired, None otherwise
        """
        if key in self.cache:
            value, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return value
            # Remove expired entry
            del self.cache[key]
        return None

    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache with current timestamp.

        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = (value, time.time())

    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [key for key, (_, timestamp) in self.cache.items() if current_time - timestamp >= self.ttl]

        for key in expired_keys:
            del self.cache[key]

        return len(expired_keys)


# Global cache instance for external URL validation
# Using 30 minutes TTL to balance freshness with performance
EXTERNAL_LINK_CACHE = TTLCache(ttl_seconds=1800)
