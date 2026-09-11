"""
CodeAcademy Pro — Pydantic Schemas: Enrollment
Schemas del progreso del alumno (`enrollments.progress_percentage`).
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class EnrollmentProgressUpdate(BaseModel):
    """Body de `PATCH .../progress` — lo edita el docente de la clase."""

    progress_percentage: Decimal = Field(
        ...,
        ge=0,
        le=100,
        max_digits=5,
        decimal_places=2,
        description="Porcentaje de avance del alumno (0-100).",
    )


class EnrollmentProgressItem(BaseModel):
    """Fila de progreso de una inscripción (lectura: alumno y docente)."""

    enrollment_id: str
    student_id: str | None = None
    student_name: str | None = None
    student_email: str | None = None
    course_id: str
    course_title: str | None = None
    course_class_id: str | None = None
    course_class_name: str | None = None
    progress_percentage: float = 0
    completed_at: str | None = None
    status: str | None = None
