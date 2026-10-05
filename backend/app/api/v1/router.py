"""API v1 router – aggregates all v1 endpoint routers."""
from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import health

api_v1_router = APIRouter()

api_v1_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

# Future module routers will be registered here:
# api_v1_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
# api_v1_router.include_router(products.router, prefix="/products", tags=["Products"])
# ... etc.
