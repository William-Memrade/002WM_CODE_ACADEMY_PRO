"""
CodeAcademy Pro — User Repository
Data access for users and roles.
"""

from uuid import UUID

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, Role, UserRole
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(User, db)

    async def get_by_id(self, id: UUID) -> User | None:
        """Get user by ID with roles loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.id == id)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_id_lite(self, id: UUID) -> User | None:
        """Get user by ID WITHOUT roles (lightweight — for updates that don't need roles)."""
        result = await self.db.execute(
            select(User)
            .where(User.id == id)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email with roles loaded."""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.user_roles).selectinload(UserRole.role))
            .where(User.email == email)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username (no roles loaded — lightweight)."""
        result = await self.db.execute(
            select(User)
            .where(User.username == username)
            .where(User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def email_exists(self, email: str) -> bool:
        """Check if email is already registered using EXISTS (no full User load)."""
        result = await self.db.execute(
            select(
                exists(
                    select(User.id)
                    .where(User.email == email)
                    .where(User.deleted_at.is_(None))
                )
            )
        )
        return result.scalar() or False

    async def username_exists(self, username: str) -> bool:
        """Check if username is already taken using EXISTS (no full User load)."""
        result = await self.db.execute(
            select(
                exists(
                    select(User.id)
                    .where(User.username == username)
                    .where(User.deleted_at.is_(None))
                )
            )
        )
        return result.scalar() or False


class RoleRepository(BaseRepository[Role]):
    """Repository for Role operations."""

    def __init__(self, db: AsyncSession):
        super().__init__(Role, db)

    async def get_by_name(self, name: str) -> Role | None:
        """Get role by name."""
        result = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()
