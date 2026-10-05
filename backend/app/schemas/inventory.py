"""Pydantic schemas for Inventory module."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------
# Stock Batch
# ---------------------------------------------------------
class StockBatchBase(BaseModel):
    batch_number: str
    mfg_date: date | None = None
    expiry_date: date | None = None
    cost_price: Decimal
    selling_price: Decimal
    initial_qty: Decimal
    current_qty: Decimal
    is_active: bool = True


class StockBatchResponse(StockBatchBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------
# Inventory Aggregate
# ---------------------------------------------------------
class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    branch_id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    current_stock: Decimal
    reserved_stock: Decimal
    available_stock: Decimal
    updated_at: datetime


# ---------------------------------------------------------
# Inventory Transaction (Immutable Audit Log)
# ---------------------------------------------------------
class InventoryTransactionCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    txn_type: str
    quantity: Decimal
    unit_cost: Decimal = Decimal("0.00")
    reference_type: str | None = None
    reference_id: uuid.UUID | None = None
    notes: str | None = None


class InventoryTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    branch_id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    batch_id: uuid.UUID | None
    txn_type: str
    quantity: Decimal
    stock_before: Decimal
    stock_after: Decimal
    unit_cost: Decimal
    reference_type: str | None
    reference_id: uuid.UUID | None
    notes: str | None
    created_at: datetime


# ---------------------------------------------------------
# Stock Adjustment
# ---------------------------------------------------------
class StockAdjustmentCreate(BaseModel):
    company_id: uuid.UUID
    branch_id: uuid.UUID
    warehouse_id: uuid.UUID
    product_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    adjustment_number: str
    reason: str
    adjusted_qty: Decimal
    cost_impact: Decimal = Decimal("0.00")
    notes: str | None = None


class StockAdjustmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    adjustment_number: str
    reason: str
    adjusted_qty: Decimal
    cost_impact: Decimal
    status: str
    created_at: datetime


# ---------------------------------------------------------
# Stock Transfer
# ---------------------------------------------------------
class StockTransferItemCreate(BaseModel):
    product_id: uuid.UUID
    batch_id: uuid.UUID | None = None
    requested_qty: Decimal


class StockTransferCreate(BaseModel):
    company_id: uuid.UUID
    transfer_number: str
    from_branch_id: uuid.UUID
    from_warehouse_id: uuid.UUID
    to_branch_id: uuid.UUID
    to_warehouse_id: uuid.UUID
    notes: str | None = None
    items: list[StockTransferItemCreate]


class StockTransferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    transfer_number: str
    status: str
    created_at: datetime
