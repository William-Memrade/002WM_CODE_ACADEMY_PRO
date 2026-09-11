"""
CodeAcademy Pro — RLS-Aware Database Session
Provides FastAPI dependencies that inject user identity into PostgreSQL
transaction-local variables for Row Level Security enforcement.

Usage in endpoints:
    # Authenticated endpoint with RLS:
    @router.get("/my-data")
    async def get_my_data(
        current_user=Depends(get_current_user),
        db: AsyncSession = Depends(get_rls_db),
    ): ...

    # Public endpoint (no RLS context):
    @router.get("/catalog")
    async def get_catalog(db: AsyncSession = Depends(get_db)): ...
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.db.session import get_db
from app.middlewares.auth import get_current_user, get_optional_user


def _get_primary_role(user) -> str:
    """
    Determine the highest-priority role for RLS context.
    Priority: admin > teacher > student > user.
    """
    if not hasattr(user, "role_names"):
        return "user"
    roles = set(user.role_names)
    if "admin" in roles:
        return "admin"
    if "teacher" in roles:
        return "teacher"
    if "student" in roles:
        return "student"
    return "user"


async def _apply_rls_context(db: AsyncSession, user) -> None:
    """
    Set transaction-local variables for RLS.

    Uses set_config() instead of SET LOCAL because PostgreSQL's extended query
    protocol (used by asyncpg) does NOT support parameter placeholders in SET
    commands. set_config(name, value, is_local=true) is functionally identical
    to SET LOCAL and properly supports parameterized queries.

    The is_local=true flag ensures values are automatically cleared on
    COMMIT/ROLLBACK, making it safe with connection pooling.
    """
    await db.execute(
        text("SELECT set_config('app.current_user_id', :uid, true)"),
        {"uid": str(user.id)},
    )
    primary_role = _get_primary_role(user)
    await db.execute(
        text("SELECT set_config('app.current_user_role', :role, true)"),
        {"role": primary_role},
    )


async def get_rls_db(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
) -> AsyncSession:
    """
    FastAPI dependency: returns the DB session with RLS context applied.
    The session is the SAME one used by get_current_user (FastAPI caches
    dependencies per request), so no extra connections are opened.

    SET LOCAL is transaction-scoped — automatically cleaned up on
    COMMIT or ROLLBACK, making it safe with async connection pooling.
    """
    await _apply_rls_context(db, current_user)
    return db


async def get_rls_db_optional(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_optional_user),
) -> AsyncSession:
    """
    Like get_rls_db but for endpoints with optional authentication.
    If no user is authenticated, returns the session without RLS context.
    Public RLS policies (USING conditions with no user check) still apply.
    """
    if current_user is not None:
        await _apply_rls_context(db, current_user)
    return db


async def get_system_rls_db(
    db: AsyncSession = Depends(get_db),
) -> AsyncSession:
    """
    RLS context for background workers / system operations.
    Sets role to 'system' which specific policies allow.
    """
    await apply_system_rls_context(db)
    return db


# ---------------------------------------------------------------------------
# Standalone helpers (usable outside FastAPI dependency injection)
# ---------------------------------------------------------------------------

async def apply_rls_context_raw(db: AsyncSession, user_id: str, role: str) -> None:
    """
    Apply RLS context to an existing session. Callable from any async context
    (FastAPI, ARQ worker, scripts, tests) without dependency injection.
    """
    await db.execute(
        text("SELECT set_config('app.current_user_id', :uid, true)"),
        {"uid": user_id},
    )
    await db.execute(
        text("SELECT set_config('app.current_user_role', :role, true)"),
        {"role": role},
    )


async def apply_system_rls_context(db: AsyncSession) -> None:
    """
    Apply 'system' RLS context to an existing session.
    Used by the ARQ worker and any background task that needs DB access.
    Only sets role (no user_id), so policies checking app_user_id() return NULL.
    """
    await db.execute(
        text("SELECT set_config('app.current_user_role', 'system', true)"),
    )

