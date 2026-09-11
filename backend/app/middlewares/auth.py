"""
CodeAcademy Pro — JWT Authentication Middleware
Extracts and validates JWT from Authorization header.
"""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Extract and validate JWT token, return the current user.
    Raises 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Import here to avoid circular imports
    from app.repositories.user_repository import UserRepository

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))

    if user is None:
        raise credentials_exception

    if user.status == "inactive" or user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated or blocked",
        )

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """Ensure user is active and not blocked."""
    if current_user.status == "inactive":
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_optional_user(
    token: str | None = Depends(
        OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)
    ),
    db: AsyncSession = Depends(get_db),
):
    """Optional authentication — returns None if no token provided."""
    if token is None:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
