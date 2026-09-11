"""
CodeAcademy Pro — Background Jobs (ARQ Worker)
Async Redis queue for background task processing.

RLS Integration:
    The worker connects to PostgreSQL using the same engine as the app
    (respecting DATABASE_RLS_URL). Each job that touches the database
    gets a session with `app.current_user_role = 'system'` set via
    apply_system_rls_context(), so RLS policies for email_queue and
    background_jobs tables allow the expected operations.
"""

import asyncio
from datetime import datetime, timezone

import structlog
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings

settings = get_settings()
logger = structlog.get_logger()


# ── Database Session Helper for Workers ──────────────────────────────────────

async def _get_worker_db(ctx: dict) -> AsyncSession:
    """
    Get a DB session from the worker context with 'system' RLS applied.
    Must be used within an async with block for proper cleanup.

    Usage in a job function:
        async with _get_worker_session(ctx) as db:
            result = await db.execute(...)
    """
    from app.db.session import async_session
    from app.db.rls import apply_system_rls_context

    session = async_session()
    try:
        await apply_system_rls_context(session)
        return session
    except Exception:
        await session.close()
        raise


# ── Task Functions ───────────────────────────────────────────────────────────


async def send_email_job(ctx: dict, to_email: str, template: str, template_data: dict) -> bool:
    """Background job: Send transactional email."""
    from app.services.email_service import send_email
    logger.info("job_send_email", to=to_email, template=template)
    return await send_email(to_email, template, template_data)


async def generate_certificate_pdf_job(ctx: dict, certificate_id: str) -> str:
    """Background job: Generate certificate PDF."""
    logger.info("job_generate_certificate", certificate_id=certificate_id)
    # TODO: Implement PDF generation with reportlab or weasyprint
    return f"certificate_{certificate_id}.pdf"


async def recalculate_metrics_job(ctx: dict) -> dict:
    """Background job: Recalculate dashboard metrics and cache them."""
    logger.info("job_recalculate_metrics")
    # TODO: Query aggregated metrics and store in Redis
    return {"status": "recalculated", "timestamp": datetime.now(timezone.utc).isoformat()}


async def cleanup_old_versions_job(ctx: dict, max_versions: int = 50) -> int:
    """Background job: Cleanup old content versions beyond retention limit."""
    logger.info("job_cleanup_versions", max_versions=max_versions)
    # TODO: Delete versions beyond limit per entity
    return 0


async def send_live_class_reminders_job(ctx: dict) -> int:
    """Background job: Send reminders for live classes starting within 1 hour."""
    logger.info("job_live_class_reminders")
    # TODO: Query upcoming classes and send reminder emails
    return 0


# ── Worker Configuration ─────────────────────────────────────────────────────


async def startup(ctx: dict) -> None:
    """Worker startup — initialize DB engine (shared with app)."""
    logger.info("worker_startup", rls_role="system")


async def shutdown(ctx: dict) -> None:
    """Worker shutdown — cleanup connections."""
    logger.info("worker_shutdown")


class WorkerSettings:
    """ARQ worker configuration."""
    functions = [
        send_email_job,
        generate_certificate_pdf_job,
        recalculate_metrics_job,
        cleanup_old_versions_job,
        send_live_class_reminders_job,
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    max_jobs = 10
    job_timeout = 300  # 5 minutes
    retry_jobs = True

    # Cron jobs
    cron_jobs = [
        # Recalculate metrics every 5 minutes
        # cron(recalculate_metrics_job, minute={0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55}),
        # Check for live class reminders every 15 minutes
        # cron(send_live_class_reminders_job, minute={0, 15, 30, 45}),
        # Cleanup old versions daily at 3 AM
        # cron(cleanup_old_versions_job, hour=3, minute=0),
    ]


# ── Helper to Enqueue Jobs ──────────────────────────────────────────────────


async def enqueue_job(function_name: str, *args, **kwargs) -> None:
    """Enqueue a background job via ARQ."""
    redis_pool = await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
    await redis_pool.enqueue_job(function_name, *args, **kwargs)
    logger.info("job_enqueued", function=function_name)

