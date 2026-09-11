"""
CodeAcademy Pro — Global Exception Handlers
Traduces technical exceptions into user-friendly Spanish messages.
"""

import re

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException


class DuplicateError(Exception):
    """Raised when a unique constraint would be violated at the business logic level."""
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


_CONSTRAINT_MESSAGES: dict[str, str] = {
    "uq_course_class_name_per_course": "Ya existe una clase con ese nombre en este curso",
    "course_classes_slug_key": "Ya existe una clase con ese identificador",
    "courses_slug_key": "Ya existe un curso con ese identificador",
    "categories_name_key": "Ya existe una categoría con ese nombre",
    "categories_slug_key": "Ya existe una categoría con ese identificador",
    "users_email_key": "El correo electrónico ya está registrado",
    "users_username_key": "El nombre de usuario ya está en uso",
    "roles_name_key": "El rol ya existe",
    "system_settings_key_key": "La configuración ya existe",
    "feature_flags_key_key": "El feature flag ya existe",
}

_CONSTRAINT_EXTRACTORS: list[tuple[str, str]] = [
    (r"uq_course_class_name_per_course", "nombre de clase"),
    (r"course_classes_slug_key", "identificador de clase"),
    (r"courses_slug_key", "identificador de curso"),
    (r"categories_name_key", "nombre de categoría"),
    (r"categories_slug_key", "identificador de categoría"),
    (r"users_email_key", "correo electrónico"),
    (r"users_username_key", "nombre de usuario"),
    (r"roles_name_key", "rol"),
]


def _translate_integrity_error(exc: IntegrityError) -> str:
    """Translate a PostgreSQL unique violation into a friendly message."""
    error_msg = str(exc.orig) if exc.orig else str(exc)

    for pattern, message in _CONSTRAINT_MESSAGES.items():
        if pattern in error_msg:
            return message

    for pattern, field in _CONSTRAINT_EXTRACTORS:
        if pattern in error_msg:
            value_match = re.search(r"Key \((.+?)\)=\((.+?)\)", error_msg)
            if value_match:
                value = value_match.group(2)
                return f"Ya existe un registro con el {field} '{value}'"

    return "Ya existe un registro con la misma información. Por favor, verifica los datos."


async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": _translate_integrity_error(exc)},
    )


async def validation_error_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Campos incompletos o inválidos. Por favor, valida la información enviada."
        },
    )


async def duplicate_error_handler(request: Request, exc: DuplicateError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"detail": exc.detail},
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


def register_exception_handlers(app):
    """Register all custom exception handlers on the FastAPI app."""
    from fastapi.exceptions import RequestValidationError

    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(DuplicateError, duplicate_error_handler)
    app.add_exception_handler(ValueError, value_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
