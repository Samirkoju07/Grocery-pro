"""Tests for health check endpoints."""
from __future__ import annotations

from fastapi.testclient import TestClient


def test_root_health(client: TestClient) -> None:
    """GET /health should return 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
    assert "environment" in body


def test_v1_health(client: TestClient) -> None:
    """GET /api/v1/health should return 200."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] in ("ok", "degraded")
    assert "services" in body
    assert "database" in body["services"]
    assert "cache" in body["services"]
