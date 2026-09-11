"""
CodeAcademy Pro — Application Entry Point
FastAPI application with middleware, routers, and lifecycle events.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.observability import CorrelationIdMiddleware, health_check, setup_logging
from app.middlewares.profiling import QueryProfilingMiddleware, setup_query_profiling
from app.middlewares.rate_limit import setup_rate_limiter, teardown_rate_limiter
from app.middlewares.security_headers import SecurityHeadersASGI, SecurityHeadersMiddleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: startup and shutdown events."""
    # Startup
    setup_logging(settings.LOG_LEVEL)
    setup_query_profiling()
    await setup_rate_limiter(app)
    yield
    # Shutdown
    await teardown_rate_limiter()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Academia virtual de programación — API REST",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ── Middleware ───────────────────────────────────────────────────────────────

# GZip compression — compress responses > 500 bytes
app.add_middleware(GZipMiddleware, minimum_size=500)

# Query profiling — adds X-Query-Count and X-DB-Time-Ms to every response
app.add_middleware(QueryProfilingMiddleware)

# CORS — origins, expose_headers and max_age driven by Settings / environment
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    # NOTE: If cookies or credentials:"include" are added in the future,
    # set allow_credentials=True and implement CSRF protection.
    allow_credentials=False,  # JWT via Authorization header; no cookies/sessions
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=settings.cors_expose_headers,
    max_age=settings.CORS_MAX_AGE,
)

# Correlation ID / Request logging
app.add_middleware(CorrelationIdMiddleware)

# Security Headers — request-path logic (Cache-Control, Server header removal).
# Registered last in add_middleware = outermost BaseHTTPMiddleware.
app.add_middleware(
    SecurityHeadersMiddleware,
    enabled=settings.SECURITY_HEADERS_ENABLED,
    environment=settings.ENVIRONMENT,
)

# ── Routers ──────────────────────────────────────────────────────────────────

app.include_router(api_router)


# ── Exception Handlers ───────────────────────────────────────────────────────

from app.core.error_handlers import register_exception_handlers
register_exception_handlers(app)


# ── Health Check Endpoints ───────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
async def liveness():
    """Liveness probe — is the app running?"""
    return await health_check()


@app.get("/health/ready", tags=["Health"])
async def readiness():
    """Readiness probe — are DB, Redis, Storage connected?"""
    # TODO: Inject actual DB and Redis clients
    return {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


# ── Root ─────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"])
async def root():
    """API root — basic info."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/api/docs" if settings.DEBUG else "disabled",
    }


# ── ASGI-level Security Headers ─────────────────────────────────────────────
# Wraps the ENTIRE app (including Starlette's ServerErrorMiddleware) so that
# security headers appear on unhandled 500 errors, 404s, and every other
# response without exception.
# IMPORTANT: This MUST be the last assignment — it replaces the FastAPI
# instance with a pure ASGI wrapper. All routes, middleware and decorators
# must be registered BEFORE this line.
app = SecurityHeadersASGI(
    app,
    enabled=settings.SECURITY_HEADERS_ENABLED,
    debug=settings.DEBUG,
    hsts_enabled=settings.HSTS_ENABLED,
    hsts_max_age=settings.HSTS_MAX_AGE,
    hsts_include_subdomains=settings.HSTS_INCLUDE_SUBDOMAINS,
    hsts_preload=settings.HSTS_PRELOAD,
    csp_report_only=settings.CSP_REPORT_ONLY,
    csp_report_uri=settings.CSP_REPORT_URI,
)
