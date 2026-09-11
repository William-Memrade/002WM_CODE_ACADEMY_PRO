"""
CodeAcademy Pro — In-Memory TTL Cache
Simple thread-safe cache for quasi-static data (categories, roles, metrics).
No Redis dependency — pure Python with TTL expiration.
"""

import asyncio
import time
from typing import Any, Callable, Coroutine


class TTLCache:
    """Simple in-memory cache with per-key TTL expiration."""

    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}  # key -> (value, expires_at)
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any | None:
        """Get value if not expired."""
        entry = self._store.get(key)
        if entry is None:
            return None
        value, expires_at = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl_seconds: int = 60) -> None:
        """Set value with TTL."""
        self._store[key] = (value, time.monotonic() + ttl_seconds)

    async def delete(self, key: str) -> None:
        """Remove a key."""
        self._store.pop(key, None)

    async def get_or_set(
        self,
        key: str,
        factory: Callable[[], Coroutine[Any, Any, Any]],
        ttl_seconds: int = 60,
    ) -> Any:
        """Get cached value or compute and cache it."""
        value = await self.get(key)
        if value is not None:
            return value

        async with self._lock:
            # Double-check after acquiring lock
            value = await self.get(key)
            if value is not None:
                return value

            value = await factory()
            await self.set(key, value, ttl_seconds)
            return value

    def invalidate_prefix(self, prefix: str) -> None:
        """Remove all keys starting with prefix."""
        keys_to_remove = [k for k in self._store if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._store[k]

    def clear(self) -> None:
        """Clear all cached data."""
        self._store.clear()


# Global cache instance
cache = TTLCache()
