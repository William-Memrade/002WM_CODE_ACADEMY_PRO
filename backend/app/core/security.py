"""
CodeAcademy Pro — Security Module
JWT token management + bcrypt password hashing.
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.password_policy import BCRYPT_MAX_PASSWORD_BYTES

settings = get_settings()

# ── Password Hashing ────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _bcrypt_secret(password: str) -> bytes:
    """
    bcrypt only uses the first 72 *bytes* of the password.

    Some backends raise an error when the password exceeds this limit, so we
    truncate proactively to keep registration/login working consistently.
    """
    password_bytes = password.encode("utf-8")
    return password_bytes[:BCRYPT_MAX_PASSWORD_BYTES]


def hash_password(password: str) -> str:
    """Hash a password with bcrypt (automatic salt)."""
    return pwd_context.hash(_bcrypt_secret(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return pwd_context.verify(_bcrypt_secret(plain_password), hashed_password)


# ── JWT Token Management ────────────────────────────────────────────────────


def create_access_token(
    user_id: UUID,
    roles: list[str],
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_ACCESS_EXPIRE_MINUTES)
    )
    payload = {
        "sub": str(user_id),
        "roles": roles,
        "type": "access",
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(
    user_id: UUID,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT refresh token."""
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.JWT_REFRESH_EXPIRE_DAYS)
    )
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": datetime.now(timezone.utc),
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    Raises JWTError if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise


def create_email_verification_token(user_id: UUID) -> str:
    """Create a token for email verification (24h expiry)."""
    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    payload = {
        "sub": str(user_id),
        "type": "email_verification",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_password_reset_token(user_id: UUID) -> str:
    """Create a token for password reset (1h expiry)."""
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    payload = {
        "sub": str(user_id),
        "type": "password_reset",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
