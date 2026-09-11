"""
CodeAcademy Pro — Course Models
Courses, Categories, Modules, Lessons, Live/Recorded Classes.
"""

import uuid
from datetime import datetime
# starts_at / ends_at removed — courses have no fixed dates
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel, SoftDeleteMixin, TimestampMixin, Base


class Category(BaseModel):
    """Course categories."""
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    courses: Mapped[list["Course"]] = relationship(back_populates="category")


class Course(BaseModel, SoftDeleteMixin):
    """Platform courses."""
    __tablename__ = "courses"
    __table_args__ = (
        Index("ix_courses_active_deleted", "is_active", "deleted_at"),
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str | None] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"))
    teacher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    level: Mapped[str] = mapped_column(String(20), default="beginner")
    duration_hours: Mapped[int | None] = mapped_column(Integer)
    duration_months: Mapped[int | None] = mapped_column(Integer)
    full_payment_discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    max_students: Mapped[int | None] = mapped_column(Integer)

    # Relationships
    category: Mapped["Category | None"] = relationship(back_populates="courses")
    teacher: Mapped["Teacher | None"] = relationship(back_populates="courses", foreign_keys=[teacher_id])
    modules: Mapped[list["Module"]] = relationship(back_populates="course", order_by="Module.sort_order")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")
    live_classes: Mapped[list["LiveClass"]] = relationship(back_populates="course")
    classes: Mapped[list["CourseClass"]] = relationship(back_populates="course")


class Module(BaseModel):
    """Course modules/sections."""
    __tablename__ = "modules"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    course: Mapped["Course"] = relationship(back_populates="modules")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="module", order_by="Lesson.sort_order")


class Lesson(BaseModel):
    """Individual lessons within a module."""
    __tablename__ = "lessons"

    module_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("modules.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    module: Mapped["Module"] = relationship(back_populates="lessons")
    recorded_classes: Mapped[list["RecordedClass"]] = relationship(back_populates="lesson")


class LiveClass(BaseModel):
    """Scheduled live class sessions."""
    __tablename__ = "live_classes"

    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    meeting_url: Mapped[str] = mapped_column(String(500), nullable=False)
    meeting_platform: Mapped[str | None] = mapped_column(String(50))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_recorded: Mapped[bool] = mapped_column(Boolean, default=False)
    recording_url: Mapped[str | None] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(20), default="scheduled")

    course: Mapped["Course"] = relationship(back_populates="live_classes")


class RecordedClass(BaseModel):
    """Pre-recorded video content."""
    __tablename__ = "recorded_classes"

    lesson_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(String(500), nullable=False)
    video_provider: Mapped[str] = mapped_column(String(50), default="storage")
    duration_minutes: Mapped[int | None] = mapped_column(Integer)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)

    lesson: Mapped["Lesson"] = relationship(back_populates="recorded_classes")


# Forward reference imports
from app.models.user import User
from app.models.payment import Enrollment
