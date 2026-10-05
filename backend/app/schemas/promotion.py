"""Pydantic schemas for Promotion module."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PromotionBase(BaseModel):
    name: str = Field(..., max_length=150)
    promo_type: str
    discount_value: Decimal
    min_order_amount: Decimal = Decimal("0.00")
    max_discount_amount: Decimal | None = None
    start_date: datetime
    end_date: datetime
    is_active: bool = True


class PromotionCreate(PromotionBase):
    company_id: uuid.UUID


class PromotionResponse(PromotionBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime


class CouponCreate(BaseModel):
    company_id: uuid.UUID
    promotion_id: uuid.UUID | None = None
    code: str
    discount_type: str = "PERCENTAGE"
    discount_value: Decimal
    min_spend: Decimal = Decimal("0.00")
    max_discount: Decimal | None = None
    usage_limit: int = 1
    valid_from: datetime
    valid_to: datetime


class CouponResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    code: str
    discount_type: str
    discount_value: Decimal
    usage_limit: int
    times_used: int
    is_active: bool
    created_at: datetime
