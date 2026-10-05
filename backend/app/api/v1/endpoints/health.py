"""Health check endpoints.

GET /health              – liveness probe (no external deps)
GET /api/v1/health       – full readiness probe (DB + Redis)
"""
from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings
from app.db.redis import check_redis_connection
from app.db.session import check_db_connection
from app.schemas.health import HealthResponse, ServiceStatus

router = APIRouter()
settings = get_settings()


@router.get("", response_model=HealthResponse, summary="Readiness health check")
def health_check() -> HealthResponse:
    """Return service health including DB and Redis status."""
    db_ok = check_db_connection()
    redis_ok = check_redis_connection()

    services = {
        "database": ServiceStatus(
            status="ok" if db_ok else "down",
            message="PostgreSQL reachable" if db_ok else "Cannot reach PostgreSQL",
        ),
        "cache": ServiceStatus(
            status="ok" if redis_ok else "down",
            message="Redis reachable" if redis_ok else "Cannot reach Redis",
        ),
    }

    overall = "ok" if (db_ok and redis_ok) else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        services=services,
    )
