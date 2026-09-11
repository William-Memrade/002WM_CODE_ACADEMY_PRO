"""
CodeAcademy Pro — Audit Repository
Data access for audit_logs with filter support.
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func, and_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit import AuditLog


class AuditRepository:
    """Repository for audit log queries."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_with_filters(
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
    ) -> tuple[list[AuditLog], int]:
        """Return paginated audit logs matching the given filters."""
        skip = (page - 1) * per_page

        filters = []

        if actor_email:
            filters.append(AuditLog.actor_email.ilike(f"%{actor_email}%"))
        if action:
            filters.append(AuditLog.action == action)
        if entity_type:
            filters.append(AuditLog.entity_type == entity_type)
        if entity_id:
            filters.append(AuditLog.entity_id == entity_id)
        if date_from:
            filters.append(AuditLog.created_at >= date_from)
        if date_to:
            filters.append(AuditLog.created_at <= date_to)

        where_clause = and_(*filters) if filters else True

        count_query = select(func.count()).select_from(AuditLog).where(where_clause)
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            select(AuditLog)
            .where(where_clause)
            .order_by(desc(AuditLog.created_at))
            .offset(skip)
            .limit(per_page)
        )
        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def create(self, log: AuditLog) -> AuditLog:
        """Insert a new audit log entry."""
        self.db.add(log)
        await self.db.flush()
        await self.db.refresh(log)
        return log
