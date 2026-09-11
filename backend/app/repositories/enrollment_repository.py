"""
CodeAcademy Pro — Enrollment Repository
Data access for enrollments (progreso del alumno).
"""

from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_class import CourseClass
from app.models.payment import Enrollment
from app.models.user import User
from app.repositories.base import BaseRepository


class EnrollmentRepository(BaseRepository[Enrollment]):
    """Repository for Enrollment operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Enrollment, db)

    async def get_with_context(
        self, enrollment_id: UUID
    ) -> tuple[Enrollment, Course, CourseClass | None] | None:
        """Una inscripción con su curso y su clase (si ya tiene clase asignada)."""
        result = await self.db.execute(
            select(Enrollment, Course, CourseClass)
            .join(Course, Enrollment.course_id == Course.id)
            .outerjoin(CourseClass, Enrollment.course_class_id == CourseClass.id)
            .where(Enrollment.id == enrollment_id)
        )
        row = result.one_or_none()
        return (row[0], row[1], row[2]) if row else None

    async def get_by_class_and_student(
        self, class_id: UUID, student_id: UUID
    ) -> Enrollment | None:
        """Inscripción activa de un alumno en una clase concreta."""
        result = await self.db.execute(
            select(Enrollment).where(
                Enrollment.course_class_id == class_id,
                Enrollment.student_id == student_id,
                Enrollment.status == "active",
            )
        )
        return result.scalar_one_or_none()

    async def list_with_course_by_student(
        self, student_id: UUID
    ) -> list[tuple[Enrollment, Course, CourseClass | None]]:
        """Inscripciones de un alumno con el curso y la clase de cada una."""
        result = await self.db.execute(
            select(Enrollment, Course, CourseClass)
            .join(Course, Enrollment.course_id == Course.id)
            .outerjoin(CourseClass, Enrollment.course_class_id == CourseClass.id)
            .where(Enrollment.student_id == student_id)
            .order_by(Course.title)
        )
        return [tuple(row) for row in result.all()]

    async def list_with_student_by_teacher(
        self, teacher_id: UUID
    ) -> list[tuple[Enrollment, User, Course, CourseClass | None]]:
        """
        Inscripciones activas de los cursos/clases de un docente.

        Cubre los dos modos de asignación que usa la plataforma: docente titular
        del curso (`courses.teacher_id`) y docente de una clase concreta
        (`course_classes.teacher_id`).
        """
        result = await self.db.execute(
            select(Enrollment, User, Course, CourseClass)
            .join(User, Enrollment.student_id == User.id)
            .join(Course, Enrollment.course_id == Course.id)
            .outerjoin(CourseClass, Enrollment.course_class_id == CourseClass.id)
            .where(
                Enrollment.status == "active",
                or_(
                    Course.teacher_id == teacher_id,
                    CourseClass.teacher_id == teacher_id,
                ),
            )
            .order_by(Course.title, User.first_name, User.last_name)
        )
        return [tuple(row) for row in result.all()]
