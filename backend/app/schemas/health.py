"""Health check response schemas."""
from __future__ import annotations

from pydantic import BaseModel


class ServiceStatus(BaseModel):
    status: str  # "ok" | "degraded" | "down"
    message: str = ""


class HealthResponse(BaseModel):
    status: str  # "ok" | "degraded" | "down"
    version: str
    environment: str
    services: dict[str, ServiceStatus] = {}
