"""
CodeAcademy Pro — Course Class Repository
Data access for course_classes and attendance.
"""

from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.course_class import CourseClass, AttendanceRecord
from app.models.user import Teacher
from app.repositories.base import BaseRepository


class CourseClassRepository(BaseRepository[CourseClass]):
    """Repository for CourseClass operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(CourseClass, db)

    async def get_by_name_in_course(self, course_id: UUID, name: str) -> CourseClass | None:
        """Check if a class with the given name already exists in the course (excluding deleted)."""
        result = await self.db.execute(
            select(CourseClass).where(
                CourseClass.course_id == course_id,
                CourseClass.name == name,
                CourseClass.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name_in_course_excluding(self, course_id: UUID, name: str, exclude_id: UUID) -> CourseClass | None:
        """Check if a class with the given name exists in the course, excluding a specific class."""
        result = await self.db.execute(
            select(CourseClass).where(
                CourseClass.course_id == course_id,
                CourseClass.name == name,
                CourseClass.id != exclude_id,
                CourseClass.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> CourseClass | None:
        """Get a class by its unique slug (global)."""
        result = await self.db.execute(
            select(CourseClass).where(CourseClass.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_by_slug_excluding(self, slug: str, exclude_id: UUID) -> CourseClass | None:
        """Get a class by slug, excluding a specific class (for update collision check)."""
        result = await self.db.execute(
            select(CourseClass).where(
                CourseClass.slug == slug,
                CourseClass.id != exclude_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_full(self, class_id: UUID) -> CourseClass | None:
        """Get class by ID with course and teacher relations."""
        result = await self.db.execute(
            select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
            .where(CourseClass.id == class_id)
        )
        return result.scalar_one_or_none()

    async def list_by_course(self, course_id: UUID, *, include_deleted: bool = False) -> list[CourseClass]:
        """List all classes for a course."""
        stmt = (
            select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
            .where(CourseClass.course_id == course_id)
            .order_by(CourseClass.created_at.desc())
        )
        if not include_deleted:
            stmt = stmt.where(CourseClass.deleted_at.is_(None))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_active_by_course(self, course_id: UUID) -> list[CourseClass]:
        """List active classes for a course (no deleted)."""
        result = await self.db.execute(
            select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
            .where(
                CourseClass.course_id == course_id,
                CourseClass.status == "active",
                CourseClass.deleted_at.is_(None),
            )
            .order_by(CourseClass.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_teacher(self, teacher_id: UUID) -> list[CourseClass]:
        """List active classes assigned to a teacher."""
        result = await self.db.execute(
            select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
            .where(
                CourseClass.teacher_id == teacher_id,
                CourseClass.status == "active",
                CourseClass.deleted_at.is_(None),
            )
            .order_by(CourseClass.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_filtered(
        self,
        *,
        status: str | None = None,
        day: str | None = None,
        teacher_id: UUID | None = None,
        course_id: UUID | None = None,
        without_teacher: bool = False,
        missing_link: bool = False,
        include_deleted: bool = False,
    ) -> list[CourseClass]:
        """List classes with filters."""
        from sqlalchemy import or_
        from app.models.course import Course

        stmt = (
            select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
        )

        if not include_deleted:
            stmt = stmt.where(CourseClass.deleted_at.is_(None))

        if status is not None:
            stmt = stmt.where(CourseClass.status == status)

        if day is not None:
            stmt = stmt.where(CourseClass.days_of_week.contains([day]))

        if teacher_id is not None:
            stmt = stmt.where(CourseClass.teacher_id == teacher_id)

        if course_id is not None:
            stmt = stmt.where(CourseClass.course_id == course_id)

        if without_teacher:
            stmt = stmt.where(CourseClass.teacher_id.is_(None))

        if missing_link:
            stmt = stmt.where(
                or_(
                    CourseClass.meeting_url.is_(None),
                    CourseClass.meeting_url == "",
                )
            )

        stmt = stmt.order_by(CourseClass.start_time.asc().nullslast(), CourseClass.name.asc())
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_today(self, today_weekday: str) -> list[CourseClass]:
        """List active classes scheduled for today, ordered by start_time."""
        result = await self.db.execute(
            select(CourseClass)
            .options(
                selectinload(CourseClass.course),
                selectinload(CourseClass.teacher).selectinload(Teacher.user),
            )
            .where(
                CourseClass.days_of_week.contains([today_weekday]),
                CourseClass.status == "active",
                CourseClass.deleted_at.is_(None),
            )
            .order_by(CourseClass.start_time.asc().nullslast())
        )
        return list(result.scalars().all())

    async def get_enrolled_count(self, class_id: UUID) -> int:
        """Count active enrollments for a class."""
        from app.models.payment import Enrollment
        result = await self.db.execute(
            select(func.count()).select_from(Enrollment).where(
                Enrollment.course_class_id == class_id,
                Enrollment.status == "active",
            )
        )
        return result.scalar() or 0


class AttendanceRepository(BaseRepository[AttendanceRecord]):
    """Repository for AttendanceRecord operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(AttendanceRecord, db)

    async def list_by_class(self, course_class_id: UUID) -> list[AttendanceRecord]:
        """List attendance records for a class."""
        result = await self.db.execute(
            select(AttendanceRecord)
            .where(AttendanceRecord.course_class_id == course_class_id)
            .order_by(AttendanceRecord.session_date.desc())
        )
        return list(result.scalars().all())

    async def list_by_student(self, student_id: UUID) -> list[AttendanceRecord]:
        """List attendance records for a student."""
        result = await self.db.execute(
            select(AttendanceRecord)
            .where(AttendanceRecord.student_id == student_id)
            .order_by(AttendanceRecord.session_date.desc())
        )
        return list(result.scalars().all())

    async def get_by_class_student_date(
        self, course_class_id: UUID, student_id: UUID, session_date
    ) -> AttendanceRecord | None:
        """Get a specific attendance record."""
        result = await self.db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.course_class_id == course_class_id,
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.session_date == session_date,
            )
        )
        return result.scalar_one_or_none()

    async def get_summary_by_class(self, course_class_id: UUID) -> dict:
        """Get attendance summary for a class."""
        result = await self.db.execute(
            select(
                func.count().label("total"),
                func.sum(func.case((AttendanceRecord.status == "present", 1), else_=0)).label("present"),
                func.sum(func.case((AttendanceRecord.status == "absent", 1), else_=0)).label("absent"),
                func.sum(func.case((AttendanceRecord.status == "late", 1), else_=0)).label("late"),
                func.sum(func.case((AttendanceRecord.status == "excused", 1), else_=0)).label("excused"),
            ).where(AttendanceRecord.course_class_id == course_class_id)
        )
        row = result.one()
        total = row.total or 0
        present = row.present or 0
        absent = row.absent or 0
        late = row.late or 0
        excused = row.excused or 0
        rate = round((present / total) * 100, 2) if total > 0 else 0.0
        return {
            "total_sessions": total,
            "present_count": present,
            "absent_count": absent,
            "late_count": late,
            "excused_count": excused,
            "attendance_rate_pct": rate,
        }
