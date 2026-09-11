"""
CodeAcademy Pro — Content Versioning Service
Automatic JSONB snapshots of educational content on updates.
"""

from uuid import UUID

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = structlog.get_logger()


class ContentVersioningService:
    """Saves version snapshots of courses, modules, and lessons."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_version(
        self,
        entity_type: str,
        entity_id: UUID,
        snapshot: dict,
        changed_by: UUID,
        change_summary: str | None = None,
    ) -> None:
        """
        Save a version snapshot before updating an entity.

        Args:
            entity_type: 'course', 'module', or 'lesson'
            entity_id: UUID of the entity
            snapshot: Full JSON representation of the entity state
            changed_by: UUID of the user making the change
            change_summary: Optional description of what changed
        """
        from app.models.system import ContentVersion

        # Get next version number
        result = await self.db.execute(
            select(func.coalesce(func.max(ContentVersion.version_number), 0))
            .where(ContentVersion.entity_type == entity_type)
            .where(ContentVersion.entity_id == entity_id)
        )
        current_max = result.scalar()
        next_version = current_max + 1

        version = ContentVersion(
            entity_type=entity_type,
            entity_id=entity_id,
            version_number=next_version,
            snapshot=snapshot,
            changed_by=changed_by,
            change_summary=change_summary,
        )
        self.db.add(version)
        await self.db.flush()

        logger.info(
            "content_version_saved",
            entity_type=entity_type,
            entity_id=str(entity_id),
            version=next_version,
        )

    async def get_history(
        self,
        entity_type: str,
        entity_id: UUID,
        limit: int = 20,
    ) -> list[dict]:
        """Get version history for an entity."""
        from app.models.system import ContentVersion

        result = await self.db.execute(
            select(ContentVersion)
            .where(ContentVersion.entity_type == entity_type)
            .where(ContentVersion.entity_id == entity_id)
            .order_by(ContentVersion.version_number.desc())
            .limit(limit)
        )
        versions = result.scalars().all()
        return [
            {
                "id": str(v.id),
                "version_number": v.version_number,
                "change_summary": v.change_summary,
                "changed_by": str(v.changed_by),
                "created_at": v.created_at.isoformat(),
            }
            for v in versions
        ]

    async def get_version(
        self,
        entity_type: str,
        entity_id: UUID,
        version_number: int,
    ) -> dict | None:
        """Get a specific version snapshot."""
        from app.models.system import ContentVersion

        result = await self.db.execute(
            select(ContentVersion)
            .where(ContentVersion.entity_type == entity_type)
            .where(ContentVersion.entity_id == entity_id)
            .where(ContentVersion.version_number == version_number)
        )
        version = result.scalar_one_or_none()
        if version:
            return {
                "id": str(version.id),
                "version_number": version.version_number,
                "snapshot": version.snapshot,
                "change_summary": version.change_summary,
                "changed_by": str(version.changed_by),
                "created_at": version.created_at.isoformat(),
            }
        return None
