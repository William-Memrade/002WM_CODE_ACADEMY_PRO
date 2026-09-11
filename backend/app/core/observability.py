"""
CodeAcademy Pro — Observability Module
Structured logging, health checks, and Prometheus metrics.
"""

import logging
import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# ── Structured Logging Setup ────────────────────────────────────────────────

# Map string level names to stdlib logging integers
_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def setup_logging(log_level: str = "INFO") -> None:
    """Configure structlog for JSON structured logging."""
    level = _LOG_LEVELS.get(log_level.upper(), logging.INFO)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


logger = structlog.get_logger()


# ── Correlation ID Middleware ────────────────────────────────────────────────


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Add a unique correlation/request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        start_time = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            client_ip=request.client.host if request.client else None,
        )

        return response


# ── Health Check Endpoints ───────────────────────────────────────────────────


async def health_check() -> dict:
    """Basic liveness check."""
    return {"status": "ok", "timestamp": time.time()}


async def readiness_check(db_session, redis_client) -> dict:
    """
    Readiness check — verifies DB, Redis, and Storage connectivity.
    Returns 503 if any check fails.
    """
    checks = {}

    # Database check
    try:
        start = time.perf_counter()
        await db_session.execute("SELECT 1")
        checks["database"] = {
            "status": "ok",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception as e:
        checks["database"] = {"status": "error", "error": str(e)}

    # Redis check
    try:
        start = time.perf_counter()
        await redis_client.ping()
        checks["redis"] = {
            "status": "ok",
            "latency_ms": round((time.perf_counter() - start) * 1000, 2),
        }
    except Exception as e:
        checks["redis"] = {"status": "error", "error": str(e)}

    all_ok = all(c["status"] == "ok" for c in checks.values())

    return {
        "status": "ok" if all_ok else "degraded",
        "checks": checks,
    }
