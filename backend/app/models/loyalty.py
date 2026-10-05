"""Loyalty models: LoyaltyAccount, LoyaltyTransaction."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.sales import SalesInvoice


class LoyaltyAccount(Base, UUIDMixin, TimestampMixin):
    """Customer loyalty points account."""

    __tablename__ = "loyalty_accounts"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    card_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True, index=True)
    current_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    lifetime_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tier: Mapped[str] = mapped_column(String(30), default="BRONZE", nullable=False)  # BRONZE, SILVER, GOLD, PLATINUM
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    customer: Mapped[Customer] = relationship("Customer")
    transactions: Mapped[list[LoyaltyTransaction]] = relationship("LoyaltyTransaction", back_populates="account", cascade="all, delete-orphan")


class LoyaltyTransaction(Base, UUIDMixin, TimestampMixin):
    """Loyalty points earn and redeem ledger."""

    __tablename__ = "loyalty_transactions"

    loyalty_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("loyalty_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    txn_type: Mapped[str] = mapped_column(String(30), nullable=False)  # EARNED, REDEEMED, EXPIRED, ADJUSTED
    points: Mapped[int] = mapped_column(Integer, nullable=False)  # positive = earned, negative = redeemed
    points_before: Mapped[int] = mapped_column(Integer, nullable=False)
    points_after: Mapped[int] = mapped_column(Integer, nullable=False)
    sales_invoice_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sales_invoices.id", ondelete="SET NULL"),
        nullable=True,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    account: Mapped[LoyaltyAccount] = relationship("LoyaltyAccount", back_populates="transactions")
