"""Pydantic schemas for Authorization module."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------
# Permission
# ---------------------------------------------------------
class PermissionBase(BaseModel):
    module: str
    action: str
    code: str
    description: str | None = None


class PermissionResponse(PermissionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------
# Role
# ---------------------------------------------------------
class RoleBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: str | None = None
    is_system: bool = False
    is_active: bool = True


class RoleCreate(RoleBase):
    company_id: uuid.UUID | None = None
    permission_ids: list[uuid.UUID] = []


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID | None
    created_at: datetime


# ---------------------------------------------------------
# User
# ---------------------------------------------------------
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=80)
    full_name: str = Field(..., max_length=150)
    phone: str | None = None
    is_active: bool = True


class UserCreate(UserBase):
    company_id: uuid.UUID
    branch_id: uuid.UUID | None = None
    password: str = Field(..., min_length=8)
    role_ids: list[uuid.UUID] = []


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    full_name: str | None = None
    phone: str | None = None
    is_active: bool | None = None
    branch_id: uuid.UUID | None = None
    password: str | None = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    branch_id: uuid.UUID | None
    is_superuser: bool
    last_login_at: datetime | None
    created_at: datetime


# ---------------------------------------------------------
# Authentication Tokens
# ---------------------------------------------------------
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: int
