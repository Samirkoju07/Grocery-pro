"""Pydantic schemas for Organization module."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------
# Company
# ---------------------------------------------------------
class CompanyBase(BaseModel):
    name: str = Field(..., max_length=200)
    legal_name: str | None = Field(None, max_length=255)
    pan_vat_number: str | None = Field(None, max_length=20)
    phone: str | None = Field(None, max_length=20)
    email: EmailStr | None = None
    address: str | None = Field(None, max_length=255)
    currency: str = Field("NPR", max_length=10)
    default_vat_rate: Decimal = Field(Decimal("13.00"), ge=0, le=100)
    is_active: bool = True


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = None
    legal_name: str | None = None
    pan_vat_number: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    currency: str | None = None
    default_vat_rate: Decimal | None = None
    is_active: bool | None = None


class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------
# Branch
# ---------------------------------------------------------
class BranchBase(BaseModel):
    name: str = Field(..., max_length=150)
    code: str = Field(..., max_length=50)
    is_main: bool = False
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    pan_number: str | None = None
    is_active: bool = True


class BranchCreate(BranchBase):
    company_id: uuid.UUID


class BranchUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    is_main: bool | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    pan_number: str | None = None
    is_active: bool | None = None


class BranchResponse(BranchBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------
# Warehouse
# ---------------------------------------------------------
class WarehouseBase(BaseModel):
    name: str = Field(..., max_length=150)
    code: str = Field(..., max_length=50)
    address: str | None = None
    is_default: bool = False
    is_active: bool = True


class WarehouseCreate(WarehouseBase):
    company_id: uuid.UUID
    branch_id: uuid.UUID


class WarehouseUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    address: str | None = None
    is_default: bool | None = None
    is_active: bool | None = None


class WarehouseResponse(WarehouseBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    branch_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------
# POS Counter
# ---------------------------------------------------------
class POSCounterBase(BaseModel):
    counter_number: str = Field(..., max_length=30)
    name: str = Field(..., max_length=100)
    device_id: str | None = None
    ip_address: str | None = None
    is_active: bool = True


class POSCounterCreate(POSCounterBase):
    company_id: uuid.UUID
    branch_id: uuid.UUID


class POSCounterUpdate(BaseModel):
    counter_number: str | None = None
    name: str | None = None
    device_id: str | None = None
    ip_address: str | None = None
    is_active: bool | None = None


class POSCounterResponse(POSCounterBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    branch_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
