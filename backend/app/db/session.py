"""
CodeAcademy Pro — Database Session
Async SQLAlchemy engine and session factory.
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

settings = get_settings()
_logger = logging.getLogger(__name__)

# ── RLS enforcement validation ───────────────────────────────────────────────
# If DATABASE_RLS_URL is not set, the app falls back to DATABASE_URL which may
# be a superuser connection that bypasses all RLS policies.
_db_url = settings.DATABASE_RLS_URL or settings.DATABASE_URL
_using_rls_url = bool(settings.DATABASE_RLS_URL)

if not _using_rls_url:
    if settings.ENVIRONMENT in ("production", "staging"):
        _logger.critical(
            "DATABASE_RLS_URL is not configured. The application will connect "
            "using DATABASE_URL which may bypass Row Level Security policies. "
            "This is NOT acceptable in %s. Set DATABASE_RLS_URL to the "
            "academy_app connection string.",
            settings.ENVIRONMENT,
        )
        raise RuntimeError(
            f"DATABASE_RLS_URL is required in {settings.ENVIRONMENT}. "
            "Cannot start without RLS enforcement."
        )
    else:
        _logger.warning(
            "DATABASE_RLS_URL is not configured. Falling back to DATABASE_URL. "
            "RLS policies may be bypassed if connected as superuser. "
            "Set DATABASE_RLS_URL=postgresql+asyncpg://academy_app:...@host/db "
            "to enable RLS enforcement."
        )

# Create async engine
# NOTE: echo is ALWAYS False for performance. Use SQL logging middleware for debugging.
engine = create_async_engine(
    _db_url,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_pre_ping=True,  # Verify connections before use
    echo=False,  # NEVER echo in production — massive overhead
)

# Session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an async database session.
    Automatically commits on success, rollbacks on exception.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

