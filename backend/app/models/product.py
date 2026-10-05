"""Product models: Category, Brand, Unit, TaxConfiguration, Product, ProductBarcode, ProductPrice."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import AuditMixin, SoftDeleteMixin, TimestampMixin, UUIDMixin


class Category(Base, UUIDMixin, TimestampMixin):
    """Hierarchical product category."""

    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_category_company_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    subcategories: Mapped[list[Category]] = relationship("Category", backref="parent", remote_side="Category.id")
    products: Mapped[list[Product]] = relationship("Product", back_populates="category")


class Brand(Base, UUIDMixin, TimestampMixin):
    """Product brand."""

    __tablename__ = "brands"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_brand_company_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    products: Mapped[list[Product]] = relationship("Product", back_populates="brand")


class Unit(Base, UUIDMixin, TimestampMixin):
    """Unit of measurement (kg, pcs, ltr, etc.)."""

    __tablename__ = "units"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_unit_company_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    code: Mapped[str] = mapped_column(String(20), nullable=False)
    allow_decimal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    products: Mapped[list[Product]] = relationship("Product", back_populates="unit")


class TaxConfiguration(Base, UUIDMixin, TimestampMixin):
    """Tax configuration (e.g., VAT 13% for Nepal, 0% exempt)."""

    __tablename__ = "tax_configurations"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_tax_company_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(30), nullable=False)
    rate: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    is_inclusive: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    products: Mapped[list[Product]] = relationship("Product", back_populates="tax")


class Product(Base, UUIDMixin, TimestampMixin, AuditMixin, SoftDeleteMixin):
    """Product master entity."""

    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("company_id", "sku", name="uq_product_company_sku"),
        Index("ix_product_company_name", "company_id", "name"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    brand_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("brands.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("units.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    tax_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tax_configurations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name_nepali: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    barcode: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_weighted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_batch_tracked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    min_stock_alert: Mapped[float] = mapped_column(Numeric(12, 3), default=0, nullable=False)
    max_stock_alert: Mapped[float | None] = mapped_column(Numeric(12, 3), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    category: Mapped[Category | None] = relationship("Category", back_populates="products")
    brand: Mapped[Brand | None] = relationship("Brand", back_populates="products")
    unit: Mapped[Unit] = relationship("Unit", back_populates="products")
    tax: Mapped[TaxConfiguration | None] = relationship("TaxConfiguration", back_populates="products")
    barcodes: Mapped[list[ProductBarcode]] = relationship("ProductBarcode", back_populates="product", cascade="all, delete-orphan")
    prices: Mapped[list[ProductPrice]] = relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")


class ProductBarcode(Base, UUIDMixin, TimestampMixin):
    """Barcodes associated with a product (supports multiple barcodes per SKU)."""

    __tablename__ = "product_barcodes"
    __table_args__ = (
        UniqueConstraint("company_id", "barcode", name="uq_barcode_company_value"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    barcode: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    barcode_type: Mapped[str] = mapped_column(String(30), default="EAN13", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    product: Mapped[Product] = relationship("Product", back_populates="barcodes")


class ProductPrice(Base, UUIDMixin, TimestampMixin):
    """Product price history and branch-specific pricing."""

    __tablename__ = "product_prices"
    __table_args__ = (
        CheckConstraint("selling_price >= 0", name="chk_selling_price_non_negative"),
        CheckConstraint("cost_price >= 0", name="chk_cost_price_non_negative"),
        Index("ix_product_price_active", "product_id", "is_active", "effective_from"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    cost_price: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    selling_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    marked_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    effective_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    product: Mapped[Product] = relationship("Product", back_populates="prices")
