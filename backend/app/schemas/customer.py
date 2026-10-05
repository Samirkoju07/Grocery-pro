"""Pydantic schemas for Customer module."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    name: str = Field(..., max_length=150)
    phone: str | None = None
    email: EmailStr | None = None
    pan_number: str | None = None
    address: str | None = None
    credit_limit: Decimal = Decimal("0.00")
    is_active: bool = True


class CustomerCreate(CustomerBase):
    company_id: uuid.UUID


class CustomerResponse(CustomerBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    current_balance: Decimal
    loyalty_points: int
    created_at: datetime


class CustomerLedgerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    customer_id: uuid.UUID
    entry_date: datetime
    entry_type: str
    reference_type: str | None
    reference_id: uuid.UUID | None
    debit: Decimal
    credit: Decimal
    running_balance: Decimal
    description: str | None


class CustomerPaymentCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    customer_id: uuid.UUID
    payment_number: str
    payment_date: datetime
    amount: Decimal = Field(..., gt=0)
    payment_mode: str
    reference_number: str | None = None
    notes: str | None = None


class CustomerPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    customer_id: uuid.UUID
    payment_number: str
    payment_date: datetime
    amount: Decimal
    payment_mode: str
    reference_number: str | None
    created_at: datetime
