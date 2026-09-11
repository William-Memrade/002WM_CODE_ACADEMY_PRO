"""
CodeAcademy Pro — Enrollment Service
Progreso del alumno: lectura (alumno y docente) y edición (docente de la clase).
"""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.models.course_class import CourseClass
from app.models.payment import Enrollment
from app.models.user import User
from app.repositories.enrollment_repository import EnrollmentRepository

# Escala real de `enrollments.progress_percentage` (NUMERIC(5,2), CHECK 0-100).
_PERCENT = Decimal("0.01")
_COMPLETED = Decimal("100")


class EnrollmentService:
    """Business logic para inscripciones y progreso."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EnrollmentRepository(db)

    # ── Helpers ─────────────────────────────────────────────────────────

    @staticmethod
    def _as_percent(value) -> Decimal:
        """Normaliza a la escala de la columna (NUMERIC(5,2))."""
        if value is None:
            return Decimal("0.00")
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        return value.quantize(_PERCENT)

    @classmethod
    def _to_item(
        cls,
        enrollment: Enrollment,
        course: Course | None = None,
        course_class: CourseClass | None = None,
        student: User | None = None,
    ) -> dict:
        item = {
            "enrollment_id": str(enrollment.id),
            "course_id": str(enrollment.course_id),
            "course_title": course.title if course else None,
            "course_class_id": str(enrollment.course_class_id) if enrollment.course_class_id else None,
            "course_class_name": course_class.name if course_class else None,
            "progress_percentage": float(cls._as_percent(enrollment.progress_percentage)),
            "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
            "status": enrollment.status,
        }
        if student is not None:
            item.update(
                {
                    "student_id": str(student.id),
                    "student_name": f"{student.first_name} {student.last_name}".strip(),
                    "student_email": student.email,
                }
            )
        return item

    # ── Lectura ─────────────────────────────────────────────────────────

    async def list_student_progress(self, student_id: UUID) -> list[dict]:
        """Progreso del propio alumno, una fila por inscripción."""
        rows = await self.repo.list_with_course_by_student(student_id)
        return [
            self._to_item(enrollment, course, course_class)
            for enrollment, course, course_class in rows
        ]

    async def list_teacher_students(self, teacher_id: UUID) -> list[dict]:
        """Alumnos activos de los cursos/clases del docente, con su progreso."""
        rows = await self.repo.list_with_student_by_teacher(teacher_id)
        return [
            self._to_item(enrollment, course, course_class, student)
            for enrollment, student, course, course_class in rows
        ]

    # ── Edición ─────────────────────────────────────────────────────────

    async def update_progress(self, enrollment_id: UUID, progress_percentage: Decimal) -> dict | None:
        """Actualiza el progreso de una inscripción concreta."""
        enrollment = await self.repo.get_by_id(enrollment_id)
        if not enrollment:
            return None
        return await self._apply(enrollment, progress_percentage)

    async def update_progress_by_class_student(
        self, class_id: UUID, student_id: UUID, progress_percentage: Decimal
    ) -> dict | None:
        """Actualiza el progreso desde la lista de alumnos de una clase."""
        enrollment = await self.repo.get_by_class_and_student(class_id, student_id)
        if not enrollment:
            return None
        return await self._apply(enrollment, progress_percentage)

    async def _apply(self, enrollment: Enrollment, progress_percentage: Decimal) -> dict:
        """
        Escribe el porcentaje y mantiene `completed_at` coherente.

        No se toca `status`: un alumno al 100% sigue siendo una inscripción activa
        (el estado `completed` sacaría al alumno de las listas de la clase, que
        filtran por `status = 'active'`). Marcar el 100% es reversible: si el
        docente baja el porcentaje, `completed_at` se limpia.
        """
        percent = self._as_percent(progress_percentage)
        enrollment.progress_percentage = percent

        if percent >= _COMPLETED:
            if not enrollment.completed_at:
                enrollment.completed_at = datetime.now(timezone.utc)
        else:
            enrollment.completed_at = None

        await self.repo.update(enrollment)

        context = await self.repo.get_with_context(enrollment.id)
        if not context:
            return self._to_item(enrollment)
        row_enrollment, course, course_class = context
        return self._to_item(row_enrollment, course, course_class)
