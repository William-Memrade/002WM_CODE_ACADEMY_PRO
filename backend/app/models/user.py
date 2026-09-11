"""
CodeAcademy Pro — User Models
Users, Roles, and UserRoles ORM models.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseModel, SoftDeleteMixin, TimestampMixin


class Role(Base, TimestampMixin):
    """System roles (admin, teacher, student)."""
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    # Relationships
    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="role")


class UserRole(Base):
    """Many-to-many: users ↔ roles."""
    __tablename__ = "user_roles"
    __table_args__ = (
        Index("ix_user_roles_user_role", "user_id", "role_id", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id"), nullable=False, index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="NOW()")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="user_roles")
    role: Mapped["Role"] = relationship(back_populates="user_roles")


class User(BaseModel, SoftDeleteMixin):
    """Platform user (admin, teacher, or student)."""
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_status", "status"),
        Index("ix_users_status_deleted", "status", "deleted_at"),
    )

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    phone: Mapped[str | None] = mapped_column(String(20))
    bio: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    email_verification_token: Mapped[str | None] = mapped_column(String(255))
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    force_change_password: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships — lazy="noload" to avoid loading roles on every User query.
    # Use explicit selectinload(User.user_roles).selectinload(UserRole.role) where needed.
    user_roles: Mapped[list["UserRole"]] = relationship(back_populates="user", lazy="noload")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="student", foreign_keys="[Enrollment.student_id]")
    teacher_profile: Mapped["Teacher"] = relationship(back_populates="user", uselist=False)
    student_profile: Mapped["Student"] = relationship(back_populates="user", uselist=False)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def role_names(self) -> list[str]:
        return [ur.role.name for ur in self.user_roles if ur.role]


class Teacher(BaseModel, TimestampMixin):
    """Teacher profile for a user."""
    __tablename__ = "teachers"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    user: Mapped["User"] = relationship(back_populates="teacher_profile")
    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")
    classes: Mapped[list["CourseClass"]] = relationship(back_populates="teacher")


class Student(BaseModel, TimestampMixin):
    """Student profile for a user."""
    __tablename__ = "students"
    
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    enrollment_status: Mapped[str] = mapped_column(String(50), default="active")
    
    user: Mapped["User"] = relationship(back_populates="student_profile")
