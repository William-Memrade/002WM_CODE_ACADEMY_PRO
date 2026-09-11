"""
CodeAcademy Pro — Feature Flag Dependency
FastAPI dependencies for gating endpoints behind feature flags.
Falls back to database when Redis is unavailable.
"""

from fastapi import Depends, HTTPException

from app.db.session import get_db
from app.core.redis_client import get_redis_client
from app.services.feature_flags import FeatureFlagService


async def require_feature_flag(flag_key: str):
    """Return a FastAPI dependency that blocks access when a feature flag is disabled."""
    async def _check(
        db=Depends(get_db),
    ):
        redis_client = await get_redis_client()
        try:
            service = FeatureFlagService(db, redis_client)
            enabled = await service.is_enabled(flag_key)
        finally:
            await redis_client.close()

        if not enabled:
            raise HTTPException(
                status_code=403,
                detail=f"Feature '{flag_key}' is not enabled",
            )
    return _check