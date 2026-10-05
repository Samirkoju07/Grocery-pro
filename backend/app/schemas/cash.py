"""Pydantic schemas for Cash module."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CashSessionOpen(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    pos_counter_id: uuid.UUID
    session_number: str
    opening_balance: Decimal = Field(Decimal("0.00"), ge=0)
    notes: str | None = None


class CashSessionClose(BaseModel):
    closing_balance_counted: Decimal = Field(..., ge=0)
    notes: str | None = None


class CashSessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    pos_counter_id: uuid.UUID
    session_number: str
    opened_at: datetime
    closed_at: datetime | None
    opening_balance: Decimal
    closing_balance_expected: Decimal | None
    closing_balance_counted: Decimal | None
    discrepancy: Decimal | None
    status: str
    created_at: datetime


class CashTransactionCreate(BaseModel):
    cash_session_id: uuid.UUID
    txn_type: str  # CASH_IN, CASH_OUT, SAFE_DROP, PAYOUT, EXPENSE
    amount: Decimal = Field(..., gt=0)
    reason: str
    reference_type: str | None = None
    reference_id: uuid.UUID | None = None
    notes: str | None = None


class CashTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    cash_session_id: uuid.UUID
    txn_type: str
    amount: Decimal
    reason: str
    created_at: datetime


class ExpenseCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    cash_session_id: uuid.UUID | None = None
    expense_number: str
    category: str
    amount: Decimal = Field(..., gt=0)
    payment_mode: str = "CASH"
    expense_date: date
    payee: str
    description: str | None = None
    receipt_number: str | None = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    expense_number: str
    category: str
    amount: Decimal
    payment_mode: str
    expense_date: date
    payee: str
    created_at: datetime
