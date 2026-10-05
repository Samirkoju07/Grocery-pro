"""Organization models: Company, Branch, Warehouse, POSCounter."""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Index, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.auth import User


class Company(Base, UUIDMixin, TimestampMixin):
    """Company / Organization entity (top-level tenant)."""

    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pan_vat_number: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), default="NPR", nullable=False)
    default_vat_rate: Mapped[float] = mapped_column(Numeric(5, 2), default=13.00, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    branches: Mapped[list[Branch]] = relationship(
        "Branch",
        back_populates="company",
        cascade="all, delete-orphan",
    )
    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="company",
        foreign_keys="User.company_id",
    )


class Branch(Base, UUIDMixin, TimestampMixin):
    """Store branch entity."""

    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_branch_company_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    pan_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    company: Mapped[Company] = relationship("Company", back_populates="branches")
    warehouses: Mapped[list[Warehouse]] = relationship(
        "Warehouse",
        back_populates="branch",
        cascade="all, delete-orphan",
    )
    pos_counters: Mapped[list[POSCounter]] = relationship(
        "POSCounter",
        back_populates="branch",
        cascade="all, delete-orphan",
    )


class Warehouse(Base, UUIDMixin, TimestampMixin):
    """Warehouse / Storage location belonging to a branch."""

    __tablename__ = "warehouses"
    __table_args__ = (
        UniqueConstraint("branch_id", "code", name="uq_warehouse_branch_code"),
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
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    branch: Mapped[Branch] = relationship("Branch", back_populates="warehouses")


class POSCounter(Base, UUIDMixin, TimestampMixin):
    """POS billing counter terminal belonging to a branch."""

    __tablename__ = "pos_counters"
    __table_args__ = (
        UniqueConstraint("branch_id", "counter_number", name="uq_pos_counter_branch_number"),
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
    counter_number: Mapped[str] = mapped_column(String(30), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    branch: Mapped[Branch] = relationship("Branch", back_populates="pos_counters")
