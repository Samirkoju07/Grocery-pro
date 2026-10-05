"""Inventory models: Inventory, InventoryTransaction, StockBatch, StockAdjustment, StockCount, StockCountItem, StockTransfer, StockTransferItem."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Product


class Inventory(Base, UUIDMixin, TimestampMixin):
    """Aggregate stock per warehouse per product."""

    __tablename__ = "inventories"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", name="uq_inventory_warehouse_product"),
        Index("ix_inventory_branch_product", "branch_id", "product_id"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    current_stock: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)
    reserved_stock: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)
    available_stock: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)

    # Relationships
    product: Mapped[Product] = relationship("Product")


class StockBatch(Base, UUIDMixin, TimestampMixin):
    """FMCG batch and expiry management."""

    __tablename__ = "stock_batches"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "product_id", "batch_number", name="uq_batch_warehouse_product"),
        Index("ix_stock_batch_expiry", "expiry_date", "is_active"),
        CheckConstraint("current_qty >= 0", name="chk_batch_current_qty_non_negative"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_number: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    mfg_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    initial_qty: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)
    current_qty: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    product: Mapped[Product] = relationship("Product")


class InventoryTransaction(Base, UUIDMixin, TimestampMixin):
    """Immutable audit trail for EVERY inventory change. Stock is never mutated directly without a txn."""

    __tablename__ = "inventory_transactions"
    __table_args__ = (
        Index("ix_inv_txn_warehouse_product", "warehouse_id", "product_id", "created_at"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_batches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    txn_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )  # PURCHASE_RECEIVE, SALES_DISPATCH, SALES_RETURN, PURCHASE_RETURN, ADJUSTMENT, TRANSFER_IN, TRANSFER_OUT, DAMAGE
    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)  # positive = increase, negative = decrease
    stock_before: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    stock_after: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit_cost: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # sales_invoice, grn, adjustment, transfer
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    product: Mapped[Product] = relationship("Product")
    batch: Mapped[StockBatch | None] = relationship("StockBatch")


class StockAdjustment(Base, UUIDMixin, TimestampMixin):
    """Stock adjustment records."""

    __tablename__ = "stock_adjustments"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_batches.id", ondelete="SET NULL"),
        nullable=True,
    )
    adjustment_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    reason: Mapped[str] = mapped_column(String(100), nullable=False)  # DAMAGE, EXPIRY, PHYSICAL_COUNT_DISCREPANCY, THEFT, OTHER
    adjusted_qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    cost_impact: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="PENDING", nullable=False)  # PENDING, APPROVED, REJECTED
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class StockCount(Base, UUIDMixin, TimestampMixin):
    """Physical stock count / stock-taking session."""

    __tablename__ = "stock_counts"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    count_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="DRAFT", nullable=False)  # DRAFT, IN_PROGRESS, COMPLETED, RECONCILED
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    items: Mapped[list[StockCountItem]] = relationship("StockCountItem", back_populates="stock_count", cascade="all, delete-orphan")


class StockCountItem(Base, UUIDMixin, TimestampMixin):
    """Items verified during physical stock count."""

    __tablename__ = "stock_count_items"

    stock_count_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_counts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_batches.id", ondelete="SET NULL"),
        nullable=True,
    )
    system_qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    counted_qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    difference_qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    stock_count: Mapped[StockCount] = relationship("StockCount", back_populates="items")
    product: Mapped[Product] = relationship("Product")


class StockTransfer(Base, UUIDMixin, TimestampMixin):
    """Inter-warehouse and inter-branch stock transfers."""

    __tablename__ = "stock_transfers"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    transfer_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    from_branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    from_warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    to_branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    to_warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(30), default="REQUESTED", nullable=False
    )  # REQUESTED, APPROVED, DISPATCHED, RECEIVED, CANCELLED
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    items: Mapped[list[StockTransferItem]] = relationship("StockTransferItem", back_populates="transfer", cascade="all, delete-orphan")


class StockTransferItem(Base, UUIDMixin, TimestampMixin):
    """Line items for a stock transfer."""

    __tablename__ = "stock_transfer_items"

    stock_transfer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_transfers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_batches.id", ondelete="SET NULL"),
        nullable=True,
    )
    requested_qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    dispatched_qty: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)
    received_qty: Mapped[float] = mapped_column(Numeric(12, 3), default=0.000, nullable=False)

    # Relationships
    transfer: Mapped[StockTransfer] = relationship("StockTransfer", back_populates="items")
    product: Mapped[Product] = relationship("Product")
