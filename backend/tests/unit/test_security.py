"""Unit tests for security utilities."""
from __future__ import annotations

import pytest
from jose import jwt

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    plain = "superSecret123!"
    hashed = hash_password(plain)
    assert hashed != plain
    assert verify_password(plain, hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_creation() -> None:
    token = create_access_token(subject="user-123")
    assert isinstance(token, str)
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["type"] == "access"


def test_refresh_token_creation() -> None:
    token = create_refresh_token(subject="user-456")
    payload = decode_token(token)
    assert payload["sub"] == "user-456"
    assert payload["type"] == "refresh"


def test_token_with_extra_claims() -> None:
    token = create_access_token(subject="user-789", extra={"role": "admin"})
    payload = decode_token(token)
    assert payload["role"] == "admin"
