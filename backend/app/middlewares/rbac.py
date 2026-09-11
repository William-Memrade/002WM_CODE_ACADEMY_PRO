"""
CodeAcademy Pro — RBAC (Role-Based Access Control) Middleware
Role checking decorators and dependencies for endpoint protection.
"""

from functools import wraps
from typing import Callable

from fastapi import Depends, HTTPException, status

from app.middlewares.auth import get_current_user


def require_roles(*required_roles: str) -> Callable:
    """
    Dependency that checks if the current user has at least one of the required roles.

    Usage:
        @router.post("/courses")
        async def create_course(
            current_user = Depends(require_roles("admin"))
        ): ...

        @router.put("/courses/{id}")
        async def edit_course(
            current_user = Depends(require_roles("admin", "teacher"))
        ): ...
    """

    async def role_checker(current_user=Depends(get_current_user)):
        user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()

        if not user_roles.intersection(set(required_roles)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions.",
            )

        return current_user

    return role_checker


# ── Convenience Dependencies ────────────────────────────────────────────────

require_admin = require_roles("admin")
require_teacher = require_roles("teacher")
require_student = require_roles("student")
require_coordinator = require_roles("coordinator")
require_admin_or_teacher = require_roles("admin", "teacher")
require_admin_or_coordinator = require_roles("admin", "coordinator")
require_admin_or_coordinator_or_teacher = require_roles("admin", "coordinator", "teacher")

async def require_student_or_pending(current_user=Depends(get_current_user)):
    """
    Allow users who are:
    1. Students (have student role), OR
    2. In pending status (waiting for role assignment)
    
    Used for payment proof uploads and other early-access features.
    """
    user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()
    
    # Allow if user is student OR in pending status
    if "student" in user_roles or current_user.status == "pending":
        return current_user
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Student role or pending status required to perform this action",
    )


# ── Ownership Verification Helpers ──────────────────────────────────────────


def verify_ownership(user_id, resource_owner_id, allow_admin: bool = True):
    """
    Verify that the current user owns the resource.
    Admins bypass ownership check if allow_admin is True.

    Usage in service layer:
        verify_ownership(current_user.id, enrollment.student_id)
    """
    if str(user_id) != str(resource_owner_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )


# ── Resource Access Helpers (curso / clase) ─────────────────────────────────
# El rol dice *qué tipo* de acción puede hacer alguien; estos helpers responden
# *sobre qué recurso concreto*. Los usan el temario (módulos y lecciones) y el
# progreso del alumno, que exigen ser el docente del curso o de la clase.


def has_role(user, *roles: str) -> bool:
    """True si el usuario tiene alguno de los roles indicados."""
    user_roles = set(user.role_names) if hasattr(user, "role_names") else set()
    return bool(user_roles.intersection(roles))


async def get_teacher_profile(db, user):
    """Perfil `teachers` del usuario actual (None si no es docente)."""
    from sqlalchemy import select

    from app.models.user import Teacher

    result = await db.execute(select(Teacher).where(Teacher.user_id == user.id))
    return result.scalar_one_or_none()


async def ensure_course_manager(db, user, course_id) -> None:
    """
    Autoriza gestionar el temario de un curso.

    Pasa admin y coordinador; un docente pasa si es el titular del curso
    (`courses.teacher_id`) o si tiene alguna clase del curso asignada. Lanza 404
    si el curso no existe (o RLS lo esconde) y 403 si no está asignado.
    """
    from sqlalchemy import select

    from app.models.course import Course
    from app.models.course_class import CourseClass

    result = await db.execute(
        select(Course.id, Course.teacher_id).where(
            Course.id == course_id, Course.deleted_at.is_(None)
        )
    )
    course = result.one_or_none()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    if has_role(user, "admin", "coordinator"):
        return

    teacher = await get_teacher_profile(db, user)
    if teacher is not None:
        if str(course.teacher_id) == str(teacher.id):
            return
        class_result = await db.execute(
            select(CourseClass.id)
            .where(
                CourseClass.course_id == course_id,
                CourseClass.teacher_id == teacher.id,
                CourseClass.deleted_at.is_(None),
            )
            .limit(1)
        )
        if class_result.scalar_one_or_none() is not None:
            return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You are not assigned to this course",
    )


async def ensure_class_manager(db, user, class_id) -> None:
    """
    Autoriza operar sobre una clase (progreso de sus alumnos, asistencia…).

    Pasa admin y coordinador; el docente pasa si es el titular de la clase.
    """
    from sqlalchemy import select

    from app.models.course_class import CourseClass

    result = await db.execute(
        select(CourseClass.id, CourseClass.teacher_id).where(
            CourseClass.id == class_id, CourseClass.deleted_at.is_(None)
        )
    )
    course_class = result.one_or_none()
    if course_class is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Class not found")

    if has_role(user, "admin", "coordinator"):
        return

    teacher = await get_teacher_profile(db, user)
    if teacher is None or str(course_class.teacher_id) != str(teacher.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not assigned to this class",
        )
