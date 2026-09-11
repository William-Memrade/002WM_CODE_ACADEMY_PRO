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
