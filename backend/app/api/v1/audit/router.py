"""
CodeAcademy Pro — Audit Logs Router (real)
Admin-only endpoint for querying system audit records.
"""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.rls import get_rls_db
from app.middlewares.rbac import require_admin
from app.schemas.audit import AuditLogListResponse
from app.services.audit_service import AuditService

router = APIRouter()


@router.get("", response_model=AuditLogListResponse, dependencies=[Depends(require_admin)])
async def get_audit_logs(
    actor_email: str | None = Query(None, description="Filter by actor email"),
    action: str | None = Query(None, description="Filter by action code"),
    entity_type: str | None = Query(None, description="Filter by entity type"),
    entity_id: UUID | None = Query(None, description="Filter by entity ID"),
    date_from: datetime | None = Query(None, description="ISO datetime from"),
    date_to: datetime | None = Query(None, description="ISO datetime to"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_rls_db),
):
    """Get paginated audit logs (admin only)."""
    svc = AuditService(db)
    result = await svc.list_logs(
        actor_email=actor_email,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
    )
    return AuditLogListResponse.model_validate(result)
