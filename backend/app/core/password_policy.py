"""
CodeAcademy Pro — Password Policy
Centralized password validation rules.
"""

from __future__ import annotations

import re

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 50
PASSWORD_REQUIRED_SPECIAL_CHARS = "! % & * + , - . : ? @ ^ _ | ~"

# bcrypt only uses the first 72 *bytes* of the password.
BCRYPT_MAX_PASSWORD_BYTES = 72

_UPPERCASE_RE = re.compile(r"[A-Z]")
_DIGIT_RE = re.compile(r"\d")
_SPECIAL_RE = re.compile(r"[_!?*]")


def validate_password(password: str) -> str:
    """
    Validate password rules:
    - 8–20 characters
    - 1 uppercase letter
    - 1 digit
    - 1 special char from: _!?*

    Note: bcrypt truncates at 72 bytes, so we also enforce the UTF-8 encoded
    length stays within that limit to avoid silent truncation.
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters")
    if len(password) > PASSWORD_MAX_LENGTH:
        raise ValueError(f"Password must be at most {PASSWORD_MAX_LENGTH} characters")
    if not _UPPERCASE_RE.search(password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not _DIGIT_RE.search(password):
        raise ValueError("Password must contain at least one digit")
    if not _SPECIAL_RE.search(password):
        raise ValueError(
            f"Password must contain at least one special character ({PASSWORD_REQUIRED_SPECIAL_CHARS})"
        )
    if len(password.encode("utf-8")) > BCRYPT_MAX_PASSWORD_BYTES:
        raise ValueError("Password is too long (in bytes) for bcrypt")
    return password
