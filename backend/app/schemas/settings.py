"""
CodeAcademy Pro — Pydantic Schemas: System Settings
"""

from typing import ClassVar

from pydantic import BaseModel, Field, field_validator
from app.utils.sanitizer import sanitize_text


class SettingsResponse(BaseModel):
    """GET /settings response — platform configuration."""
    platform_name: str
    default_currency: str
    global_max_students_per_class: int


class SettingsUpdateRequest(BaseModel):
    """PUT /settings request — partial update allowed."""
    platform_name: str | None = Field(
        None, min_length=1, max_length=255, description="Nombre de la plataforma"
    )
    default_currency: str | None = Field(
        None, description="Moneda predeterminada (USD, EUR, MXN, COP, GTQ, HNL, NIO, CRC, SVC)"
    )
    global_max_students_per_class: int | None = Field(
        None, ge=1, le=1000, description="Máximo global de alumnos por clase"
    )

    # Static currency map for validation and symbol lookup
    ALLOWED_CURRENCIES: ClassVar[frozenset[str]] = frozenset(
        {"USD", "EUR", "MXN", "COP", "GTQ", "HNL", "NIO", "CRC", "SVC"}
    )

    @field_validator("platform_name", mode="before")
    @classmethod
    def sanitize_platform_name(cls, value):
        if value is None:
            return None
        normalized = str(value).strip()
        if not normalized:
            raise ValueError("Platform name cannot be blank")
        return sanitize_text(normalized)

    @field_validator("default_currency", mode="before")
    @classmethod
    def validate_currency(cls, value):
        if value is None:
            return None
        normalized = str(value).strip().upper()
        if normalized not in cls.ALLOWED_CURRENCIES:
            raise ValueError(f"Moneda no válida: {normalized}")
        return normalized
