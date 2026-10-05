"""Cash drawer and expense models: CashSession, CashTransaction, Expense."""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.auth import User


class CashSession(Base, UUIDMixin, TimestampMixin):
    """POS Cash drawer shift session."""

    __tablename__ = "cash_sessions"
    __table_args__ = (
        UniqueConstraint("branch_id", "session_number", name="uq_cash_session_branch_number"),
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
    pos_counter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("pos_counters.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    session_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    opening_balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    closing_balance_expected: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    closing_balance_counted: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    discrepancy: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="OPEN", nullable=False, index=True)  # OPEN, CLOSED
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    transactions: Mapped[list[CashTransaction]] = relationship("CashTransaction", back_populates="cash_session", cascade="all, delete-orphan")


class CashTransaction(Base, UUIDMixin, TimestampMixin):
    """Cash-in, cash-out, drop, or payout from drawer."""

    __tablename__ = "cash_transactions"

    cash_session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cash_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    txn_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )  # CASH_IN, CASH_OUT, SAFE_DROP, PAYOUT, EXPENSE
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )

    # Relationships
    cash_session: Mapped[CashSession] = relationship("CashSession", back_populates="transactions")


class Expense(Base, UUIDMixin, TimestampMixin):
    """Store operational expense."""

    __tablename__ = "expenses"
    __table_args__ = (
        UniqueConstraint("company_id", "expense_number", name="uq_expense_company_number"),
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
    cash_session_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cash_sessions.id", ondelete="SET NULL"),
        nullable=True,
    )
    expense_number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # TEA_SNACKS, CLEANING, UTILITY, STATIONERY, MAINTENANCE, TRANSPORT, OTHER
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_mode: Mapped[str] = mapped_column(
        String(30), default="CASH", nullable=False
    )  # CASH, BANK_TRANSFER, CARD, ESEWA, FONEPAY
    expense_date: Mapped[date] = mapped_column(Date, nullable=False)
    payee: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    receipt_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
