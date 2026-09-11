"""
CodeAcademy Pro — Pydantic Schemas: Auth
Request/response schemas for authentication endpoints.
"""

import re
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.password_policy import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    validate_password as validate_password_policy,
)


class UserRegister(BaseModel):
    """POST /auth/register request body."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH)
    first_name: str = Field(..., min_length=2, max_length=120)
    last_name: str = Field(..., min_length=2, max_length=120)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate that username is 3-30 chars of letters, digits, or underscores.

        Args:
            v (str): The username to validate.
        """
        if not re.match(r"^[a-zA-Z0-9_]{3,30}$", v):
            raise ValueError("Username must be 3-30 alphanumeric characters or underscores")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password rules:
        - 8 to 20 characters
        - 1 uppercase letter
        - 1 digit
        - 1 special char

        Args:
            v (str): The password to validate.
        """
        return validate_password_policy(v)

    @field_validator("first_name", "last_name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """
        Validate that name is 2-120 chars of letters or spaces.

        Args:
            v (str): The name to validate.
        """
        if not re.match(r"^[a-zA-ZÀ-ÿ\s]{2,120}$", v):
            raise ValueError("Name must contain only letters and spaces (2-120 chars)")
        return v.strip()


class UserLogin(BaseModel):
    """POST /auth/login request body."""
    email: EmailStr
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Login/refresh response with tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserBrief"


class UserBrief(BaseModel):
    """Brief user info included in token response."""
    id: UUID
    email: str
    username: str
    first_name: str
    last_name: str
    roles: list[str]
    status: str | None = None
    force_change_password: bool = False

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    """POST /auth/refresh request body."""
    refresh_token: str


class RegisterResponse(BaseModel):
    """POST /auth/register response."""
    id: UUID
    email: str
    username: str
    message: str = "Account created. Please verify your email."


class ForgotPasswordRequest(BaseModel):
    """POST /auth/forgot-password request body."""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """POST /auth/reset-password request body."""
    token: str
    new_password: str = Field(
        ...,
        min_length=PASSWORD_MIN_LENGTH,
        max_length=PASSWORD_MAX_LENGTH,
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password rules:
        - 8 to 20 characters
        - 1 uppercase letter
        - 1 digit
        - 1 special char

        Args:
            v (str): The password to validate.
        """
        return validate_password_policy(v)


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
