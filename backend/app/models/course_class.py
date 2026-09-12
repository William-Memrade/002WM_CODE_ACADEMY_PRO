"""
CodeAcademy Pro — Course Class & Attendance Models
CourseClass represents a class/group/cohort instance of a Course.
AttendanceRecord tracks daily/session attendance.
"""

import uuid
from datetime import date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, SoftDeleteMixin


class CourseClass(BaseModel, SoftDeleteMixin):
    """A class/group/cohort instance of a Course."""
    __tablename__ = "course_classes"
    __table_args__ = (
        UniqueConstraint("course_id", "name", name="uq_course_class_name_per_course"),
    )

    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True
    )
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    schedule_info: Mapped[str | None] = mapped_column(String(500))
    days_of_week: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    start_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    end_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")
    meeting_platform: Mapped[str | None] = mapped_column(String(50))
    meeting_url: Mapped[str | None] = mapped_column(String(500))
    # Grabación de la sesión: la publica el docente titular de la clase (o un admin).
    recording_platform: Mapped[str | None] = mapped_column(String(50))
    recording_url: Mapped[str | None] = mapped_column(String(500))
    recording_updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Relationships
    course: Mapped["Course"] = relationship(back_populates="classes")
    teacher: Mapped["Teacher | None"] = relationship(back_populates="classes")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course_class")
    attendance_records: Mapped[list["AttendanceRecord"]] = relationship(
        back_populates="course_class", cascade="all, delete-orphan"
    )


class AttendanceRecord(BaseModel):
    """Attendance record for a student in a class session."""
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint(
            "course_class_id", "student_id", "session_date",
            name="uq_attendance_class_student_date"
        ),
        Index("ix_attendance_course_class_session", "course_class_id", "session_date"),
        Index("ix_attendance_student", "student_id"),
    )

    course_class_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("course_classes.id", ondelete="CASCADE"), nullable=False
    )
    student_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    teacher_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="present")
    notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    course_class: Mapped["CourseClass"] = relationship(back_populates="attendance_records")
    student: Mapped["User"] = relationship(foreign_keys=[student_id])
    teacher: Mapped["User"] = relationship(foreign_keys=[teacher_id])
