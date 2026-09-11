"""
CodeAcademy Pro — Redis Client Helper
Provides a shared async Redis client instance.
"""
import redis.asyncio as redis
from app.core.config import get_settings

_settings = get_settings()


async def get_redis_client() -> redis.Redis:
    """Return a new Redis client from the configured URL."""
    return redis.from_url(
        _settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )
