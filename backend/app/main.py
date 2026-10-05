"""FastAPI application factory.

Do NOT import heavy modules at module level to keep cold-start fast.
All routers and middleware are registered in create_app().
"""
from __future__ import annotations

import contextlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.middleware.request_id import RequestIDMiddleware
from app.schemas.health import HealthResponse, ServiceStatus

settings = get_settings()
configure_logging()
log = get_logger(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    log.info(
        "Starting Grocery POS backend",
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
    )
    yield
    log.info("Shutting down Grocery POS backend")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Production-grade Grocery / Supermarket Management System for Nepal",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        openapi_url="/openapi.json" if settings.DEBUG else None,
        lifespan=lifespan,
    )

    # -----------------------------------------------------------------
    # Middleware (order matters – outermost first)
    # -----------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)

    # -----------------------------------------------------------------
    # Routers
    # -----------------------------------------------------------------
    app.include_router(api_v1_router, prefix="/api/v1")

    # -----------------------------------------------------------------
    # Root health endpoint (liveness probe – no external deps)
    # -----------------------------------------------------------------
    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    def root_health() -> HealthResponse:
        """Simple liveness probe – always returns ok if the process is alive."""
        return HealthResponse(
            status="ok",
            version=settings.APP_VERSION,
            environment=settings.APP_ENV,
        )

    @app.get("/", response_model=dict, tags=["Root"])
    def root() -> dict:
        """Root endpoint – provides a friendly welcome message."""
        return {"message": "Welcome to the Grocery POS API"}

    return app


app = create_app()
