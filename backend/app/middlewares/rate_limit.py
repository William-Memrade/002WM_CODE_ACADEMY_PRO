"""
CodeAcademy Pro — Rate Limiting Middleware
Redis-backed rate limiting using fastapi-limiter.
"""

from fastapi import FastAPI, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
import redis.asyncio as redis

from app.core.config import get_settings

settings = get_settings()


async def setup_rate_limiter(app: FastAPI) -> None:
    """Initialize Redis-backed rate limiter on app startup."""
    redis_client = redis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_client)


async def teardown_rate_limiter() -> None:
    """Close rate limiter on app shutdown."""
    await FastAPILimiter.close()


# ── Pre-configured Rate Limiters ────────────────────────────────────────────

# Login: 10 requests per minute
login_rate_limit = RateLimiter(times=10, seconds=60)

# Register: 5 requests per minute
register_rate_limit = RateLimiter(times=5, seconds=60)

# File upload: 5 requests per minute
upload_rate_limit = RateLimiter(times=5, seconds=60)

# Password reset: 3 requests per minute
password_reset_rate_limit = RateLimiter(times=3, seconds=60)

# General API: configurable (default 100/min)
general_rate_limit = RateLimiter(times=settings.RATE_LIMIT_PER_MINUTE, seconds=60)

# Admin actions: 30 requests per minute
admin_rate_limit = RateLimiter(times=30, seconds=60)
