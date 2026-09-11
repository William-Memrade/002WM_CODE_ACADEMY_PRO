"""
CodeAcademy Pro — Users Router
Profile, admin user management (list, filter, create, block/unblock, metrics).
"""

import re
import secrets
import string
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.auth import get_current_user
from app.middlewares.rbac import require_admin
from app.models.user import User, Role, UserRole
from app.models.system import SystemSetting
from app.models.payment import Payment, Enrollment
from app.repositories.user_repository import UserRepository, RoleRepository
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService
from app.services.captcha_service import verify_captcha
from app.services.email_service import send_email
from app.core.config import get_settings
from app.core.password_policy import validate_password as validate_password_policy
from app.core.security import hash_password

settings = get_settings()
router = APIRouter()


# ── Request schemas ───────────────────────────────────────────────────────────

# Roles an admin is allowed to assign when creating a user via the platform.
ALLOWED_ASSIGNMENT_ROLES = ("teacher", "admin")


class CreateUserRequest(BaseModel):
    """POST /users/admin/users request body.

    The admin provides only the user's name and email and picks a role
    restricted to Docente (`teacher`) or Admin (`admin`). A temporary password
    is generated server-side and emailed to the new user, who is forced to
    change it on first login.
    """
    email: EmailStr
    first_name: str = Field(..., min_length=2, max_length=120)
    last_name: str = Field("", max_length=120)
    role: str = Field(..., description="teacher (Docente) | admin (Admin)")
    captcha_token: str | None = Field(None, description="Google reCAPTCHA response token")

    @field_validator("first_name")
    @classmethod
    def validate_first_name(cls, v: str) -> str:
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]{2,120}$", v):
            raise ValueError("El nombre debe contener solo letras y espacios (2-120 caracteres)")
        return v.strip()

    @field_validator("last_name")
    @classmethod
    def validate_last_name(cls, v: str) -> str:
        if v and not re.match(r"^[a-zA-ZÀ-ÿ\s]{0,120}$", v):
            raise ValueError("El apellido debe contener solo letras y espacios")
        return v.strip()

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = (v or "").strip().lower()
        if v not in ALLOWED_ASSIGNMENT_ROLES:
            raise ValueError(
                "El rol asignable solo puede ser 'teacher' (Docente) o 'admin' (Admin)"
            )
        return v


class ChangeTempPasswordRequest(BaseModel):
    """POST /users/me/change-temp-password request body.

    Forced flow used by users created by an admin with a temporary password.
    Validates that `new_password` matches the platform password policy and that
    it is confirmed by `confirm_password`.
    """
    new_password: str = Field(..., min_length=8, max_length=50)
    confirm_password: str = Field(..., min_length=8, max_length=50)
    captcha_token: str | None = Field(None, description="Google reCAPTCHA response token")

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        return validate_password_policy(v)


# ── Helpers ───────────────────────────────────────────────────────────────────

_USERNAME_ALLOWED_RE = re.compile(r"[^a-zA-Z0-9_]")


def _generate_username(base: str) -> str:
    """Derive a valid, unique-looking username from an email local part.

    A random suffix is appended to avoid collisions while keeping the regex
    constraint `^[a-zA-Z0-9_]{3,30}$`.
    """
    sanitized = _USERNAME_ALLOWED_RE.sub("_", base)[:22] or "user"
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    candidate = f"{sanitized}_{suffix}"
    return candidate[:30]


def _generate_temp_password(length: int = 14) -> str:
    """Generate a random temporary password that satisfies the platform policy.

    Guarantees at least one uppercase letter, one digit and one special char
    from `[_!?*]`.
    """
    upper = secrets.choice(string.ascii_uppercase)
    digit = secrets.choice(string.digits)
    special = secrets.choice("_!?*")
    rest_alphabet = string.ascii_letters + string.digits + "_!?*"
    rest = "".join(secrets.choice(rest_alphabet) for _ in range(length - 3))
    pwd = upper + digit + special + rest
    # Shuffle so the guaranteed chars are not always at the start.
    pwd_list = list(pwd)
    secrets.SystemRandom().shuffle(pwd_list)
    return "".join(pwd_list)


async def _get_academy_name(db: AsyncSession) -> str:
    """Return the public academy/platform name from DB, falling back to APP_NAME env."""
    result = await db.execute(
        select(SystemSetting.value).where(SystemSetting.key == "app_name")
    )
    value = result.scalar_one_or_none()
    return value or settings.APP_NAME


# ── Profile Endpoints ─────────────────────────────────────────────────────────


@router.get("/me")
async def get_my_profile(current_user=Depends(get_current_user)):
    """Get current user's profile."""
    return AuthService.user_to_brief(current_user)


@router.put("/me")
async def update_my_profile(
    first_name: str | None = None,
    last_name: str | None = None,
    phone: str | None = None,
    bio: str | None = None,
    request: Request = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Update current user's profile."""
    repo = UserRepository(db)
    if first_name:
        current_user.first_name = first_name
    if last_name:
        current_user.last_name = last_name
    if phone is not None:
        current_user.phone = phone
    if bio is not None:
        current_user.bio = bio

    await repo.update(current_user)

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="user_updated",
        entity_type="user",
        entity_id=current_user.id,
        entity_label=current_user.email,
        request=request,
        metadata={"fields_changed": [k for k, v in [("first_name", first_name), ("last_name", last_name), ("phone", phone), ("bio", bio)] if v is not None]},
    )
    return AuthService.user_to_brief(current_user)


# ── Admin Endpoints ───────────────────────────────────────────────────────────


@router.get("/admin/metrics")
async def admin_metrics(
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Get admin dashboard metrics — consolidated into minimal queries, cached 30s."""
    from app.core.cache import cache
    from app.models.course import Course

    async def _fetch_metrics():
        # All counts in one round-trip using scalar subqueries
        total_students = (
            select(func.count())
            .select_from(User)
            .join(User.user_roles)
            .join(UserRole.role)
            .where(Role.name == "student")
            .where(User.deleted_at.is_(None))
            .correlate(None)
            .scalar_subquery()
        )
        total_teachers = (
            select(func.count())
            .select_from(User)
            .join(User.user_roles)
            .join(UserRole.role)
            .where(Role.name == "teacher")
            .where(User.deleted_at.is_(None))
            .correlate(None)
            .scalar_subquery()
        )
        total_courses = (
            select(func.count())
            .select_from(Course)
            .where(Course.deleted_at.is_(None))
            .correlate(None)
            .scalar_subquery()
        )
        active_courses = (
            select(func.count())
            .select_from(Course)
            .where(Course.is_active == True)
            .where(Course.deleted_at.is_(None))
            .correlate(None)
            .scalar_subquery()
        )
        pending_payments = (
            select(func.count())
            .select_from(Payment)
            .where(Payment.status == "pending")
            .correlate(None)
            .scalar_subquery()
        )
        total_revenue = (
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.status == "approved")
            .correlate(None)
            .scalar_subquery()
        )
        pending_users = (
            select(func.count())
            .select_from(User)
            .where(User.status == "pending")
            .where(User.deleted_at.is_(None))
            .correlate(None)
            .scalar_subquery()
        )

        result = await db.execute(
            select(
                total_students.label("total_students"),
                total_teachers.label("total_teachers"),
                total_courses.label("total_courses"),
                active_courses.label("active_courses"),
                pending_payments.label("pending_payments"),
                total_revenue.label("total_revenue"),
                pending_users.label("pending_users"),
            )
        )
        row = result.one()

        return {
            "total_students": row.total_students or 0,
            "total_teachers": row.total_teachers or 0,
            "total_courses": row.total_courses or 0,
            "active_courses": row.active_courses or 0,
            "pending_payments": row.pending_payments or 0,
            "total_revenue": float(row.total_revenue or 0),
            "pending_users": row.pending_users or 0,
        }

    return await cache.get_or_set("admin:metrics", _fetch_metrics, ttl_seconds=30)


@router.get("/admin/users")
async def admin_list_users(
    role: str | None = Query(None, description="Filter by role: student, teacher, admin"),
    search: str | None = Query(None, description="Search by name or email"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """List all users with optional role/search filter (admin)."""
    skip = (page - 1) * per_page

    query = (
        select(User)
        .options(selectinload(User.user_roles).selectinload(UserRole.role))
        .where(User.deleted_at.is_(None))
    )
    count_query = select(func.count()).select_from(User).where(User.deleted_at.is_(None))

    if role:
        query = query.join(User.user_roles).join(UserRole.role).where(Role.name == role)
        count_query = count_query.join(User.user_roles).join(UserRole.role).where(Role.name == role)

    if search:
        from sqlalchemy import or_
        safe_search = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        search_filter = or_(
            User.first_name.ilike(f"%{safe_search}%", escape="\\"),
            User.last_name.ilike(f"%{safe_search}%", escape="\\"),
            User.email.ilike(f"%{safe_search}%", escape="\\"),
            User.username.ilike(f"%{safe_search}%", escape="\\"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(User.created_at.desc()).offset(skip).limit(per_page)
    result = await db.execute(query)
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
                "is_blocked": u.is_blocked,
                "email_verified": u.email_verified,
                "force_change_password": getattr(u, "force_change_password", False),
                "roles": [ur.role.name for ur in u.user_roles if ur.role],
                "created_at": u.created_at.isoformat() if u.created_at else None,
            }
            for u in users
        ],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


@router.post("/admin/users", status_code=201)
async def admin_create_user(
    data: CreateUserRequest,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Create a new user assigned to Docente (`teacher`) or Admin (`admin`).

    The admin supplies only the user's name and email plus the role. A temporary
    password is generated server-side, the user is flagged with
    `force_change_password=True`, and an assignment email is sent. The new user
    can log in with the temp password but is forced to set a new one on first
    login. A reCAPTCHA token is validated to confirm the admin is human.
    """
    # 1. Captcha validation (human confirmation for this privileged action).
    if not await verify_captcha(data.captcha_token):
        raise HTTPException(status_code=400, detail="Validación captcha fallida")

    repo = UserRepository(db)
    role_repo = RoleRepository(db)

    # 2. Email uniqueness.
    if await repo.email_exists(data.email):
        raise HTTPException(status_code=409, detail="El correo electrónico ya está registrado")

    # 3. Derive a unique username (the admin does not provide one).
    local_part = data.email.split("@", 1)[0]
    username = _generate_username(local_part)
    # Defensive: in the unlikely event of a collision, retry with a fresh suffix.
    for _ in range(3):
        if not await repo.username_exists(username):
            break
        username = _generate_username(local_part)
    if await repo.username_exists(username):
        raise HTTPException(status_code=500, detail="No se pudo generar un nombre de usuario único")

    # 4. Resolve the assigned role (already validated by schema to be teacher|admin).
    assigned_role = await role_repo.get_by_name(data.role)
    if not assigned_role:
        raise HTTPException(status_code=400, detail=f"El rol '{data.role}' no existe")

    # 5. Generate a temporary password that complies with the password policy.
    temp_password = _generate_temp_password()

    user = User(
        email=data.email,
        username=username,
        password_hash=hash_password(temp_password),
        first_name=data.first_name,
        last_name=data.last_name,
        status="active",
        email_verified=True,  # Admin-created users are pre-verified
        force_change_password=True,  # Forced password change on first login
    )
    user = await repo.create(user)
    db.add(UserRole(user_id=user.id, role_id=assigned_role.id))
    await db.flush()

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="user_created",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
        metadata={
            "assigned_role": data.role,
            "source": "admin_creation",
            "force_change_password": True,
        },
    )

    await db.commit()

    # 6. Send the assignment email with academy name + temp credentials.
    academy_name = await _get_academy_name(db)
    await send_email(
        to_email=user.email,
        template="user_assignment",
        template_data={
            "app_name": academy_name,
            "first_name": user.first_name,
            "email": user.email,
            "temp_password": temp_password,
        },
    )

    # Invalidate admin metrics cache since user counts changed
    from app.core.cache import cache
    await cache.delete("admin:metrics")

    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": data.role,
        "message": f"Usuario creado con rol '{data.role}'. Se envió un correo con la contraseña temporal.",
    }


@router.post("/me/change-temp-password")
async def change_temp_password(
    data: ChangeTempPasswordRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Force-change the temporary password set during admin-created user flow.

    Only callable by users flagged with `force_change_password=True`. Validates
    captcha, password policy, and that `confirm_password` matches, then stores
    the new hash and clears the force flag.
    """
    if not getattr(current_user, "force_change_password", False):
        raise HTTPException(
            status_code=403,
            detail="No se requiere cambio de contraseña temporal para este usuario",
        )

    # 1. Captcha validation.
    if not await verify_captcha(data.captcha_token):
        raise HTTPException(status_code=400, detail="Validación captcha fallida")

    # 2. Confirm password matches.
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="La confirmación de contraseña no coincide")

    # 3. Update password hash and clear the force flag.
    repo = UserRepository(db)
    current_user.password_hash = hash_password(data.new_password)
    current_user.force_change_password = False
    await repo.update(current_user)

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="temp_password_changed",
        entity_type="user",
        entity_id=current_user.id,
        entity_label=current_user.email,
        request=request,
        metadata={"source": "forced_change_flow"},
    )

    await db.commit()

    return {"message": "Contraseña actualizada correctamente"}


@router.patch("/admin/users/{user_id}/block")
async def block_user(
    user_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Block a user (admin)."""
    repo = UserRepository(db)
    user = await repo.get_by_id_lite(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_blocked = True
    await repo.update(user)

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="user_blocked",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
    )
    return {"id": str(user.id), "is_blocked": True, "message": "User blocked"}


@router.patch("/admin/users/{user_id}/unblock")
async def unblock_user(
    user_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Unblock a user (admin)."""
    repo = UserRepository(db)
    user = await repo.get_by_id_lite(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_blocked = False
    await repo.update(user)

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="user_unblocked",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
    )
    return {"id": str(user.id), "is_blocked": False, "message": "User unblocked"}


@router.patch("/admin/users/{user_id}/approve")
async def approve_user(
    user_id: UUID,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Approve a pending user, marking them active."""
    repo = UserRepository(db)
    user = await repo.get_by_id_lite(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    previous_status = user.status
    user.status = "active"
    await repo.update(user)

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="user_activated",
        entity_type="user",
        entity_id=user.id,
        entity_label=user.email,
        request=request,
        metadata={"previous_status": previous_status, "new_status": "active"},
    )

    # Invalidate metrics cache since pending_users count changed
    from app.core.cache import cache
    await cache.delete("admin:metrics")

    return {"id": str(user.id), "status": "active", "message": "User approved and active"}
