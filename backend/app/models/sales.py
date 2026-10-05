"""Sales models: SalesInvoice, SalesInvoiceItem, SalesReturn, SalesReturnItem, Payment."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.product import Product, Unit


class SalesInvoice(Base, UUIDMixin, TimestampMixin):
    """POS Sales invoice compliant with Nepal IRD requirements. Preserves historical prices."""

    __tablename__ = "sales_invoices"
    __table_args__ = (
        UniqueConstraint("branch_id", "fiscal_year", "invoice_number", name="uq_invoice_branch_fiscal_number"),
        Index("ix_sales_invoice_date", "branch_id", "invoice_date"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    pos_counter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos_counters.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    fiscal_year: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # e.g., 2081/82
    invoice_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    invoice_date_bs: Mapped[str | None] = mapped_column(String(20), nullable=True)  # Bikram Sambat date string
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    taxable_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    nontaxable_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    vat_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    round_off: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    change_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    payment_status: Mapped[str] = mapped_column(
        String(30), default="PAID", nullable=False
    )  # PAID, PARTIALLY_PAID, CREDIT
    status: Mapped[str] = mapped_column(
        String(30), default="COMPLETED", nullable=False
    )  # COMPLETED, VOIDED, RETURNED, CANCELLED
    customer_pan: Mapped[str | None] = mapped_column(String(20), nullable=True)
    customer_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    is_synced: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)  # For offline POS
    sync_id: Mapped[str | None] = mapped_column(String(100), nullable=True, unique=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    customer: Mapped[Customer | None] = relationship("Customer")
    items: Mapped[list[SalesInvoiceItem]] = relationship("SalesInvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments: Mapped[list[Payment]] = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")


class SalesInvoiceItem(Base, UUIDMixin, TimestampMixin):
    """Sales invoice line item preserving product pricing snapshot at time of sale."""

    __tablename__ = "sales_invoice_items"

    sales_invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_batches.id", ondelete="SET NULL"),
        nullable=True,
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=False,
    )
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)  # historical snapshot
    quantity: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)  # historical selling price
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)  # historical cost price
    discount_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=0.00, nullable=False)
    discount_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=13.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # Relationships
    invoice: Mapped[SalesInvoice] = relationship("SalesInvoice", back_populates="items")
    product: Mapped[Product] = relationship("Product")


class SalesReturn(Base, UUIDMixin, TimestampMixin):
    """Credit note / customer sales return."""

    __tablename__ = "sales_returns"
    __table_args__ = (
        UniqueConstraint("branch_id", "return_number", name="uq_sales_return_branch_number"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    pos_counter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos_counters.id", ondelete="SET NULL"),
        nullable=True,
    )
    sales_invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    return_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    return_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    return_date_bs: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    refund_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    refund_method: Mapped[str] = mapped_column(
        String(30), default="CASH", nullable=False
    )  # CASH, STORE_CREDIT, ORIGINAL_PAYMENT
    status: Mapped[str] = mapped_column(
        String(30), default="COMPLETED", nullable=False
    )  # COMPLETED, CANCELLED

    # Relationships
    invoice: Mapped[SalesInvoice] = relationship("SalesInvoice")
    items: Mapped[list[SalesReturnItem]] = relationship("SalesReturnItem", back_populates="sales_return", cascade="all, delete-orphan")


class SalesReturnItem(Base, UUIDMixin, TimestampMixin):
    """Items returned by customer."""

    __tablename__ = "sales_return_items"

    sales_return_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_returns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sales_invoice_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_invoice_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("stock_batches.id", ondelete="SET NULL"),
        nullable=True,
    )
    return_qty: Mapped[float] = mapped_column(Numeric(12, 3), nullable=False)
    refund_unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    total_refund: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    restock_inventory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    sales_return: Mapped[SalesReturn] = relationship("SalesReturn", back_populates="items")
    product: Mapped[Product] = relationship("Product")


class Payment(Base, UUIDMixin, TimestampMixin):
    """Payment record supporting mixed payment methods (Cash, eSewa, Khalti, Fonepay, Card, Credit)."""

    __tablename__ = "payments"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_invoices.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    return_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_returns.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    payment_method: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # CASH, ESEWA, KHALTI, FONEPAY, CARD, BANK_TRANSFER, KHATA_CREDIT, REWARD_POINTS
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    transaction_reference: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="COMPLETED", nullable=False)  # COMPLETED, FAILED, REFUNDED
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Relationships
    invoice: Mapped[SalesInvoice | None] = relationship("SalesInvoice", back_populates="payments")
