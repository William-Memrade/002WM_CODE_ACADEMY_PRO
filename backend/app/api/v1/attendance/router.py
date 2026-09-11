"""
CodeAcademy Pro — Attendance Router
Endpoints for attendance records.
"""

from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.rls import get_rls_db
from app.middlewares.rbac import require_admin, require_teacher, require_student_or_pending
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate
from app.services.course_class_service import AttendanceService, CourseClassService
from app.services.audit_service import AuditService
from app.services.enrollment_service import EnrollmentService

router = APIRouter()


@router.post("/course-classes/{class_id}/attendance", status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    class_id: UUID,
    data: AttendanceCreate,
    request: Request,
    current_user=Depends(require_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Mark attendance for a student in a class (teacher only, must be assigned)."""
    from app.models.user import Teacher
    from sqlalchemy import select

    t_result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = t_result.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=403, detail="Teacher profile not found")

    svc = CourseClassService(db)
    course_class = await svc.get_class(class_id)
    if not course_class:
        raise HTTPException(status_code=404, detail="Class not found")
    if str(course_class.get("teacher_id")) != str(teacher.id):
        raise HTTPException(status_code=403, detail="You are not assigned to this class")

    # Verify student is enrolled in this class
    if not await svc.is_student_enrolled(class_id, data.student_id):
        raise HTTPException(
            status_code=400,
            detail="El estudiante no está inscrito en esta clase.",
        )

    att_svc = AttendanceService(db)
    result = await att_svc.mark_attendance(
        course_class_id=class_id,
        student_id=data.student_id,
        teacher_id=teacher.id,
        session_date=data.session_date,
        status=data.status,
        notes=data.notes,
    )

    await AuditService(db).log_action(
        actor_user=current_user,
        action="attendance_marked",
        entity_type="attendance",
        entity_id=result["id"],
        request=request,
        metadata={
            "course_class_id": str(class_id),
            "student_id": str(data.student_id),
            "status": data.status,
        },
    )
    return result


@router.get("/course-classes/{class_id}/attendance")
async def list_class_attendance(
    class_id: UUID,
    current_user=Depends(require_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """List attendance records for a class (teacher assigned or admin)."""
    from app.models.user import Teacher
    from sqlalchemy import select

    t_result = await db.execute(
        select(Teacher).where(Teacher.user_id == current_user.id)
    )
    teacher = t_result.scalar_one_or_none()

    svc = CourseClassService(db)
    course_class = await svc.get_class(class_id)
    if not course_class:
        raise HTTPException(status_code=404, detail="Class not found")

    # Allow if teacher is assigned or user is admin
    user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()
    is_admin = "admin" in user_roles
    if not is_admin and (not teacher or str(course_class.get("teacher_id")) != str(teacher.id)):
        raise HTTPException(status_code=403, detail="You are not assigned to this class")

    att_svc = AttendanceService(db)
    return {"items": await att_svc.list_class_attendance(class_id)}


@router.get("/students/me/attendance")
async def list_my_attendance(
    current_user=Depends(require_student_or_pending),
    db: AsyncSession = Depends(get_rls_db),
):
    """List own attendance records (student)."""
    att_svc = AttendanceService(db)
    return {"items": await att_svc.list_student_attendance(current_user.id)}


@router.get("/students/me/classes")
async def list_my_classes(
    current_user=Depends(require_student_or_pending),
    db: AsyncSession = Depends(get_rls_db),
):
    """List classes where the current student is actively enrolled (includes meeting_url)."""
    svc = CourseClassService(db)
    return {"items": await svc.get_classes_for_student(current_user.id)}


@router.get("/students/me/progress")
async def list_my_progress(
    current_user=Depends(require_student_or_pending),
    db: AsyncSession = Depends(get_rls_db),
):
    """
    Progreso propio, una fila por curso inscrito.

    El alumno solo lo consulta: lo edita el docente de su clase desde
    `PATCH /course-classes/{class_id}/students/{student_id}/progress`.
    """
    svc = EnrollmentService(db)
    return {"items": await svc.list_student_progress(current_user.id)}


@router.patch("/attendance/{attendance_id}")
async def update_attendance(
    attendance_id: UUID,
    data: AttendanceUpdate,
    request: Request,
    current_user=Depends(require_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update an attendance record (teacher or admin, must be assigned to the class)."""
    att_svc = AttendanceService(db)

    # Fetch the record to verify class ownership
    record_obj = await att_svc.repo.get_by_id(attendance_id)
    if not record_obj:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    # Verify teacher is assigned to this class or is admin
    user_roles = set(current_user.role_names) if hasattr(current_user, "role_names") else set()
    is_admin = "admin" in user_roles
    if not is_admin:
        from app.models.user import Teacher
        from sqlalchemy import select
        t_result = await db.execute(select(Teacher).where(Teacher.user_id == current_user.id))
        teacher = t_result.scalar_one_or_none()
        if not teacher:
            raise HTTPException(status_code=403, detail="Teacher profile not found")

        svc = CourseClassService(db)
        course_class = await svc.get_class(record_obj.course_class_id)
        if not course_class or str(course_class.get("teacher_id")) != str(teacher.id):
            raise HTTPException(status_code=403, detail="You are not assigned to this class")

    record = await att_svc.update_attendance(
        attendance_id, data.status or "present", data.notes
    )

    await AuditService(db).log_action(
        actor_user=current_user,
        action="attendance_updated",
        entity_type="attendance",
        entity_id=attendance_id,
        request=request,
        metadata={"status": data.status, "notes": data.notes},
    )
    return record
