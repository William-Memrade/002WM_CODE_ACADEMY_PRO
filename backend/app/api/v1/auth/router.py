"""
CodeAcademy Pro — Auth Router
Registration, login, token refresh, profile.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.rls import get_rls_db
from app.middlewares.auth import get_current_user
from app.middlewares.rate_limit import login_rate_limit, register_rate_limit
from app.schemas.auth import (
    MessageResponse,
    RefreshRequest,
    RegisterResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.services.auth_service import AuthService
from app.services.audit_service import AuditService

router = APIRouter()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(register_rate_limit)],
)
async def register(
    data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Create a new user account and auto-login."""
    auth = AuthService(db)
    result = await auth.register(
        email=data.email,
        username=data.username,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
    )
    # Audit: user_created (the new user is the actor of their own creation)
    audit = AuditService(db)
    await audit.log_action(
        actor_user=result["user"],
        action="user_created",
        entity_type="user",
        entity_id=result["user"]["id"],
        entity_label=result["user"]["email"],
        request=request,
        metadata={"source": "self_registration"},
    )
    return result


@router.post(
    "/login",
    response_model=TokenResponse,
    dependencies=[Depends(login_rate_limit)],
)
async def login(
    data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and return JWT tokens."""
    auth = AuthService(db)
    audit = AuditService(db)
    try:
        result = await auth.login(email=data.email, password=data.password)
        await audit.log_action(
            actor_user=result["user"],
            action="login_success",
            entity_type="user",
            entity_id=result["user"]["id"],
            entity_label=result["user"]["email"],
            request=request,
        )
        return result
    except ValueError:
        # Do not reveal whether the email exists.
        await audit.log_action(
            actor_user=None,
            action="login_failed",
            entity_type="user",
            entity_id=None,
            entity_label=data.email,
            request=request,
            metadata={"reason": "invalid_credentials"},
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    auth = AuthService(db)
    try:
        return await auth.refresh(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    """Get current authenticated user profile."""
    return AuthService.user_to_brief(current_user)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_rls_db),
):
    """Logout (client-side token deletion)."""
    audit = AuditService(db)
    await audit.log_action(
        actor_user=current_user,
        action="logout",
        entity_type="user",
        entity_id=current_user.id,
        entity_label=current_user.email,
        request=request,
    )
    return {"message": "Logged out successfully. Please delete your tokens."}
