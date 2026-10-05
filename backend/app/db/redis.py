"""Redis client factory with connection health check."""
from __future__ import annotations

import redis
from redis import Redis

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger(__name__)
settings = get_settings()

_redis_client: Redis | None = None


def get_redis() -> Redis:
    """Return the singleton Redis client, creating it if necessary."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
    return _redis_client


def check_redis_connection() -> bool:
    """Probe the Redis connection. Returns True if healthy."""
    try:
        get_redis().ping()
        return True
    except Exception as exc:
        log.error("Redis health check failed", error=str(exc))
        return False
