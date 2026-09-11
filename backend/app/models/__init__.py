"""
CodeAcademy Pro — Models __init__
Exports all models for Alembic and general use.
"""

from app.models.base import Base, BaseModel, TimestampMixin, SoftDeleteMixin
from app.models.user import User, Role, UserRole
from app.models.course import Category, Course, Module, Lesson, LiveClass, RecordedClass
from app.models.course_class import CourseClass, AttendanceRecord
from app.models.payment import Enrollment, Payment, PaymentProof, PaymentSettings
from app.models.audit import AuditLog
from app.models.system import SystemSetting, FeatureFlag

__all__ = [
    "Base",
    "BaseModel",
    "TimestampMixin",
    "SoftDeleteMixin",
    "User",
    "Role",
    "UserRole",
    "Category",
    "Course",
    "CourseClass",
    "AttendanceRecord",
    "Module",
    "Lesson",
    "LiveClass",
    "RecordedClass",
    "Enrollment",
    "Payment",
    "PaymentProof",
    "PaymentSettings",
    "AuditLog",
    "SystemSetting",
    "FeatureFlag",
]
