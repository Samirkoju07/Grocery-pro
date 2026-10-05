"""Pydantic schemas for Sales module."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PaymentCreate(BaseModel):
    payment_method: str  # CASH, ESEWA, KHALTI, FONEPAY, CARD, BANK_TRANSFER, KHATA_CREDIT, REWARD_POINTS
    amount: Decimal = Field(..., ge=0)
    transaction_reference: str | None = None
    notes: str | None = None


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    payment_method: str
    amount: Decimal
    transaction_reference: str | None
    status: str
    created_at: datetime


class SalesInvoiceItemCreate(BaseModel):
    product_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    unit_id: uuid.UUID
    quantity: Decimal = Field(..., gt=0)
    unit_price: Decimal = Field(..., ge=0)
    cost_price: Decimal = Decimal("0.00")
    discount_percent: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal("13.00")


class SalesInvoiceItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    batch_id: uuid.UUID | None
    unit_id: uuid.UUID
    product_name: str
    quantity: Decimal
    unit_price: Decimal
    discount_amount: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    total_amount: Decimal


class SalesInvoiceCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    pos_counter_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None
    fiscal_year: str
    invoice_number: str
    invoice_date: datetime
    invoice_date_bs: str | None = None
    customer_pan: str | None = None
    customer_name: str | None = None
    discount_amount: Decimal = Decimal("0.00")
    round_off: Decimal = Decimal("0.00")
    items: list[SalesInvoiceItemCreate]
    payments: list[PaymentCreate]
    notes: str | None = None


class SalesInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    branch_id: uuid.UUID
    invoice_number: str
    fiscal_year: str
    invoice_date: datetime
    invoice_date_bs: str | None
    subtotal: Decimal
    discount_amount: Decimal
    taxable_amount: Decimal
    nontaxable_amount: Decimal
    vat_amount: Decimal
    round_off: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    change_amount: Decimal
    payment_status: str
    status: str
    customer_pan: str | None
    customer_name: str | None
    items: list[SalesInvoiceItemResponse] = []
    payments: list[PaymentResponse] = []
    created_at: datetime


class SalesReturnItemCreate(BaseModel):
    sales_invoice_item_id: uuid.UUID | None = None
    product_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    return_qty: Decimal = Field(..., gt=0)
    refund_unit_price: Decimal = Field(..., ge=0)
    restock_inventory: bool = True


class SalesReturnCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    pos_counter_id: uuid.UUID | None = None
    sales_invoice_id: uuid.UUID
    customer_id: uuid.UUID | None = None
    return_number: str
    return_date: datetime
    return_date_bs: str | None = None
    reason: str | None = None
    refund_method: str = "CASH"
    items: list[SalesReturnItemCreate]


class SalesReturnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    return_number: str
    return_date: datetime
    subtotal: Decimal
    tax_amount: Decimal
    refund_amount: Decimal
    refund_method: str
    status: str
    created_at: datetime
