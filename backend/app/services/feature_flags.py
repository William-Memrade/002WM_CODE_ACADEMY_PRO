"""
CodeAcademy Pro — Feature Flags Service
Database-backed feature flags with Redis caching.
Falls back to database when Redis is unavailable.
"""

import json
from uuid import UUID

import redis.asyncio as redis
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()

CACHE_PREFIX = "ff:"
CACHE_TTL = 60  # seconds


class FeatureFlagService:
    """Feature flag evaluation with Redis cache. Falls back to DB when Redis is down."""

    def __init__(self, db: AsyncSession, redis_client: redis.Redis | None = None):
        self.db = db
        self.redis = redis_client

    async def is_enabled(self, key: str) -> bool:
        """
        Check if a feature flag is enabled.
        Uses Redis cache first, falls back to database.
        Gracefully degrades if Redis is unavailable.
        """
        from app.models.system import FeatureFlag

        if self.redis:
            try:
                cached = await self.redis.get(f"{CACHE_PREFIX}{key}")
                if cached is not None:
                    return cached == "1"
            except (redis.RedisError, redis.ConnectionError, OSError) as exc:
                logger.warning("redis_unavailable_fallback_db", key=key, error=str(exc))

        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        if flag is None:
            logger.warning("feature_flag_not_found", key=key)
            return False

        if self.redis:
            try:
                await self.redis.set(
                    f"{CACHE_PREFIX}{key}",
                    "1" if flag.enabled else "0",
                    ex=CACHE_TTL,
                )
            except (redis.RedisError, redis.ConnectionError, OSError):
                pass

        return flag.enabled

    async def toggle(self, key: str, enabled: bool) -> bool:
        """Toggle a feature flag. Returns True if flag was found and updated."""
        from app.models.system import FeatureFlag
        result = await self.db.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        if not flag:
            return False

        flag.enabled = enabled
        await self.db.flush()

        if self.redis:
            try:
                await self.redis.delete(f"{CACHE_PREFIX}{key}")
            except (redis.RedisError, redis.ConnectionError, OSError):
                pass

        logger.info("feature_flag_toggled", key=key, enabled=enabled)
        return True

    async def get_all(self) -> list[dict]:
        """Get all feature flags."""
        from app.models.system import FeatureFlag
        result = await self.db.execute(select(FeatureFlag))
        flags = result.scalars().all()
        return [
            {
                "id": str(f.id),
                "key": f.key,
                "enabled": f.enabled,
                "description": f.description,
                "flag_metadata": f.flag_metadata,
            }
            for f in flags
        ]

    async def invalidate_cache(self, key: str) -> None:
        """Invalidate cache for a specific flag."""
        if self.redis:
            try:
                await self.redis.delete(f"{CACHE_PREFIX}{key}")
            except (redis.RedisError, redis.ConnectionError, OSError):
                pass
