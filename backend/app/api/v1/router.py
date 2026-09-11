"""
CodeAcademy Pro — API v1 Router
Aggregates all domain routers under /api/v1.
"""

from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router
from app.api.v1.courses.router import router as courses_router
from app.api.v1.payments.router import router as payments_router
from app.api.v1.users.router import router as users_router
from app.api.v1.reviews.router import router as reviews_router
from app.api.v1.notifications.router import router as notifications_router
from app.api.v1.audit.router import router as audit_router
from app.api.v1.teachers.router import router as teachers_router
from app.api.v1.settings.router import router as settings_router
from app.api.v1.admin.router import router as admin_router
from app.api.v1.course_classes.router import router as course_classes_router
from app.api.v1.attendance.router import router as attendance_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(courses_router, prefix="/courses", tags=["Courses"])
api_router.include_router(payments_router, prefix="/payments", tags=["Payments"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(teachers_router, prefix="/teachers", tags=["Teachers"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(audit_router, prefix="/audit-logs", tags=["Audit"])
api_router.include_router(settings_router, prefix="/settings", tags=["Settings"])
api_router.include_router(course_classes_router, tags=["Course Classes"])
api_router.include_router(attendance_router, tags=["Attendance"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
