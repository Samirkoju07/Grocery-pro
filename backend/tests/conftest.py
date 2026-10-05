"""Pytest configuration and shared fixtures."""
from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

# Use a separate test database / in-memory settings
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg2://grocery_user:test@localhost:5432/grocery_pos_test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/1")
os.environ.setdefault("SECRET_KEY", "test-secret-key-do-not-use-in-production")

from app.main import app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a synchronous test client for the FastAPI app."""
    with TestClient(app) as c:
        yield c
