"""
CodeAcademy Pro — Audit Logger (legacy wrapper)
Provides a thin wrapper around AuditService for backwards compatibility.
New code should prefer AuditService directly.
"""

from uuid import UUID

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.audit_service import AuditService

# Re-export action set for reference
AUDIT_ACTIONS = {
    "login_success",
    "login_failed",
    "logout",
    "user_created",
    "user_updated",
    "user_blocked",
    "user_unblocked",
    "user_activated",
    "user_deleted",
    "role_changed",
    "course_created",
    "course_updated",
    "course_deleted",
    "course_published",
    "course_unpublished",
    "teacher_assigned",
    "teacher_removed",
    "payment_approved",
    "payment_rejected",
    "payment_updated",
    "enrollment_created",
    "enrollment_updated",
    "certificate_issued",
}


async def log_audit(
    db: AsyncSession,
    *,
    user_id: UUID | None = None,
    action: str,
    entity_type: str | None = None,
    entity_id: UUID | None = None,
    details: dict | None = None,
    request: Request | None = None,
) -> None:
    """
    Legacy compatibility helper. Records an audit log entry.
    ``user_id`` is mapped to ``actor_user_id``; no email is available here.
    For full features (actor_email, entity_label, safe IP extraction) use
    AuditService.log_action() directly.
    """
    from app.repositories.user_repository import UserRepository

    user = None
    if user_id:
        repo = UserRepository(db)
        user = await repo.get_by_id_lite(user_id)

    svc = AuditService(db)
    await svc.log_action(
        actor_user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        request=request,
        metadata=details,
    )
