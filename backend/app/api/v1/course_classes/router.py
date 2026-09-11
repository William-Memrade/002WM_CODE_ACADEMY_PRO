"""
CodeAcademy Pro — Course Classes Router
Endpoints for managing course classes/groups.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.rls import get_rls_db
from app.middlewares.rbac import (
    require_admin, require_coordinator, require_admin_or_coordinator,
    require_teacher, require_admin_or_coordinator_or_teacher,
)
from app.schemas.course_class import (
    CourseClassCreate, CourseClassUpdate, CourseClassStatusUpdate,
    AssignTeacherRequest, MeetingLinkUpdateRequest, CourseClassCapacityResponse,
)
from app.services.course_class_service import CourseClassService
from app.services.audit_service import AuditService

router = APIRouter()


# ── Public endpoints ────────────────────────────────────────────────────────

@router.get("/courses/{course_id}/classes")
async def list_course_classes(
    course_id: UUID,
    db: AsyncSession = Depends(get_rls_db),
):
    """List active classes for a course (public, no meeting_url)."""
    svc = CourseClassService(db)
    classes = await svc.list_active_classes_by_course_public(course_id)
    return {"items": classes}


# ── Admin / Coordinator: list all classes with filters ──────────────────────
# NOTE: static paths MUST be registered before dynamic /{class_id} routes
# to prevent FastAPI from trying to parse "today" as a UUID.

@router.get("/course-classes")
async def list_classes(
    status: str | None = Query(None, description="Filter by status"),
    day: str | None = Query(None, description="Filter by weekday: mon,tue,wed,thu,fri,sat,sun"),
    teacher_id: UUID | None = Query(None),
    course_id: UUID | None = Query(None),
    without_teacher: bool = Query(False),
    available_slots: bool = Query(False),
    missing_link: bool = Query(False),
    include_deleted: bool = Query(False),
    current_user=Depends(require_admin_or_coordinator),
    db: AsyncSession = Depends(get_rls_db),
):
    """List all classes with filters (admin or coordinator)."""
    svc = CourseClassService(db)
    classes = await svc.list_classes_filtered(
        status=status,
        day=day,
        teacher_id=teacher_id,
        course_id=course_id,
        without_teacher=without_teacher,
        missing_link=missing_link,
        include_deleted=include_deleted,
    )
    if available_slots:
        # Filter in Python since capacity requires DB query per class
        classes = [c for c in classes if c.get("available_slots", 0) > 0]
    return {"items": classes}


@router.get("/course-classes/today")
async def list_classes_today(
    current_user=Depends(require_admin_or_coordinator_or_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """List active classes scheduled for today (admin, coordinator, or teacher)."""
    svc = CourseClassService(db)
    classes = await svc.list_classes_today()

    # Teacher only sees their own classes
    user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()
    is_admin = "admin" in user_roles
    is_coordinator = "coordinator" in user_roles

    if not is_admin and not is_coordinator:
        from app.models.user import Teacher
        from sqlalchemy import select
        t_result = await db.execute(
            select(Teacher).where(Teacher.user_id == current_user.id)
        )
        teacher = t_result.scalar_one_or_none()
        if teacher:
            classes = [c for c in classes if str(c.get("teacher_id")) == str(teacher.id)]
        else:
            classes = []

    return {"items": classes}


# ── Public endpoints (dynamic) ──────────────────────────────────────────────

@router.get("/course-classes/{class_id}")
async def get_class_detail(
    class_id: UUID,
    db: AsyncSession = Depends(get_rls_db),
):
    """Get class detail (public, no meeting_url)."""
    svc = CourseClassService(db)
    result = await svc.get_class_public(class_id)
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")
    return result


@router.get("/course-classes/{class_id}/capacity")
async def get_class_capacity(
    class_id: UUID,
    db: AsyncSession = Depends(get_rls_db),
):
    """Get class capacity (public)."""
    svc = CourseClassService(db)
    result = await svc.get_class_capacity(class_id)
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")
    return result


# ── Admin / Coordinator endpoints ───────────────────────────────────────────

@router.post("/courses/{course_id}/classes", status_code=status.HTTP_201_CREATED)
async def create_class(
    course_id: UUID,
    data: CourseClassCreate,
    request: Request,
    current_user=Depends(require_admin_or_coordinator),
    db: AsyncSession = Depends(get_rls_db),
):
    """Create a new class for a course (admin or coordinator)."""
    svc = CourseClassService(db)
    result = await svc.create_class(
        course_id=course_id,
        name=data.name,
        created_by=current_user.id,
        days_of_week=data.days_of_week,
        start_time=data.start_time,
        end_time=data.end_time,
        meeting_platform=data.meeting_platform,
        meeting_url=data.meeting_url,
    )

    await AuditService(db).log_action(
        actor_user=current_user,
        action="course_class_created",
        entity_type="course_class",
        entity_id=result["id"],
        entity_label=result["name"],
        request=request,
        metadata={"course_id": str(course_id), "slug": result["slug"]},
    )
    return result


@router.patch("/course-classes/{class_id}")
async def update_class(
    class_id: UUID,
    data: CourseClassUpdate,
    request: Request,
    current_user=Depends(require_admin_or_coordinator),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update a class (admin or coordinator)."""
    svc = CourseClassService(db)
    result = await svc.update_class(class_id, **data.model_dump(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")

    await AuditService(db).log_action(
        actor_user=current_user,
        action="course_class_updated",
        entity_type="course_class",
        entity_id=class_id,
        entity_label=result["name"],
        request=request,
        metadata={"fields_updated": list(data.model_dump(exclude_unset=True).keys())},
    )
    return result


@router.patch("/course-classes/{class_id}/status")
async def change_class_status(
    class_id: UUID,
    data: CourseClassStatusUpdate,
    request: Request,
    current_user=Depends(require_admin_or_coordinator),
    db: AsyncSession = Depends(get_rls_db),
):
    """Change class status (admin or coordinator)."""
    svc = CourseClassService(db)
    result = await svc.change_status(class_id, data.status)
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")

    await AuditService(db).log_action(
        actor_user=current_user,
        action="course_class_status_updated",
        entity_type="course_class",
        entity_id=class_id,
        entity_label=result["name"],
        request=request,
        metadata={"new_status": data.status},
    )
    return result


@router.delete("/course-classes/{class_id}")
async def delete_class(
    class_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Soft delete a class (admin only)."""
    svc = CourseClassService(db)
    course_class = await svc.get_class(class_id)
    if not course_class:
        raise HTTPException(status_code=404, detail="Class not found")

    result = await svc.soft_delete_class(class_id)

    await AuditService(db).log_action(
        actor_user=current_user,
        action="course_class_deleted",
        entity_type="course_class",
        entity_id=class_id,
        entity_label=course_class.get("name"),
        request=request,
    )
    return result


@router.patch("/course-classes/{class_id}/assign-teacher")
async def assign_teacher(
    class_id: UUID,
    data: AssignTeacherRequest,
    request: Request,
    current_user=Depends(require_admin_or_coordinator),
    db: AsyncSession = Depends(get_rls_db),
):
    """Assign a teacher to a class (admin or coordinator)."""
    svc = CourseClassService(db)
    result = await svc.assign_teacher(class_id, data.teacher_id)
    if not result:
        raise HTTPException(status_code=404, detail="Class not found")

    await AuditService(db).log_action(
        actor_user=current_user,
        action="course_class_teacher_assigned",
        entity_type="course_class",
        entity_id=class_id,
        entity_label=result["name"],
        request=request,
        metadata={"teacher_id": str(data.teacher_id)},
    )
    return result


# ── Meeting link (admin, coordinator, or assigned teacher) ────────────────────

@router.patch("/course-classes/{class_id}/meeting-link")
async def update_meeting_link(
    class_id: UUID,
    data: MeetingLinkUpdateRequest,
    request: Request,
    current_user=Depends(require_admin_or_coordinator_or_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update meeting link for a class."""
    svc = CourseClassService(db)
    course_class = await svc.get_class(class_id)
    if not course_class:
        raise HTTPException(status_code=404, detail="Class not found")

    user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()
    is_admin = "admin" in user_roles
    is_coordinator = "coordinator" in user_roles

    if not is_admin and not is_coordinator:
        # Teacher must be assigned to this class
        from app.models.user import Teacher
        from sqlalchemy import select
        t_result = await db.execute(
            select(Teacher).where(Teacher.user_id == current_user.id)
        )
        teacher = t_result.scalar_one_or_none()
        if not teacher:
            raise HTTPException(status_code=403, detail="Teacher profile not found")

        if str(course_class.get("teacher_id")) != str(teacher.id):
            raise HTTPException(status_code=403, detail="You are not assigned to this class")

    result = await svc.update_meeting_link(
        class_id, data.meeting_platform, data.meeting_url
    )

    await AuditService(db).log_action(
        actor_user=current_user,
        action="course_class_meeting_link_updated",
        entity_type="course_class",
        entity_id=class_id,
        entity_label=course_class["name"],
        request=request,
        metadata={"meeting_platform": data.meeting_platform},
    )
    return result


# ── Teacher endpoints ───────────────────────────────────────────────────────

@router.get("/teachers/me/classes")
async def list_teacher_classes(
    current_user=Depends(require_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """List classes assigned to the current teacher."""
    from app.models.user import Teacher
    from sqlalchemy import select
    t_result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = t_result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=403, detail="Teacher profile not found")

    svc = CourseClassService(db)
    return {"items": await svc.get_classes_for_teacher(teacher.id)}


@router.get("/course-classes/{class_id}/students")
async def list_class_students(
    class_id: UUID,
    current_user=Depends(require_admin_or_coordinator_or_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """List active students enrolled in a class (admin, coordinator, or assigned teacher)."""
    from app.models.user import Teacher
    from sqlalchemy import select

    svc = CourseClassService(db)
    course_class = await svc.get_class(class_id)
    if not course_class:
        raise HTTPException(status_code=404, detail="Class not found")

    user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()
    is_admin = "admin" in user_roles
    is_coordinator = "coordinator" in user_roles

    if not is_admin and not is_coordinator:
        # Teacher must be assigned to this class
        t_result = await db.execute(
            select(Teacher).where(Teacher.user_id == current_user.id)
        )
        teacher = t_result.scalar_one_or_none()
        if not teacher or str(course_class.get("teacher_id")) != str(teacher.id):
            raise HTTPException(status_code=403, detail="You are not assigned to this class")

    return {"items": await svc.list_students_by_class(class_id)}
