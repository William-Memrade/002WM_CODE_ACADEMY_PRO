"""
CodeAcademy Pro — Audit Schemas
Pydantic models for audit log responses.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    """Single audit log entry response."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    actor_user_id: UUID | None
    actor_email: str | None
    action: str
    entity_type: str | None
    entity_id: UUID | None
    entity_label: str | None
    ip_address: str | None
    user_agent: str | None
    metadata: dict | None


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""
    items: list[AuditLogResponse]
    total: int
    page: int
    per_page: int
    pages: int
