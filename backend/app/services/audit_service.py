"""
CodeAcademy Pro — Audit Service
Centralised, safe audit logging with IP / UA extraction.
Uses a separate database session to avoid poisoning the primary transaction.
"""

from uuid import UUID
from datetime import datetime

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.models.audit import AuditLog
from app.models.user import User
from app.db.session import async_session
from app.repositories.audit_repository import AuditRepository

logger = structlog.get_logger()


class AuditService:
    """Business logic for audit logging. Uses the caller's session for reads,
    but writes audit entries to a separate session so failures don't poison
    the primary transaction."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuditRepository(db)

    @staticmethod
    def _extract_ip(request: Request | None) -> str | None:
        """Extract real client IP safely."""
        if not request:
            return None
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()[:45]
        if request.client:
            return str(request.client.host)[:45]
        return None

    @staticmethod
    def _extract_user_agent(request: Request | None) -> str | None:
        """Extract user-agent header safely."""
        if not request:
            return None
        ua = request.headers.get("user-agent", "")
        return ua[:500] if ua else None

    async def log_action(
        self,
        *,
        actor_user: User | dict | None = None,
        action: str,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        entity_label: str | None = None,
        request: Request | None = None,
        metadata: dict | None = None,
    ) -> None:
        """
        Fire-and-forget audit log creation. Uses a separate database session
        so that any audit error (constraint violation, table missing, etc.)
        does NOT poison the caller's transaction.
        """
        try:
            actor_id = None
            actor_email = None
            if actor_user is not None:
                if isinstance(actor_user, dict):
                    actor_id = actor_user.get("id")
                    actor_email = actor_user.get("email")
                else:
                    actor_id = actor_user.id
                    actor_email = actor_user.email

            ip_address = self._extract_ip(request)
            user_agent = self._extract_user_agent(request)

            log = AuditLog(
                actor_user_id=actor_id,
                actor_email=actor_email,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                entity_label=entity_label,
                ip_address=ip_address,
                user_agent=user_agent,
                details=metadata or {},
            )

            async with async_session() as audit_session:
                audit_session.add(log)
                await audit_session.commit()
        except Exception as exc:
            actor_id_str = None
            if actor_user is not None:
                if isinstance(actor_user, dict):
                    actor_id_str = str(actor_user.get("id"))
                else:
                    actor_id_str = str(actor_user.id)
            logger.warning(
                "audit_log_failed",
                action=action,
                error=str(exc),
                actor_id=actor_id_str,
            )

    async def list_logs(
        self,
        *,
        actor_email: str | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        page: int = 1,
        per_page: int = 50,
    ) -> dict:
        """Return paginated, filtered audit logs."""
        logs, total = await self.repo.list_with_filters(
            actor_email=actor_email,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            date_from=date_from,
            date_to=date_to,
            page=page,
            per_page=per_page,
        )
        pages = max(1, (total + per_page - 1) // per_page) if total > 0 else 1

        items = []
        for log in logs:
            items.append(
                {
                    "id": str(log.id),
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                    "actor_user_id": str(log.actor_user_id) if log.actor_user_id else None,
                    "actor_email": log.actor_email,
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": str(log.entity_id) if log.entity_id else None,
                    "entity_label": log.entity_label,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "metadata": log.details or {},
                }
            )

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }
