"""
CodeAcademy Pro — Payment Models
Enrollments, Payments, PaymentProofs.

New flow: Payment is created first (with proof upload).
         Enrollment is created ONLY when admin approves the payment.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Enrollment(BaseModel):
    """Student course enrollments — created only on payment approval."""
    __tablename__ = "enrollments"
    __table_args__ = (
        Index("ix_enrollments_student_course", "student_id", "course_id"),
        Index("ix_enrollments_status", "status"),
    )

    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active")
    enrolled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="NOW()")
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    progress_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0.00)
    course_class_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("course_classes.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    student: Mapped["User"] = relationship(back_populates="enrollments", foreign_keys=[student_id])
    course: Mapped["Course"] = relationship(back_populates="enrollments")
    payments: Mapped[list["Payment"]] = relationship(back_populates="enrollment")
    course_class: Mapped["CourseClass | None"] = relationship(back_populates="enrollments")


class Payment(BaseModel):
    """Payment records — created when student uploads proof."""
    __tablename__ = "payments"
    __table_args__ = (
        Index("ix_payments_status", "status"),
        Index("ix_payments_student_course", "student_id", "course_id"),
    )

    # Direct references (always set at creation)
    student_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    course_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False, index=True)

    # Enrollment is set ONLY after admin approves (nullable)
    enrollment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("enrollments.id", ondelete="SET NULL"), nullable=True)

    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    payment_method: Mapped[str] = mapped_column(String(50), default="bank_transfer")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    payment_plan: Mapped[str] = mapped_column(String(20), default="full")
    expected_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    duration_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    monthly_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    full_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    reference_number: Mapped[str | None] = mapped_column(String(100))
    reviewed_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    review_notes: Mapped[str | None] = mapped_column(Text)

    # Relationships
    enrollment: Mapped["Enrollment | None"] = relationship(back_populates="payments", foreign_keys=[enrollment_id])
    course: Mapped["Course"] = relationship(foreign_keys=[course_id])
    student_user: Mapped["User"] = relationship(foreign_keys=[student_id])
    proofs: Mapped[list["PaymentProof"]] = relationship(back_populates="payment")


class PaymentProof(BaseModel):
    """Uploaded payment proof files."""
    __tablename__ = "payment_proofs"

    payment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    payment: Mapped["Payment"] = relationship(back_populates="proofs")


class PaymentSettings(BaseModel):
    """System-wide payment configuration settings."""
    __tablename__ = "payment_settings"

    bank_name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_number: Mapped[str] = mapped_column(String(100), nullable=False)
    account_holder: Mapped[str] = mapped_column(String(255), nullable=False)
    payment_instructions: Mapped[str | None] = mapped_column(Text)
    qr_image_url: Mapped[str | None] = mapped_column(String(500))

    # Relationships and constraints can be added here if needed


# Forward references
from app.models.user import User, Student
from app.models.course import Course
