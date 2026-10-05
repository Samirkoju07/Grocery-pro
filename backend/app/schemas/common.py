"""Common shared Pydantic schemas used across modules."""
from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response."""
    items: list[T]
    total: int
    page: int
    per_page: int
    pages: int


class ErrorDetail(BaseModel):
    """Standard error detail."""
    code: str
    message: str
    field: str | None = None
