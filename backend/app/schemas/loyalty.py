"""Pydantic schemas for Loyalty module."""
from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LoyaltyAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    customer_id: uuid.UUID
    card_number: str | None
    current_points: int
    lifetime_points: int
    tier: str
    is_active: bool
    created_at: datetime


class LoyaltyTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    loyalty_account_id: uuid.UUID
    txn_type: str
    points: int
    points_before: int
    points_after: int
    sales_invoice_id: uuid.UUID | None
    created_at: datetime
