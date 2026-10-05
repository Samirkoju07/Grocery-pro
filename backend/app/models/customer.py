"""Customer models: Customer, CustomerLedger, CustomerPayment."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import SoftDeleteMixin, TimestampMixin, UUIDMixin


class Customer(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Customer entity (supports Khata credit and loyalty)."""

    __tablename__ = "customers"
    __table_args__ = (
        Index("ix_customer_company_phone", "company_id", "phone"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True, index=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    credit_limit: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)  # Khata limit
    current_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)  # positive = amount owed to store
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    ledger_entries: Mapped[list[CustomerLedger]] = relationship("CustomerLedger", back_populates="customer", cascade="all, delete-orphan")
    payments: Mapped[list[CustomerPayment]] = relationship("CustomerPayment", back_populates="customer", cascade="all, delete-orphan")


class CustomerLedger(Base, UUIDMixin, TimestampMixin):
    """Immutable financial ledger for customer credit / Khata. Never physically deleted."""

    __tablename__ = "customer_ledgers"
    __table_args__ = (
        Index("ix_customer_ledger_timeline", "customer_id", "entry_date"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entry_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    entry_type: Mapped[str] = mapped_column(
        String(30), nullable=False, index=True
    )  # INVOICE, PAYMENT, SALES_RETURN, OPENING_BALANCE, ADJUSTMENT
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)  # sales_invoice, customer_payment, sales_return
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    debit: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)  # increases customer debt
    credit: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)  # decreases customer debt (payment received)
    running_balance: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    customer: Mapped[Customer] = relationship("Customer", back_populates="ledger_entries")


class CustomerPayment(Base, UUIDMixin, TimestampMixin):
    """Customer payment received against Khata credit."""

    __tablename__ = "customer_payments"
    __table_args__ = (
        UniqueConstraint("company_id", "payment_number", name="uq_cust_pmt_company_number"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    payment_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    payment_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_mode: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # CASH, ESEWA, KHALTI, FONEPAY, BANK_TRANSFER, CHEQUE
    reference_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    received_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    customer: Mapped[Customer] = relationship("Customer", back_populates="payments")
