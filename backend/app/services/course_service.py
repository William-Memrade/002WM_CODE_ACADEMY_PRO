"""
CodeAcademy Pro — Course Service
Business logic for course operations.
"""

import re
import uuid
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select as sa_select, func as sa_func
from app.models.course import Course, Module, Lesson
from app.models.payment import Enrollment
from app.models.system import SystemSetting
from app.repositories.course_repository import (
    CourseRepository,
    ModuleRepository,
    LessonRepository,
    CategoryRepository,
)


def slugify(text: str) -> str:
    """Generate a URL-safe slug from text."""
    text = text.lower().strip()
    text = re.sub(r"[áàäâ]", "a", text)
    text = re.sub(r"[éèëê]", "e", text)
    text = re.sub(r"[íìïî]", "i", text)
    text = re.sub(r"[óòöô]", "o", text)
    text = re.sub(r"[úùüû]", "u", text)
    text = re.sub(r"[ñ]", "n", text)
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


class CourseService:
    """Course business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.module_repo = ModuleRepository(db)
        self.lesson_repo = LessonRepository(db)
        self.category_repo = CategoryRepository(db)

    async def list_courses(
        self,
        category: str | None = None,
        level: str | None = None,
        search: str | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """List active courses with pagination."""
        skip = (page - 1) * per_page
        courses, total = await self.course_repo.list_active(
            category=category, level=level, search=search, skip=skip, limit=per_page
        )
        pages = (total + per_page - 1) // per_page if total > 0 else 0

        items = []
        for c in courses:
            items.append(await self._course_to_list_item(c))
        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    async def get_course_detail(self, slug: str) -> dict | None:
        """Get full course detail by slug."""
        course = await self.course_repo.get_by_slug(slug)
        if not course:
            return None
        return await self._course_to_detail(course)

    async def get_course_by_id(self, course_id: UUID) -> dict | None:
        """Get course by ID (full detail)."""
        course = await self.course_repo.get_by_id_full(course_id)
        if not course:
            return None
        return await self._course_to_detail(course)

    async def create_course(
        self, title: str, description: str, price: float = 0.0, **kwargs
    ) -> dict:
        """Create a new course."""
        slug = slugify(title)
        # Ensure unique slug
        existing = await self.course_repo.get_by_slug(slug)
        if existing:
            suffix = str(uuid.uuid4())[:4]
            slug = f"{slug}-{suffix}"

        if kwargs.get("currency") is None:
            try:
                from app.models.system import SystemSetting
                from sqlalchemy import select as sa_select
                cur_result = await self.db.execute(
                    sa_select(SystemSetting.value).where(SystemSetting.key == "default_currency")
                )
                cur_row = cur_result.scalar_one_or_none()
                kwargs["currency"] = cur_row if cur_row else "USD"
            except Exception:
                kwargs["currency"] = "USD"

        course = Course(
            title=title,
            slug=slug,
            description=description,
            short_description=kwargs.get("short_description"),
            category_id=kwargs.get("category_id"),
            teacher_id=kwargs.get("teacher_id"),
            price=price,
            currency=kwargs.get("currency", "USD"),
            level=kwargs.get("level", "beginner"),
            duration_hours=kwargs.get("duration_hours"),
            duration_months=kwargs.get("duration_months"),
            full_payment_discount_pct=kwargs.get("full_payment_discount_pct") or 0,
            is_featured=kwargs.get("is_featured", False),
        )
        course = await self.course_repo.create(course)
        return {"id": course.id, "slug": course.slug, "title": course.title}

    async def update_course(self, course_id: UUID, **kwargs) -> dict | None:
        """Update a course."""
        from sqlalchemy import select
        from app.models.course import Course as CourseModel

        # Lightweight fetch — no relations needed for the update itself
        result = await self.db.execute(
            select(CourseModel).where(CourseModel.id == course_id, CourseModel.deleted_at.is_(None))
        )
        course = result.scalar_one_or_none()
        if not course:
            return None

        for key, value in kwargs.items():
            if hasattr(course, key):
                # Only allow explicit None for nullable DB columns
                nullable_fields = {
                    "short_description", "thumbnail_url", "category_id",
                    "teacher_id", "duration_hours", "max_students",
                }
                if value is not None or key in nullable_fields:
                    setattr(course, key, value)

        if "title" in kwargs and kwargs["title"]:
            course.slug = slugify(kwargs["title"])

        await self.course_repo.update(course)

        # Reload with full relations for the response (modules + lessons)
        course = await self.course_repo.get_by_id_full(course_id)
        return await self._course_to_detail(course) if course else None

    async def toggle_active(self, course_id: UUID, active: bool) -> dict | None:
        """Activate/deactivate a course."""
        from sqlalchemy import select
        from app.models.course import Course as CourseModel

        # Lightweight fetch — no relations needed
        result = await self.db.execute(
            select(CourseModel).where(CourseModel.id == course_id, CourseModel.deleted_at.is_(None))
        )
        course = result.scalar_one_or_none()
        if not course:
            return None
        course.is_active = active
        await self.course_repo.update(course)
        return {"id": course.id, "is_active": course.is_active}

    async def delete_course(self, course_id: UUID) -> bool:
        """Soft delete a course."""
        return await self.course_repo.soft_delete(course_id)

    # ── Module/Lesson operations ────────────────────────────────────────

    async def add_module(self, course_id: UUID, title: str, description: str = None, sort_order: int = 0) -> dict:
        module = Module(course_id=course_id, title=title, description=description, sort_order=sort_order)
        module = await self.module_repo.create(module)
        return {"id": module.id, "title": module.title}

    async def add_lesson(self, module_id: UUID, title: str, description: str = None, sort_order: int = 0, duration_minutes: int = None, is_free: bool = False) -> dict:
        lesson = Lesson(module_id=module_id, title=title, description=description, sort_order=sort_order, duration_minutes=duration_minutes, is_free=is_free, is_published=True)
        lesson = await self.lesson_repo.create(lesson)
        return {"id": lesson.id, "title": lesson.title}

    async def list_categories(self) -> list[dict]:
        cats = await self.category_repo.list_active()
        return [{"id": c.id, "name": c.name, "slug": c.slug} for c in cats]

    # ── Capacity Helpers ────────────────────────────────────────────────

    async def _get_global_max_students(self) -> int:
        """Read global_max_students_per_class from system_settings."""
        result = await self.db.execute(
            sa_select(SystemSetting.value).where(
                SystemSetting.key == "global_max_students_per_class"
            )
        )
        row = result.scalar_one_or_none()
        return int(row) if row else 100

    async def _get_enrolled_count(self, course_id: uuid.UUID) -> int:
        """Count active enrollments across all classes of a course."""
        result = await self.db.execute(
            sa_select(sa_func.count(Enrollment.id)).where(
                Enrollment.course_id == course_id,
                Enrollment.status == "active",
            )
        )
        return result.scalar() or 0

    async def _get_course_classes_summary(self, course_id: uuid.UUID) -> dict:
        """Get class summary for a course: count, total available slots."""
        from app.models.course_class import CourseClass
        result = await self.db.execute(
            sa_select(CourseClass).where(
                CourseClass.course_id == course_id,
                CourseClass.status == "active",
            )
        )
        classes = result.scalars().all()
        global_max = await self._get_global_max_students()
        total_available = 0
        for cls in classes:
            enrolled_result = await self.db.execute(
                sa_select(sa_func.count(Enrollment.id)).where(
                    Enrollment.course_class_id == cls.id,
                    Enrollment.status == "active",
                )
            )
            enrolled = enrolled_result.scalar() or 0
            total_available += max(0, global_max - enrolled)
        return {
            "total_classes_count": len(classes),
            "total_available_slots": total_available,
            "has_available_classes": total_available > 0,
        }

    # ── Serialization Helpers ───────────────────────────────────────────

    async def _course_to_list_item(self, course: Course) -> dict:
        global_max = await self._get_global_max_students()
        enrolled = await self._get_enrolled_count(course.id)
        class_summary = await self._get_course_classes_summary(course.id)

        # Pricing calculations
        duration_months = course.duration_months or 1
        discount_pct = float(course.full_payment_discount_pct or 0)
        total_price = float(course.price)
        monthly_price = round(total_price / duration_months, 2) if duration_months else total_price
        full_payment_price = round(total_price * (1 - discount_pct / 100), 2)

        return {
            "id": str(course.id),
            "title": course.title,
            "slug": course.slug,
            "description": course.description,
            "short_description": course.short_description,
            "thumbnail_url": course.thumbnail_url,
            "price": total_price,
            "currency": course.currency,
            "level": course.level,
            "duration_hours": course.duration_hours,
            "duration_months": course.duration_months,
            "full_payment_discount_pct": float(course.full_payment_discount_pct or 0),
            "monthly_price": monthly_price,
            "full_payment_price": full_payment_price,
            "is_featured": course.is_featured,
            "is_active": course.is_active,
            "max_students": course.max_students,
            "effective_max_students": global_max,
            "enrolled_count": enrolled,
            "available_slots": max(0, global_max - enrolled) if enrolled is not None else global_max,
            "total_classes_count": class_summary["total_classes_count"],
            "total_available_slots": class_summary["total_available_slots"],
            "has_available_classes": class_summary["has_available_classes"],
            "teacher": {
                "id": str(course.teacher.id),
                "first_name": course.teacher.user.first_name,
                "last_name": course.teacher.user.last_name,
            } if course.teacher and course.teacher.user else None,
            "category": {
                "id": str(course.category.id),
                "name": course.category.name,
                "slug": course.category.slug,
            } if course.category else None,
        }

    async def _course_to_detail(self, course: Course) -> dict:
        detail = await self._course_to_list_item(course)
        detail["description"] = course.description
        detail["created_at"] = course.created_at.isoformat() if course.created_at else None
        detail["modules"] = [
            {
                "id": str(m.id),
                "title": m.title,
                "description": m.description,
                "sort_order": m.sort_order,
                "is_published": m.is_published,
                "lessons": [
                    {
                        "id": str(l.id),
                        "title": l.title,
                        "description": l.description,
                        "duration_minutes": l.duration_minutes,
                        "is_free": l.is_free,
                        "sort_order": l.sort_order,
                    }
                    for l in sorted(m.lessons, key=lambda x: x.sort_order)
                ],
            }
            for m in sorted(course.modules, key=lambda x: x.sort_order)
        ]
        return detail
