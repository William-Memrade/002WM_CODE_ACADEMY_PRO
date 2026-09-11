"""
CodeAcademy Pro — Course Repository
Data access for courses, modules, lessons.
"""

from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.course import Course, Module, Lesson, Category
from app.models.user import Teacher
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    """Repository for Course operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Course, db)

    async def get_by_id_full(self, id: UUID) -> Course | None:
        """Get course by ID with ALL relations (for detail view)."""
        result = await self.db.execute(
            select(Course)
            .options(
                selectinload(Course.category),
                selectinload(Course.teacher).selectinload(Teacher.user),
                selectinload(Course.modules).selectinload(Module.lessons),
            )
            .where(Course.id == id)
            .where(Course.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, id: UUID) -> Course | None:
        """Get course by ID with lightweight relations (no modules/lessons)."""
        result = await self.db.execute(
            select(Course)
            .options(
                selectinload(Course.category),
                selectinload(Course.teacher).selectinload(Teacher.user),
            )
            .where(Course.id == id)
            .where(Course.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Course | None:
        """Get course by slug with full relations (detail page)."""
        result = await self.db.execute(
            select(Course)
            .options(
                selectinload(Course.category),
                selectinload(Course.teacher).selectinload(Teacher.user),
                selectinload(Course.modules).selectinload(Module.lessons),
            )
            .where(Course.slug == slug)
            .where(Course.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list_active(
        self,
        category: str | None = None,
        level: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Course], int]:
        """List active courses with filters and pagination. No modules/lessons loaded."""
        base_filter = [Course.is_active == True, Course.deleted_at.is_(None)]

        # Build filters once
        extra_filters = []
        join_category = False
        if category:
            join_category = True
            extra_filters.append(Category.slug == category)
        if level:
            extra_filters.append(Course.level == level)
        if search:
            extra_filters.append(
                or_(
                    Course.title.ilike(f"%{search}%"),
                    Course.short_description.ilike(f"%{search}%"),
                )
            )

        all_filters = base_filter + extra_filters

        # Count query — lightweight, no JOINs for relations
        count_query = select(func.count()).select_from(Course).where(*base_filter)
        if join_category:
            count_query = count_query.join(Category)
        if extra_filters:
            count_query = count_query.where(*extra_filters)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Data query — only category + teacher (NO modules/lessons)
        query = (
            select(Course)
            .options(
                selectinload(Course.category),
                selectinload(Course.teacher).selectinload(Teacher.user),
            )
            .where(*base_filter)
        )
        if join_category:
            query = query.join(Category)
        if extra_filters:
            query = query.where(*extra_filters)

        query = query.order_by(Course.is_featured.desc(), Course.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        courses = list(result.scalars().all())

        return courses, total

    async def list_all_admin(self, skip: int = 0, limit: int = 50) -> tuple[list[Course], int]:
        """List ALL courses for admin (including inactive). No modules/lessons."""
        count_query = select(func.count()).select_from(Course).where(Course.deleted_at.is_(None))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = (
            select(Course)
            .options(
                selectinload(Course.category),
                selectinload(Course.teacher).selectinload(Teacher.user),
            )
            .where(Course.deleted_at.is_(None))
            .order_by(Course.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all()), total


class ModuleRepository(BaseRepository[Module]):
    """Repository for Module operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Module, db)

    async def get_by_course(self, course_id: UUID) -> list[Module]:
        """Get modules for a course, ordered."""
        result = await self.db.execute(
            select(Module)
            .options(selectinload(Module.lessons))
            .where(Module.course_id == course_id)
            .order_by(Module.sort_order)
        )
        return list(result.scalars().all())


class LessonRepository(BaseRepository[Lesson]):
    """Repository for Lesson operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Lesson, db)

    async def get_by_module(self, module_id: UUID) -> list[Lesson]:
        """Get lessons for a module, ordered."""
        result = await self.db.execute(
            select(Lesson)
            .where(Lesson.module_id == module_id)
            .order_by(Lesson.sort_order)
        )
        return list(result.scalars().all())


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_by_slug(self, slug: str) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.slug == slug))
        return result.scalar_one_or_none()

    async def list_active(self) -> list[Category]:
        result = await self.db.execute(
            select(Category).where(Category.is_active == True).order_by(Category.sort_order)
        )
        return list(result.scalars().all())
