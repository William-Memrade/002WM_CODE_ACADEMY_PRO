"""
CodeAcademy Pro — Base Repository
Generic repository pattern for CRUD operations.
"""

from uuid import UUID
from typing import TypeVar, Generic, Type

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """
    Generic CRUD repository.

    Usage:
        class CourseRepository(BaseRepository[Course]):
            def __init__(self, db: AsyncSession):
                super().__init__(Course, db)
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get_by_id(self, id: UUID) -> ModelType | None:
        """Get a single record by ID."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[ModelType]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
            .order_by(self.model.created_at.desc())
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """Count total records."""
        result = await self.db.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar() or 0

    async def create(self, obj: ModelType) -> ModelType:
        """Insert a new record."""
        self.db.add(obj)
        await self.db.flush()
        await self.db.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing record."""
        await self.db.flush()
        return obj

    async def delete(self, id: UUID) -> bool:
        """Hard delete a record by ID."""
        obj = await self.get_by_id(id)
        if obj:
            await self.db.delete(obj)
            await self.db.flush()
            return True
        return False

    async def soft_delete(self, id: UUID) -> bool:
        """Soft delete (set deleted_at) if model supports it."""
        from datetime import datetime, timezone

        obj = await self.get_by_id(id)
        if obj and hasattr(obj, "deleted_at"):
            obj.deleted_at = datetime.now(timezone.utc)
            await self.db.flush()
            return True
        return False
