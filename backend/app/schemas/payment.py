"""
CodeAcademy Pro — Pydantic Schemas: Payment
Request/response schemas for payments and enrollments.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID
import re

from pydantic import BaseModel, Field, field_validator

from app.utils.sanitizer import sanitize_text, validate_max_length


QR_IMAGE_URL_RE = re.compile(r"^/api/v1/payments/qr/[A-Za-z0-9_.-]+$")


class PaymentSubmitRequest(BaseModel):
    """POST /payments/submit-proof request body (extended)."""
    course_id: UUID
    payment_plan: str = Field(default="full", max_length=20)


class EnrollRequest(BaseModel):
    """POST /enrollments request body."""
    course_id: UUID


class EnrollResponse(BaseModel):
    """POST /enrollments response."""
    id: UUID
    course_id: UUID
    status: str
    payment_info: "PaymentInfo"


class PaymentInfo(BaseModel):
    """Payment details included in enrollment response."""
    payment_id: UUID
    amount: Decimal
    currency: str
    bank_details: str


class PaymentStatusResponse(BaseModel):
    """GET /payments/{id}/status response."""
    id: UUID
    enrollment_id: UUID | None
    course_id: UUID
    amount: Decimal
    currency: str
    status: str
    payment_plan: str
    expected_amount: Decimal | None
    monthly_amount: Decimal | None
    full_amount: Decimal | None
    reference_number: str | None
    reviewed_at: datetime | None
    review_notes: str | None
    proofs: list["PaymentProofResponse"]
    created_at: datetime
    model_config = {"from_attributes": True}


class PaymentProofResponse(BaseModel):
    """Payment proof in responses."""
    id: UUID
    file_url: str
    file_name: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    model_config = {"from_attributes": True}


class PaymentApproveRequest(BaseModel):
    """POST /payments/{id}/approve request body."""
    notes: str | None = Field(None, max_length=1000)

    @field_validator("notes", mode="before")
    @classmethod
    def sanitize_notes(cls, value):
        if value is None:
            return None
        return sanitize_text(value)


class PaymentRejectRequest(BaseModel):
    """POST /payments/{id}/reject request body."""
    notes: str = Field(..., min_length=5, max_length=1000)

    @field_validator("notes", mode="before")
    @classmethod
    def sanitize_notes(cls, value):
        if value is None:
            raise ValueError("Las notas de rechazo son obligatorias")
        return sanitize_text(value)


class AssignClassRequest(BaseModel):
    """POST /payments/{id}/assign-class request body."""
    course_class_id: UUID


class PaymentActionResponse(BaseModel):
    """Response for approve/reject actions."""
    payment_id: UUID
    status: str
    enrollment_status: str | None
    course_class_id: UUID | None = None
    message: str


class EnrollmentResponse(BaseModel):
    """Enrollment detail response."""
    id: UUID
    course_id: UUID
    status: str
    progress_percentage: Decimal
    enrolled_at: datetime
    approved_at: datetime | None
    completed_at: datetime | None
    model_config = {"from_attributes": True}


class PaymentSettingsResponse(BaseModel):
    """GET /payments/settings response (admin — full account number)."""
    id: UUID | None = None
    bank_name: str = ""
    account_number: str = ""
    account_holder: str = ""
    payment_instructions: str | None = None
    qr_image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}


class PaymentSettingsPublicResponse(BaseModel):
    """Public response — account number is masked."""
    bank_name: str = ""
    account_number: str = ""
    account_holder: str = ""
    payment_instructions: str | None = None
    qr_image_url: str | None = None
    currency: str = "USD"

    @staticmethod
    def mask_account_number(number: str) -> str:
        if not number or len(number) <= 4:
            return "****" if number else ""
        return "*" * (len(number) - 4) + number[-4:]


class PaymentSettingsRequest(BaseModel):
    """POST /payments/settings request body."""
    bank_name: str = Field(..., min_length=1, max_length=255, description="Nombre del banco")
    account_number: str = Field(..., min_length=1, max_length=100, description="Número de cuenta")
    account_holder: str = Field(..., min_length=1, max_length=255, description="Titular de la cuenta")
    payment_instructions: str | None = Field(None, max_length=2000, description="Instrucciones de pago")
    qr_image_url: str | None = Field(None, description="URL de la imagen QR (opcional)")

    @field_validator("bank_name", "account_number", "account_holder", mode="before")
    @classmethod
    def sanitize_required_string(cls, value, info):
        """Sanitize and validate required string fields."""
        if value is None:
            raise ValueError(f"{info.field_name.replace('_', ' ').capitalize()} es obligatorio")
        normalized = str(value).strip()
        if not normalized:
            raise ValueError(f"{info.field_name.replace('_', ' ').capitalize()} no puede estar vacío")
        cleaned = sanitize_text(normalized)
        if not cleaned:
            raise ValueError(f"{info.field_name.replace('_', ' ').capitalize()} no puede estar vacío")
        return cleaned

    @field_validator("payment_instructions", mode="before")
    @classmethod
    def sanitize_instructions(cls, value):
        """Sanitize and validate payment instructions text."""
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            return None
        cleaned = sanitize_text(normalized)
        return validate_max_length(cleaned, 2000)

    @field_validator("qr_image_url", mode="before")
    @classmethod
    def validate_qr_image_url(cls, value):
        """Validate that the QR image URL is a safe internal storage path."""
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            return None
        if not QR_IMAGE_URL_RE.fullmatch(normalized):
            raise ValueError("La URL del QR no es válida ni segura")
        return normalized
