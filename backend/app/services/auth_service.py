"""
CodeAcademy Pro — Auth Service
Business logic for authentication operations.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.config import get_settings
from app.models.user import User, UserRole
from app.repositories.user_repository import UserRepository, RoleRepository
from app.core.error_handlers import DuplicateError

settings = get_settings()


class AuthService:
    """Authentication business logic."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)

    async def register(
        self,
        email: str,
        username: str,
        password: str,
        first_name: str,
        last_name: str,
    ) -> dict:
        """Register a new student account."""
        # Check uniqueness
        if await self.user_repo.email_exists(email):
            raise DuplicateError("El correo electrónico ya está registrado")
        if await self.user_repo.username_exists(username):
            raise DuplicateError("El nombre de usuario ya está en uso")

        # Create user
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            status="pending",
            email_verified=False,
        )
        user = await self.user_repo.create(user)

        # Assign 'user' role by default
        user_role = await self.role_repo.get_by_name("user")
        if user_role:
            self.db.add(UserRole(user_id=user.id, role_id=user_role.id))
            await self.db.flush()

        # Notify admin (mock log)
        print(f"NOTIFICATION: New user registered '{email}'. Pending approval.")

        # Reload user with roles
        user = await self.user_repo.get_by_id(user.id)

        # Auto-login: generate tokens
        roles = user.role_names
        access_token = create_access_token(user.id, roles)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": roles,
                "status": user.status,
                "force_change_password": getattr(user, "force_change_password", False),
            },
        }

    async def login(self, email: str, password: str) -> dict:
        """Authenticate user and return JWT tokens."""
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid email or password")

        if user.status == "inactive":
            raise ValueError("Account is deactivated")

        # Allow pending users to login (they can browse courses)

        if user.is_blocked:
            raise ValueError("Account is blocked")

        # Set RLS session variables so the UPDATE is allowed by the
        # users_update policy: (id = app_user_id()) OR is_admin()
        # Without this, app_user_id() returns NULL and the UPDATE matches 0 rows.
        from sqlalchemy import text
        await self.db.execute(
            text(f"SET LOCAL app.current_user_id = '{user.id}'")
        )
        roles = user.role_names
        await self.db.execute(
            text(f"SET LOCAL app.current_user_role = '{roles[0] if roles else 'student'}'")
        )

        # Update last login
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.flush()

        # Generate tokens (roles already fetched above for RLS setup)
        access_token = create_access_token(user.id, roles)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": roles,
                "status": user.status,
                "force_change_password": getattr(user, "force_change_password", False),
            },
        }

    async def refresh(self, refresh_token_str: str) -> dict:
        """Refresh access token using a refresh token."""
        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            raise ValueError("Invalid or expired refresh token")

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id = payload.get("sub")
        user = await self.user_repo.get_by_id(UUID(user_id))
        if not user or user.status == "inactive" or user.is_blocked:
            raise ValueError("User not found or inactive")

        roles = user.role_names
        access_token = create_access_token(user.id, roles)
        new_refresh = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_EXPIRE_MINUTES * 60,
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "roles": roles,
                "status": user.status,
                "force_change_password": getattr(user, "force_change_password", False),
            },
        }

    @staticmethod
    def user_to_brief(user: User) -> dict:
        """Convert User model to brief dict for responses."""
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": user.avatar_url,
            "roles": user.role_names,
            "force_change_password": getattr(user, "force_change_password", False),
        }
