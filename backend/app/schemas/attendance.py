"""
CodeAcademy Pro — Pydantic Schemas: Attendance
Request/response schemas for attendance records.
"""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


_ALLOWED_ATTENDANCE_STATUSES = frozenset({"present", "absent", "late", "excused"})


class AttendanceCreate(BaseModel):
    """POST /course-classes/{class_id}/attendance request body."""
    student_id: UUID
    session_date: date
    status: str = Field(default="present", max_length=20)
    notes: str | None = Field(None, max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in _ALLOWED_ATTENDANCE_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(_ALLOWED_ATTENDANCE_STATUSES))}")
        return v


class AttendanceUpdate(BaseModel):
    """PATCH /attendance/{attendance_id} request body."""
    status: str | None = Field(None, max_length=20)
    notes: str | None = Field(None, max_length=1000)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in _ALLOWED_ATTENDANCE_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(_ALLOWED_ATTENDANCE_STATUSES))}")
        return v


class AttendanceResponse(BaseModel):
    """Attendance record detail response."""
    id: UUID
    course_class_id: UUID
    student_id: UUID
    teacher_id: UUID
    session_date: date
    status: str
    notes: str | None
    created_at: date
    updated_at: date

    model_config = {"from_attributes": True}


class AttendanceSummaryResponse(BaseModel):
    """Summary of attendance for a student in a class."""
    course_class_id: UUID
    total_sessions: int
    present_count: int
    absent_count: int
    late_count: int
    excused_count: int
    attendance_rate_pct: float
