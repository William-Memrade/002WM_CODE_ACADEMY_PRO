"""
CodeAcademy Pro — Admin Router
Endpoints for admin-only operations: feature flags, etc.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.rbac import require_admin
from app.schemas.feature_flag import FeatureFlagResponse, FeatureFlagToggleRequest
from app.services.audit_service import AuditService
from app.services.feature_flags import FeatureFlagService
from app.core.redis_client import get_redis_client

router = APIRouter()


@router.get("/feature-flags", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """List all feature flags. Admin only."""
    redis_client = await get_redis_client()
    try:
        service = FeatureFlagService(db, redis_client)
        flags = await service.get_all()
        return [
            FeatureFlagResponse(
                id=f["id"],
                key=f["key"],
                enabled=f["enabled"],
                description=f.get("description"),
            )
            for f in flags
        ]
    finally:
        await redis_client.close()


@router.patch("/feature-flags/{key}")
async def toggle_feature_flag(
    key: str,
    body: FeatureFlagToggleRequest,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Toggle a feature flag. Admin only."""
    redis_client = await get_redis_client()
    try:
        service = FeatureFlagService(db, redis_client)
        updated = await service.toggle(key, body.enabled)

        if not updated:
            raise HTTPException(status_code=404, detail=f"Feature flag '{key}' not found")

        audit = AuditService(db)
        await audit.log_action(
            actor_user=current_user,
            action="feature_flag_toggled",
            entity_type="feature_flag",
            entity_label=key,
            request=request,
            metadata={"key": key, "enabled": body.enabled},
        )

        return {"key": key, "enabled": body.enabled, "message": "Feature flag updated"}
    finally:
        await redis_client.close()
