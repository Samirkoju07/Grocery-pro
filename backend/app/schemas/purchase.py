"""Pydantic schemas for Purchase module."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SupplierBase(BaseModel):
    name: str = Field(..., max_length=150)
    pan_vat: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None
    opening_balance: Decimal = Decimal("0.00")
    credit_period_days: int = 30
    is_active: bool = True


class SupplierCreate(SupplierBase):
    company_id: uuid.UUID


class SupplierResponse(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    current_balance: Decimal
    created_at: datetime


class PurchaseInvoiceItemCreate(BaseModel):
    product_id: uuid.UUID
    batch_number: str | None = None
    mfg_date: date | None = None
    expiry_date: date | None = None
    quantity: Decimal = Field(..., gt=0)
    unit_cost: Decimal = Field(..., ge=0)
    discount_amount: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal("13.00")


class PurchaseInvoiceCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    warehouse_id: uuid.UUID
    supplier_id: uuid.UUID
    grn_id: uuid.UUID | None = None
    invoice_number: str
    supplier_invoice_no: str | None = None
    invoice_date: date
    due_date: date | None = None
    discount_amount: Decimal = Decimal("0.00")
    items: list[PurchaseInvoiceItemCreate]


class PurchaseInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    invoice_number: str
    supplier_invoice_no: str | None
    invoice_date: date
    subtotal: Decimal
    tax_amount: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    balance_amount: Decimal
    status: str
    created_at: datetime
