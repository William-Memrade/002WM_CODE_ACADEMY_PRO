"""
CodeAcademy Pro — Pydantic Schemas: CourseClass
Request/response schemas for course classes and attendance.
"""

from datetime import date, datetime, time
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


_ALLOWED_CLASS_STATUSES = frozenset({"active", "inactive", "cancelled", "deleted"})
_WEEKDAYS = frozenset({"mon", "tue", "wed", "thu", "fri", "sat", "sun"})


class CourseClassCreate(BaseModel):
    """POST /courses/{course_id}/classes request body."""
    name: str = Field(..., min_length=2, max_length=255)
    days_of_week: list[str] = Field(default_factory=list)
    start_time: time | None = None
    end_time: time | None = None
    meeting_platform: str | None = Field(None, max_length=50)
    meeting_url: str | None = Field(None, max_length=500)

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: list[str]) -> list[str]:
        invalid = [d for d in v if d not in _WEEKDAYS]
        if invalid:
            raise ValueError(f"Invalid weekdays: {invalid}. Use: {_WEEKDAYS}")
        if not v:
            raise ValueError("At least one weekday is required")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: time | None, info) -> time | None:
        start = info.data.get("start_time")
        if start and v:
            if v <= start:
                raise ValueError("end_time must be after start_time")
        return v


class CourseClassUpdate(BaseModel):
    """PATCH /course-classes/{class_id} request body."""
    name: str | None = Field(None, min_length=2, max_length=255)
    days_of_week: list[str] | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: str | None = Field(None, max_length=20)
    meeting_platform: str | None = Field(None, max_length=50)
    meeting_url: str | None = Field(None, max_length=500)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if v not in _ALLOWED_CLASS_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(_ALLOWED_CLASS_STATUSES))}")
        return v

    @field_validator("days_of_week")
    @classmethod
    def validate_days(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        invalid = [d for d in v if d not in _WEEKDAYS]
        if invalid:
            raise ValueError(f"Invalid weekdays: {invalid}. Use: {_WEEKDAYS}")
        if not v:
            raise ValueError("At least one weekday is required")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, v: time | None, info) -> time | None:
        start = info.data.get("start_time")
        if start and v:
            if v <= start:
                raise ValueError("end_time must be after start_time")
        return v


class CourseClassStatusUpdate(BaseModel):
    """PATCH /course-classes/{class_id}/status request body."""
    status: str = Field(..., max_length=20)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in _ALLOWED_CLASS_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(_ALLOWED_CLASS_STATUSES))}")
        return v


class AssignTeacherRequest(BaseModel):
    """PATCH /course-classes/{class_id}/assign-teacher request body."""
    teacher_id: UUID


class MeetingLinkUpdateRequest(BaseModel):
    """PATCH /course-classes/{class_id}/meeting-link request body."""
    meeting_platform: str = Field(..., max_length=50)
    meeting_url: str = Field(..., max_length=500)


class CourseClassCapacityResponse(BaseModel):
    """GET /course-classes/{class_id}/capacity response."""
    course_class_id: UUID
    global_max: int
    enrolled_count: int
    available_slots: int
    is_full: bool


class CourseClassResponse(BaseModel):
    """CourseClass detail response."""
    id: UUID
    course_id: UUID
    teacher_id: UUID | None
    created_by: UUID | None
    name: str
    slug: str
    schedule_info: str | None
    days_of_week: list[str]
    start_time: str | None
    end_time: str | None
    status: str
    meeting_platform: str | None
    meeting_url: str | None
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    enrolled_count: int = 0
    available_slots: int = 0
    global_max: int = 100
    teacher_name: str | None = None
    course_title: str | None = None

    model_config = {"from_attributes": True}


class CourseClassListItem(BaseModel):
    """CourseClass item in list responses."""
    id: UUID
    course_id: UUID
    name: str
    slug: str
    schedule_info: str | None
    status: str
    meeting_platform: str | None
    start_time: str | None
    end_time: str | None
    days_of_week: list[str]
    teacher_name: str | None = None
    enrolled_count: int = 0
    available_slots: int = 0
    global_max: int = 100
    has_meeting_link: bool = False

    model_config = {"from_attributes": True}
