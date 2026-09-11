"""
CodeAcademy Pro — Teachers Router
Manage teacher role logic per admin requirements.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.rbac import get_teacher_profile, require_admin, require_teacher
from app.models.user import User, UserRole, Teacher
from app.models.course import Course
from app.repositories.user_repository import UserRepository, RoleRepository
from app.services.audit_service import AuditService
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService

router = APIRouter()

class TeacherUpdate(BaseModel):
    first_name: str | None = Field(None, min_length=2, max_length=120)
    last_name: str | None = Field(None, min_length=2, max_length=120)
    is_active: bool | None = None


# ── Panel del docente (`/teachers/me/...`) ────────────────────────────────────
# Van antes de las rutas con `{user_id}` para que "me" nunca se interprete como
# un UUID.


@router.get("/me/courses")
async def list_my_courses(
    current_user=Depends(require_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """
    Cursos asignados al docente actual, con los conteos de su panel.

    Cuenta como curso propio el que tiene asignado como titular (`courses.teacher_id`)
    y también aquel donde solo imparte alguna clase (`course_classes.teacher_id`).
    """
    teacher = await get_teacher_profile(db, current_user)
    if not teacher:
        raise HTTPException(status_code=403, detail="Teacher profile not found")

    svc = CourseService(db)
    return {"items": await svc.list_courses_for_teacher(teacher.id)}


@router.get("/me/students")
async def list_my_students(
    current_user=Depends(require_teacher),
    db: AsyncSession = Depends(get_rls_db),
):
    """Alumnos activos de los cursos y clases del docente, con su progreso."""
    teacher = await get_teacher_profile(db, current_user)
    if not teacher:
        raise HTTPException(status_code=403, detail="Teacher profile not found")

    svc = EnrollmentService(db)
    return {"items": await svc.list_teacher_students(teacher.id)}


@router.get("")
async def list_teachers(
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """List all active teachers with their profile IDs (for course assignment)."""
    result = await db.execute(
        select(Teacher, User)
        .join(User, User.id == Teacher.user_id)
        .where(Teacher.is_active == True, User.deleted_at.is_(None))
        .order_by(User.last_name, User.first_name)
    )
    items = []
    for teacher, user in result.all():
        items.append({
            "id": str(teacher.id),
            "user_id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
    return {"items": items}


@router.get("/eligible-users")
async def list_eligible_users(
    search: str | None = Query(None, description="Search by name or email"),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """List users who are NOT yet teachers (eligible for teacher assignment)."""
    # Subquery: user_ids that already have a Teacher profile
    teacher_user_ids = select(Teacher.user_id)
    
    query = (
        select(User)
        .where(User.deleted_at.is_(None))
        .where(User.id.notin_(teacher_user_ids))
        .order_by(User.created_at.desc())
    )
    
    if search:
        from sqlalchemy import or_
        search_filter = or_(
            User.first_name.ilike(f"%{search}%"),
            User.last_name.ilike(f"%{search}%"),
            User.email.ilike(f"%{search}%"),
            User.username.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
    
    result = await db.execute(query.limit(50))
    users = result.scalars().all()
    
    return {
        "items": [
            {
                "id": str(u.id),
                "email": u.email,
                "username": u.username,
                "first_name": u.first_name,
                "last_name": u.last_name,
                "status": u.status,
            }
            for u in users
        ]
    }


@router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def assign_teacher_role(
    user_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Assign the teacher role to an existing user. Activates them automatically."""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    teacher_role = await role_repo.get_by_name("teacher")
    if not teacher_role:
        raise HTTPException(status_code=500, detail="Teacher role not configured in DB")
        
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == teacher_role.id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="User is already a teacher")
        
    db.add(UserRole(user_id=user.id, role_id=teacher_role.id))
    
    # Create Teacher record if not exists
    teacher_record = await db.execute(select(Teacher).where(Teacher.user_id == user.id))
    if not teacher_record.scalar_one_or_none():
        db.add(Teacher(user_id=user.id, is_active=True))
    
    # Activate the user
    user.status = "active"

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="teacher_assigned",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
        metadata={"role": "teacher"},
    )
        
    await db.commit()

    return {
        "message": "Teacher role assigned and profile created successfully",
        "user_id": str(user.id),
        "status": "active",
    }


@router.put("/{user_id}")
async def update_teacher(
    user_id: UUID,
    data: TeacherUpdate,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update teacher details (first_name, last_name, is_active). Must be a teacher."""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    
    user = await user_repo.get_by_id_lite(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    teacher_role = await role_repo.get_by_name("teacher")
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == teacher_role.id
        )
    )
    teacher_record_q = await db.execute(select(Teacher).where(Teacher.user_id == user.id))
    teacher = teacher_record_q.scalar_one_or_none()
    if not teacher:
        raise HTTPException(status_code=400, detail="User has teacher role but no teacher profile")

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.is_active is not None:
        teacher.is_active = data.is_active
        
    await user_repo.update(user)
    await db.commit()

    await AuditService(db).log_action(
        actor_user=current_user,
        action="teacher_updated",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
        metadata={"updated_fields": list(data.model_dump(exclude_unset=True).keys())},
    )

    return {
        "id": str(user.id),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_active": teacher.is_active,
    }


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_teacher(
    user_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Remove teacher role. Fails if the teacher has any courses."""
    user_repo = UserRepository(db)
    role_repo = RoleRepository(db)
    
    user = await user_repo.get_by_id_lite(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    teacher_role = await role_repo.get_by_name("teacher")
    
    result = await db.execute(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == teacher_role.id
        )
    )
    user_role = result.scalar_one_or_none()
    if not user_role:
        raise HTTPException(status_code=400, detail="User is not a teacher")
        
    teacher_record_q = await db.execute(select(Teacher).where(Teacher.user_id == user.id))
    teacher = teacher_record_q.scalar_one_or_none()
    
    if teacher:
        await db.delete(teacher)

    await db.delete(user_role)

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="teacher_removed",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
        metadata={"role": "teacher"},
    )

    await db.commit()
