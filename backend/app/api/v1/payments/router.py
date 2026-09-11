"""
CodeAcademy Pro — Payments Router
New flow: Student submits payment proof → Admin approves → Enrollment created.
NO enrollment is created before admin approval.
"""
import re
import uuid as uuid_mod
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Query, Request, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.auth import get_current_user
from app.middlewares.rbac import require_admin, require_student_or_pending, require_admin_or_coordinator
from app.middlewares.rate_limit import upload_rate_limit
from app.models.payment import Payment, Enrollment, PaymentProof
from app.models.user import User, Student, UserRole
from app.models.course import Course
from app.repositories.user_repository import RoleRepository
from app.schemas.payment import PaymentSettingsRequest, PaymentApproveRequest, PaymentRejectRequest, AssignClassRequest
from app.services.audit_service import AuditService

router = APIRouter()

# ── Config ────────────────────────────────────────────────────────────────────

UPLOAD_DIR = Path("uploads/proofs")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

# QR Code uploads
QR_UPLOAD_DIR = Path("uploads/qr")
QR_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
QR_MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB for QR codes
QR_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/svg+xml"}
QR_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".svg"}


# ── Helpers ──────────────────────────────────────────────────────────────────

def _sanitize_filename(filename: str) -> str:
    """Remove unsafe characters from filenames."""
    name = re.sub(r'[^\w\-.]', '_', filename)
    return name[:200]  # Limit length


def _validate_image_magic_bytes(content: bytes) -> str | None:
    """Check real file type via magic bytes."""
    if content[:3] == b'\xff\xd8\xff':
        return "image/jpeg"
    if content[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    return None

SVG_DANGEROUS_PATTERN = re.compile(
    r"(<script\b|javascript:|onload=|onerror=|<iframe\b|<object\b|<embed\b)",
    re.IGNORECASE,
)


def _validate_svg_content(content: bytes) -> bool:
    """Perform a lightweight safety check on SVG upload content."""
    text = content.decode("utf-8", errors="ignore").lower()
    if "<svg" not in text:
        return False
    if SVG_DANGEROUS_PATTERN.search(text):
        return False
    return True


def _build_qr_url(filename: str) -> str:
    return f"/api/v1/payments/qr/{filename}"


def _extract_filename_from_url(url: str | None) -> str | None:
    if not url:
        return None
    return Path(url).name


def _delete_qr_file_by_url(url: str | None) -> None:
    filename = _extract_filename_from_url(url)
    if not filename:
        return
    path = QR_UPLOAD_DIR / filename
    if path.exists():
        path.unlink()


async def _get_payment_settings(db: AsyncSession):
    from app.models.payment import PaymentSettings

    result = await db.execute(select(PaymentSettings).limit(1))
    return result.scalar_one_or_none()


def _payment_to_dict(payment: Payment) -> dict:
    # Always use direct relationships (course_id and student_id are always set on Payment)
    course = payment.course
    student_user = payment.student_user

    return {
        "id": str(payment.id),
        "enrollment_id": str(payment.enrollment_id) if payment.enrollment_id else None,
        "course_id": str(payment.course_id),
        "amount": float(payment.amount),
        "currency": payment.currency,
        "payment_method": payment.payment_method,
        "status": payment.status,
        "payment_plan": payment.payment_plan,
        "expected_amount": float(payment.expected_amount) if payment.expected_amount else None,
        "monthly_amount": float(payment.monthly_amount) if payment.monthly_amount else None,
        "full_amount": float(payment.full_amount) if payment.full_amount else None,
        "duration_months": payment.duration_months,
        "reference_number": payment.reference_number,
        "reviewed_at": payment.reviewed_at.isoformat() if payment.reviewed_at else None,
        "review_notes": payment.review_notes,
        "created_at": payment.created_at.isoformat() if payment.created_at else None,
        "student": {
            "id": str(student_user.id),
            "full_name": f"{student_user.first_name} {student_user.last_name}",
            "email": student_user.email,
        } if student_user else None,
        "course": {
            "id": str(course.id),
            "title": course.title,
            "slug": course.slug,
        } if course else None,
        "proofs": [
            {"id": str(p.id), "file_url": f"/payments/proofs/{p.id}/view", "file_name": p.file_name}
            for p in payment.proofs
        ] if payment.proofs else [],
    }


async def _get_payment_full(db: AsyncSession, payment_id: UUID) -> Payment | None:
    """Load a payment with student, course, and proofs."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.enrollment)
            .selectinload(Enrollment.student),
            selectinload(Payment.enrollment)
            .selectinload(Enrollment.course),
            selectinload(Payment.proofs),
            selectinload(Payment.course),
            selectinload(Payment.student_user),
        )
        .where(Payment.id == payment_id)
    )
    return result.scalar_one_or_none()


# ── Public: Payment Info ──────────────────────────────────────────────────────


@router.get("/payment-info")
async def get_payment_info(db: AsyncSession = Depends(get_db)):
    """Get bank transfer payment information from payment_settings (public, masked account number)."""
    from app.schemas.payment import PaymentSettingsPublicResponse

    settings = await _get_payment_settings(db)
    if settings:
        masked = PaymentSettingsPublicResponse.mask_account_number(settings.account_number)
        from app.models.system import SystemSetting
        cur_result = await db.execute(
            select(SystemSetting.value).where(SystemSetting.key == "default_currency")
        )
        currency = cur_result.scalar_one_or_none() or "USD"
        return {
            "bank_name": settings.bank_name,
            "account_number": masked,
            "account_holder": settings.account_holder,
            "payment_instructions": settings.payment_instructions or "",
            "qr_image_url": settings.qr_image_url or "",
            "currency": currency,
        }

    from app.models.system import SystemSetting
    result = await db.execute(
        select(SystemSetting).where(
            SystemSetting.key.in_([
                "payment_bank_name",
                "payment_bank_account",
                "payment_bank_account_type",
                "payment_bank_holder",
                "payment_bank_holder_type",
                "payment_instructions",
                "payment_qr_url",
                "default_currency",
            ]),
            SystemSetting.is_public,
        )
    )
    settings_rows = result.scalars().all()
    info = {s.key: s.value for s in settings_rows}
    raw_account = info.get("payment_bank_account", "")
    masked = PaymentSettingsPublicResponse.mask_account_number(raw_account)
    return {
        "bank_name": info.get("payment_bank_name", ""),
        "account_number": masked,
        "account_type": info.get("payment_bank_account_type", ""),
        "account_holder": info.get("payment_bank_holder", ""),
        "holder_type": info.get("payment_bank_holder_type", ""),
        "payment_instructions": info.get("payment_instructions", ""),
        "qr_url": info.get("payment_qr_url", ""),
        "currency": info.get("default_currency", "USD"),
    }


# ── Student: Submit Payment Proof ─────────────────────────────────────────────


@router.post("/submit-proof", status_code=201, dependencies=[Depends(upload_rate_limit)])
async def submit_payment_proof(
    request: Request,
    course_id: str = Form(..., description="UUID of the course to pay for"),
    payment_plan: str = Form("monthly", description="Payment plan: monthly or full"),
    file: UploadFile = File(..., description="Payment proof image (JPG/PNG, max 5MB)"),
    current_user=Depends(require_student_or_pending),
    db: AsyncSession = Depends(get_rls_db),
):
    """
    Student submits a payment proof for a course.
    Creates a Payment record with status 'pending' (NO enrollment yet).
    Enrollment is only created when admin approves.
    """
    # Validate payment_plan
    if payment_plan not in ("monthly", "full"):
        raise HTTPException(status_code=400, detail="Plan de pago inválido. Usa 'monthly' o 'full'.")

    # Parse course_id
    try:
        course_uuid = UUID(course_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID de curso inválido")

    # Validate course exists and is active
    course_result = await db.execute(
        select(Course).where(
            Course.id == course_uuid,
            Course.is_active,
            Course.deleted_at.is_(None),
        )
    )
    course = course_result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Curso no encontrado o no disponible")

    # Check for existing pending payment for same course by same user
    existing = await db.execute(
        select(Payment).where(
            Payment.student_id == current_user.id,
            Payment.course_id == course_uuid,
            Payment.status.in_(["pending", "pending_proof"]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Ya tienes un comprobante pendiente de revisión para este curso",
        )

    # Also check if already enrolled and active
    existing_enrollment = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_uuid,
            Enrollment.status == "active",
        )
    )
    if existing_enrollment.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Ya estás inscrito en este curso")

    # Validate file extension
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nombre de archivo requerido")
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato no permitido. Usa: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read file content and validate size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Archivo muy grande. Máximo: {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Validate real MIME type via magic bytes
    real_mime = _validate_image_magic_bytes(content)
    if not real_mime or real_mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="El archivo no es una imagen válida (JPG o PNG)",
        )

    # Save file to disk with unique name
    safe_name = _sanitize_filename(file.filename)
    unique_name = f"{uuid_mod.uuid4().hex}_{safe_name}"
    file_path = UPLOAD_DIR / unique_name

    with open(file_path, "wb") as f:
        f.write(content)

    # Compute payment amounts based on course pricing
    total_price = float(course.price)
    duration_months = course.duration_months or 1
    discount_pct = float(course.full_payment_discount_pct or 0)
    monthly_amount = round(total_price / duration_months, 2) if duration_months else total_price
    full_amount = round(total_price * (1 - discount_pct / 100), 2)
    expected_amount = full_amount if payment_plan == "full" else monthly_amount

    # Create payment record (NO enrollment — that happens on approval)
    payment = Payment(
        student_id=current_user.id,
        course_id=course_uuid,
        enrollment_id=None,
        amount=expected_amount,
        currency=course.currency,
        payment_method="bank_transfer",
        status="pending",
        payment_plan=payment_plan,
        expected_amount=expected_amount,
        monthly_amount=monthly_amount,
        full_amount=full_amount,
        duration_months=duration_months,
    )
    db.add(payment)
    await db.flush()

    # Create proof record
    proof = PaymentProof(
        payment_id=payment.id,
        file_url=str(file_path),
        file_name=safe_name,
        file_size=len(content),
        mime_type=real_mime,
    )
    db.add(proof)
    await db.commit()

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="payment_proof_uploaded",
        entity_type="payment",
        entity_id=payment.id,
        entity_label=f"Payment {payment.id}",
        request=request,
        metadata={"course_id": str(course_uuid), "file_name": safe_name, "file_size": len(content), "payment_plan": payment_plan, "expected_amount": expected_amount},
    )

    return {
        "payment_id": str(payment.id),
        "course": course.title,
        "amount": expected_amount,
        "payment_plan": payment_plan,
        "status": "pending",
        "message": "Comprobante enviado. Tu pago será revisado por un administrador.",
    }


# ── Admin: List Payments ──────────────────────────────────────────────────────


@router.get("/admin/list")
async def admin_list_payments(
    status: str | None = Query(None, description="Filter: pending, approved, rejected"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """List all payments (admin), optionally filtered by status."""
    skip = (page - 1) * per_page

    query = (
        select(Payment)
        .options(
            selectinload(Payment.enrollment).selectinload(Enrollment.student),
            selectinload(Payment.enrollment).selectinload(Enrollment.course),
            selectinload(Payment.course),
            selectinload(Payment.student_user),
            selectinload(Payment.proofs),
        )
        .order_by(Payment.created_at.desc())
    )
    count_query = select(func.count()).select_from(Payment)

    if status:
        query = query.where(Payment.status == status)
        count_query = count_query.where(Payment.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset(skip).limit(per_page)
    result = await db.execute(query)
    payments = result.scalars().all()

    return {
        "items": [_payment_to_dict(p) for p in payments],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
    }


# ── Admin: Approve Payment ────────────────────────────────────────────────────


@router.post("/{payment_id}/approve")
async def approve_payment(
    payment_id: UUID,
    body: PaymentApproveRequest,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """
    Approve payment → Find class with capacity → Create enrollment → Activate student access.
    This is the ONLY place enrollments are created.
    If no class has capacity, marks payment as approved_pending_class for coordinator action.
    """
    from app.models.course_class import CourseClass
    from app.models.system import SystemSetting

    payment = await _get_payment_full(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != "pending":
        raise HTTPException(status_code=409, detail=f"Payment is already '{payment.status}'")

    now = datetime.now(timezone.utc)

    # ── Find class with capacity (SELECT FOR UPDATE to prevent race conditions) ──
    global_max_result = await db.execute(
        select(SystemSetting.value).where(SystemSetting.key == "global_max_students_per_class")
    )
    global_max_row = global_max_result.scalar_one_or_none()
    global_max = int(global_max_row) if global_max_row else 100

    classes_result = await db.execute(
        select(CourseClass).where(
            CourseClass.course_id == payment.course_id,
            CourseClass.status == "active",
        ).order_by(CourseClass.created_at.asc())
        .with_for_update()
    )
    classes = classes_result.scalars().all()

    selected_class = None
    for cls in classes:
        enrolled_result = await db.execute(
            select(func.count()).select_from(Enrollment).where(
                Enrollment.course_class_id == cls.id,
                Enrollment.status == "active",
            )
        )
        enrolled = enrolled_result.scalar() or 0
        if enrolled < global_max:
            selected_class = cls
            break

    if not selected_class:
        # No class with capacity — mark as approved_pending_class
        payment.status = "approved_pending_class"
        payment.reviewed_by = current_user.id
        payment.reviewed_at = now
        payment.review_notes = body.notes

        audit = AuditService(db)
        await audit.log_action(
            actor_user=current_user,
            action="payment_approved_pending_class",
            entity_type="payment",
            entity_id=payment.id,
            entity_label=f"Payment {payment.id}",
            request=request,
            metadata={
                "amount": float(payment.amount),
                "currency": payment.currency,
                "student_id": str(payment.student_id),
                "course_id": str(payment.course_id),
                "reason": "no_class_capacity",
            },
        )

        await db.commit()

        # Invalidate admin metrics cache
        from app.core.cache import cache
        await cache.delete("admin:metrics")

        return {
            "id": str(payment.id),
            "status": "approved_pending_class",
            "message": "Pago aprobado pero sin cupo disponible. Un coordinador te asignará una clase.",
        }

    # Update payment
    payment.status = "approved"
    payment.reviewed_by = current_user.id
    payment.reviewed_at = now
    payment.review_notes = body.notes

    # CREATE enrollment now with course_class_id
    enrollment = Enrollment(
        student_id=payment.student_id,
        course_id=payment.course_id,
        course_class_id=selected_class.id,
        status="active",
        approved_at=now,
    )
    db.add(enrollment)
    await db.flush()

    # Link payment to enrollment
    payment.enrollment_id = enrollment.id

    # Create Student profile if missing
    student_record_q = await db.execute(
        select(Student).where(Student.user_id == payment.student_id)
    )
    if not student_record_q.scalar_one_or_none():
        db.add(Student(user_id=payment.student_id, enrollment_status="active"))

    # Assign student role if missing
    role_repo = RoleRepository(db)
    student_role = await role_repo.get_by_name("student")
    if student_role:
        role_check = await db.execute(
            select(UserRole).where(
                UserRole.user_id == payment.student_id,
                UserRole.role_id == student_role.id,
            )
        )
        if not role_check.scalar_one_or_none():
            db.add(UserRole(user_id=payment.student_id, role_id=student_role.id))

    # Activate user status if still pending
    student_user_q = await db.execute(
        select(User).where(User.id == payment.student_id)
    )
    student_user = student_user_q.scalar_one_or_none()
    if student_user and student_user.status != "active":
        student_user.status = "active"

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="payment_approved",
        entity_type="payment",
        entity_id=payment.id,
        entity_label=f"Payment {payment.id}",
        request=request,
        metadata={
            "amount": float(payment.amount),
            "currency": payment.currency,
            "student_id": str(payment.student_id),
            "course_id": str(payment.course_id),
            "enrollment_id": str(enrollment.id),
            "course_class_id": str(selected_class.id),
        },
    )
    await audit.log_action(
        actor_user=current_user,
        action="enrollment_created",
        entity_type="enrollment",
        entity_id=enrollment.id,
        entity_label=f"Enrollment {enrollment.id}",
        request=request,
        metadata={
            "student_id": str(payment.student_id),
            "course_id": str(payment.course_id),
            "payment_id": str(payment.id),
            "course_class_id": str(selected_class.id),
        },
    )

    await db.commit()

    # Invalidate admin metrics cache
    from app.core.cache import cache
    await cache.delete("admin:metrics")

    return {
        "id": str(payment.id),
        "enrollment_id": str(enrollment.id),
        "course_class_id": str(selected_class.id),
        "status": "approved",
        "message": "Pago aprobado e inscripción activada",
    }


# ── Admin/Coordinator: Assign Class to Approved-Pending Payment ──────────────


@router.post("/{payment_id}/assign-class")
async def assign_class_to_payment(
    payment_id: UUID,
    body: AssignClassRequest,
    request: Request,
    current_user=Depends(require_admin_or_coordinator),
    db: AsyncSession = Depends(get_rls_db),
):
    """
    Assign a payment in 'approved_pending_class' status to a specific class.
    Creates enrollment only if the class has available capacity.
    """
    from app.models.course_class import CourseClass
    from app.models.system import SystemSetting

    payment = await _get_payment_full(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != "approved_pending_class":
        raise HTTPException(
            status_code=409,
            detail=f"Payment status is '{payment.status}', expected 'approved_pending_class'"
        )

    # Validate the target class exists and belongs to the same course
    class_result = await db.execute(
        select(CourseClass).where(CourseClass.id == body.course_class_id)
    )
    target_class = class_result.scalar_one_or_none()
    if not target_class:
        raise HTTPException(status_code=404, detail="Class not found")
    if target_class.course_id != payment.course_id:
        raise HTTPException(
            status_code=400,
            detail="Class does not belong to the course associated with this payment"
        )
    if target_class.status != "active":
        raise HTTPException(status_code=409, detail="Class is not active")

    # Check for existing active enrollment to avoid duplicates
    existing_enrollment = await db.execute(
        select(Enrollment).where(
            Enrollment.student_id == payment.student_id,
            Enrollment.course_id == payment.course_id,
            Enrollment.status == "active",
        )
    )
    if existing_enrollment.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="Student already has an active enrollment for this course"
        )

    now = datetime.now(timezone.utc)

    # Capacity check with SELECT FOR UPDATE on the class row
    global_max_result = await db.execute(
        select(SystemSetting.value).where(SystemSetting.key == "global_max_students_per_class")
    )
    global_max_row = global_max_result.scalar_one_or_none()
    global_max = int(global_max_row) if global_max_row else 100

    locked_class_result = await db.execute(
        select(CourseClass)
        .where(CourseClass.id == body.course_class_id)
        .with_for_update()
    )
    locked_class = locked_class_result.scalar_one_or_none()
    if not locked_class:
        raise HTTPException(status_code=404, detail="Class not found")

    enrolled_result = await db.execute(
        select(func.count()).select_from(Enrollment).where(
            Enrollment.course_class_id == body.course_class_id,
            Enrollment.status == "active",
        )
    )
    enrolled = enrolled_result.scalar() or 0
    if enrolled >= global_max:
        raise HTTPException(
            status_code=409,
            detail=f"Class is full ({enrolled}/{global_max} enrolled)"
        )

    # CREATE enrollment
    enrollment = Enrollment(
        student_id=payment.student_id,
        course_id=payment.course_id,
        course_class_id=body.course_class_id,
        status="active",
        approved_at=now,
    )
    db.add(enrollment)
    await db.flush()

    # Link payment to enrollment and update status
    payment.status = "approved"
    payment.enrollment_id = enrollment.id

    # Create Student profile if missing
    student_record_q = await db.execute(
        select(Student).where(Student.user_id == payment.student_id)
    )
    if not student_record_q.scalar_one_or_none():
        db.add(Student(user_id=payment.student_id, enrollment_status="active"))

    # Assign student role if missing
    role_repo = RoleRepository(db)
    student_role = await role_repo.get_by_name("student")
    if student_role:
        role_check = await db.execute(
            select(UserRole).where(
                UserRole.user_id == payment.student_id,
                UserRole.role_id == student_role.id,
            )
        )
        if not role_check.scalar_one_or_none():
            db.add(UserRole(user_id=payment.student_id, role_id=student_role.id))

    # Activate user status if still pending
    student_user_q = await db.execute(
        select(User).where(User.id == payment.student_id)
    )
    student_user = student_user_q.scalar_one_or_none()
    if student_user and student_user.status != "active":
        student_user.status = "active"

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="payment_assigned_to_class",
        entity_type="payment",
        entity_id=payment.id,
        entity_label=f"Payment {payment.id}",
        request=request,
        metadata={
            "amount": float(payment.amount),
            "currency": payment.currency,
            "student_id": str(payment.student_id),
            "course_id": str(payment.course_id),
            "course_class_id": str(body.course_class_id),
            "enrollment_id": str(enrollment.id),
        },
    )
    await audit.log_action(
        actor_user=current_user,
        action="enrollment_created",
        entity_type="enrollment",
        entity_id=enrollment.id,
        entity_label=f"Enrollment {enrollment.id}",
        request=request,
        metadata={
            "student_id": str(payment.student_id),
            "course_id": str(payment.course_id),
            "payment_id": str(payment.id),
            "course_class_id": str(body.course_class_id),
        },
    )

    await db.commit()

    # Invalidate admin metrics cache
    from app.core.cache import cache
    await cache.delete("admin:metrics")

    return {
        "id": str(payment.id),
        "enrollment_id": str(enrollment.id),
        "course_class_id": str(body.course_class_id),
        "status": "approved",
        "message": "Estudiante asignado a clase e inscripción activada",
    }


# ── Admin: Reject Payment ────────────────────────────────────────────────────


@router.post("/{payment_id}/reject")
async def reject_payment(
    payment_id: UUID,
    body: PaymentRejectRequest,
    request: Request,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Reject a payment (admin). No enrollment is created."""
    payment = await _get_payment_full(db, payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != "pending":
        raise HTTPException(status_code=409, detail=f"Payment is already '{payment.status}'")

    now = datetime.now(timezone.utc)
    payment.status = "rejected"
    payment.reviewed_by = current_user.id
    payment.reviewed_at = now
    payment.review_notes = body.notes

    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="payment_rejected",
        entity_type="payment",
        entity_id=payment.id,
        entity_label=f"Payment {payment.id}",
        request=request,
        metadata={
            "amount": float(payment.amount),
            "currency": payment.currency,
            "student_id": str(payment.student_id),
            "course_id": str(payment.course_id),
            "review_notes": body.notes,
        },
    )

    await db.commit()

    # Invalidate admin metrics cache
    from app.core.cache import cache
    await cache.delete("admin:metrics")

    return {
        "id": str(payment.id),
        "status": "rejected",
        "message": "Pago rechazado",
    }


# ── Admin: View Proof Image ──────────────────────────────────────────────────


@router.get("/proofs/{proof_id}/view")
async def view_proof(
    proof_id: UUID,
    authorization: str | None = Header(None, description="Authorization: Bearer <token>"),
    db: AsyncSession = Depends(get_db),
):
    """View a payment proof image. Requires Authorization: Bearer <token> header."""
    from app.core.security import decode_token
    from jose import JWTError

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Pass token via Authorization: Bearer <token> header.",
        )

    scheme, _, bearer_token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not bearer_token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format.")

    try:
        payload = decode_token(bearer_token)
        user_id_str = payload.get("sub")
        token_type = payload.get("type")
        if not user_id_str or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    from sqlalchemy import text as sql_text
    roles_result = await db.execute(
        sql_text("SELECT r.name FROM user_roles ur JOIN roles r ON r.id = ur.role_id WHERE ur.user_id = :uid"),
        {"uid": user_id_str},
    )
    user_roles = [row.name for row in roles_result.fetchall()]
    if "admin" not in user_roles:
        raise HTTPException(status_code=403, detail="Admin access required")

    await db.execute(
        sql_text("SELECT set_config('app.current_user_id', :uid, true)"),
        {"uid": user_id_str},
    )
    primary_role = "admin" if "admin" in user_roles else ("teacher" if "teacher" in user_roles else "user")
    await db.execute(
        sql_text("SELECT set_config('app.current_user_role', :role, true)"),
        {"role": primary_role},
    )

    result = await db.execute(
        select(PaymentProof).where(PaymentProof.id == proof_id)
    )
    proof = result.scalar_one_or_none()
    if not proof:
        raise HTTPException(status_code=404, detail="Proof not found")

    file_path = Path(proof.file_url).resolve()
    if not file_path.is_relative_to(UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Proof file not found on disk")

    return FileResponse(
        path=str(file_path),
        media_type=proof.mime_type,
        filename=proof.file_name,
    )


# ── Student: My Payments ──────────────────────────────────────────────────────


@router.get("/my-payments")
async def my_payments(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Student: get own payment history."""
    result = await db.execute(
        select(Payment)
        .options(
            selectinload(Payment.course),
            selectinload(Payment.proofs),
        )
        .where(Payment.student_id == current_user.id)
        .order_by(Payment.created_at.desc())
    )
    payments = result.scalars().all()

    items = []
    for p in payments:
        items.append({
            "id": str(p.id),
            "course_id": str(p.course_id),
            "course_title": p.course.title if p.course else "—",
            "amount": float(p.amount),
            "currency": p.currency,
            "status": p.status,
            "payment_plan": p.payment_plan,
            "expected_amount": float(p.expected_amount) if p.expected_amount else None,
            "monthly_amount": float(p.monthly_amount) if p.monthly_amount else None,
            "full_amount": float(p.full_amount) if p.full_amount else None,
            "duration_months": p.duration_months,
            "created_at": p.created_at.isoformat() if p.created_at else None,
            "reviewed_at": p.reviewed_at.isoformat() if p.reviewed_at else None,
            "review_notes": p.review_notes,
        })

    return {"items": items}


# ── Student: Payment Status ───────────────────────────────────────────────────


@router.get("/{payment_id}/status")
async def payment_status(
    payment_id: UUID,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Get payment status (public by ID) — lightweight."""
    result = await db.execute(
        select(Payment.id, Payment.status).where(Payment.id == payment_id)
    )
    row = result.one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"id": str(row.id), "status": row.status}


# ── Public: Payment Settings ─────────────────────────────────────────────────


@router.get("/settings")
async def get_payment_settings(
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Get current payment settings configuration."""
    from app.schemas.payment import PaymentSettingsResponse

    settings = await _get_payment_settings(db)
    if settings:
        return PaymentSettingsResponse.model_validate(settings)
    return PaymentSettingsResponse()


@router.get("/settings/public")
async def get_payment_settings_public(db: AsyncSession = Depends(get_db)):
    """Get public payment settings for checkout and student views (masked account number)."""
    from app.schemas.payment import PaymentSettingsPublicResponse

    settings = await _get_payment_settings(db)
    if settings:
        masked = PaymentSettingsPublicResponse.mask_account_number(settings.account_number)
        return PaymentSettingsPublicResponse(
            bank_name=settings.bank_name,
            account_number=masked,
            account_holder=settings.account_holder,
            payment_instructions=settings.payment_instructions,
            qr_image_url=settings.qr_image_url,
        )
    return PaymentSettingsPublicResponse()


@router.post("/settings/qr-upload")
async def upload_qr_image(
    request: Request,
    file: UploadFile = File(..., description="QR code image (JPG/PNG/SVG, max 2MB)"),
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Upload QR code image for payment settings."""
    from app.models.payment import PaymentSettings
    from app.schemas.payment import PaymentSettingsResponse
    from sqlalchemy import select, update

    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in QR_ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(QR_ALLOWED_EXTENSIONS)}"
        )

    # Read file content
    content = await file.read()

    # Check file size
    if len(content) > QR_MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {QR_MAX_FILE_SIZE // (1024*1024)}MB"
        )

    # Validate image content for JPG/PNG or SVG payloads
    if file_ext == ".svg":
        if not _validate_svg_content(content):
            raise HTTPException(
                status_code=400,
                detail="Invalid SVG file. The file must contain a valid SVG image without embedded scripts.",
            )
    else:
        real_mime = _validate_image_magic_bytes(content)
        if not real_mime or real_mime not in QR_ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file. Only JPG, PNG, and SVG images are allowed.",
            )

    # Sanitize filename and generate unique name
    safe_name = _sanitize_filename(file.filename)
    unique_filename = f"{uuid_mod.uuid4()}_{safe_name}"
    file_path = QR_UPLOAD_DIR / unique_filename

    # Save file
    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Check if payment settings exist
    existing_settings = await _get_payment_settings(db)

    if not existing_settings:
        raise HTTPException(
            status_code=404,
            detail="Payment settings not found. Please create payment settings first."
        )

    # Delete old QR image if exists
    if existing_settings.qr_image_url:
        try:
            _delete_qr_file_by_url(existing_settings.qr_image_url)
        except Exception:
            pass

    # Update settings with new QR image URL
    qr_url = _build_qr_url(unique_filename)
    await db.execute(
        update(PaymentSettings).where(PaymentSettings.id == existing_settings.id).values(
            qr_image_url=qr_url,
        )
    )
    await db.commit()

    # Fetch updated settings
    result = await db.execute(select(PaymentSettings).where(PaymentSettings.id == existing_settings.id))
    updated_settings = result.scalar_one()

    await AuditService(db).log_action(
        actor_user=current_user,
        action="qr_image_uploaded",
        entity_type="payment_settings",
        entity_id=existing_settings.id,
        entity_label="QR Image Upload",
        request=request,
        metadata={"filename": unique_filename},
    )

    return PaymentSettingsResponse.model_validate(updated_settings)


@router.post("/settings", status_code=200)
async def create_or_update_payment_settings(
    http_request: Request,
    request: PaymentSettingsRequest,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_rls_db),
):
    """Create or update payment settings configuration."""
    from app.models.payment import PaymentSettings
    from app.schemas.payment import PaymentSettingsResponse
    from sqlalchemy import update

    existing_settings = await _get_payment_settings(db)

    if existing_settings:
        update_values = {
            "bank_name": request.bank_name,
            "account_number": request.account_number,
            "account_holder": request.account_holder,
            "payment_instructions": request.payment_instructions,
        }

        if request.qr_image_url is not None and request.qr_image_url != existing_settings.qr_image_url:
            _delete_qr_file_by_url(existing_settings.qr_image_url)
            update_values["qr_image_url"] = request.qr_image_url

        await db.execute(
            update(PaymentSettings)
            .where(PaymentSettings.id == existing_settings.id)
            .values(**update_values)
        )
        await db.commit()

        audit = AuditService(db)
        await audit.log_action(
            actor_user=current_user,
            action="payment_settings_updated",
            entity_type="payment_settings",
            entity_id=existing_settings.id,
            entity_label="Payment Settings",
            request=http_request,
            metadata={"updated_fields": list(update_values.keys())},
        )

        updated_settings = await _get_payment_settings(db)
        return PaymentSettingsResponse.model_validate(updated_settings)

    new_settings = PaymentSettings(
        bank_name=request.bank_name,
        account_number=request.account_number,
        account_holder=request.account_holder,
        payment_instructions=request.payment_instructions,
    )

    if request.qr_image_url is not None:
        new_settings.qr_image_url = request.qr_image_url
    db.add(new_settings)
    await db.commit()
    await db.refresh(new_settings)

    await AuditService(db).log_action(
        actor_user=current_user,
        action="payment_settings_created",
        entity_type="payment_settings",
        entity_id=new_settings.id,
        entity_label="Payment Settings",
        request=http_request,
    )

    return PaymentSettingsResponse.model_validate(new_settings)


@router.get("/qr/{filename}")
async def get_qr_image(
    filename: str,
    db: AsyncSession = Depends(get_db),
):
    """Serve QR code image file. Filename obfuscation (UUID prefix) protects against enumeration."""
    if not filename or ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = QR_UPLOAD_DIR / filename
    if not file_path.resolve().is_relative_to(QR_UPLOAD_DIR.resolve()):
        raise HTTPException(status_code=403, detail="Access denied")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="QR image not found")

    # Determine content type
    if filename.lower().endswith(('.jpg', '.jpeg')):
        media_type = "image/jpeg"
    elif filename.lower().endswith('.png'):
        media_type = "image/png"
    elif filename.lower().endswith('.svg'):
        media_type = "image/svg+xml"
    else:
        media_type = "application/octet-stream"

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
    )
