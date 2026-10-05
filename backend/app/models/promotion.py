"""Promotion models: Promotion, PromotionProduct, PromotionCategory, Coupon."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.base import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.product import Category, Product


class Promotion(Base, UUIDMixin, TimestampMixin):
    """Marketing promotion discount rule."""

    __tablename__ = "promotions"

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    promo_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PERCENTAGE_DISCOUNT, FLAT_DISCOUNT, BUY_X_GET_Y, BUNDLE_PRICE
    discount_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    min_order_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    max_discount_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    products: Mapped[list[PromotionProduct]] = relationship("PromotionProduct", back_populates="promotion", cascade="all, delete-orphan")
    categories: Mapped[list[PromotionCategory]] = relationship("PromotionCategory", back_populates="promotion", cascade="all, delete-orphan")
    coupons: Mapped[list[Coupon]] = relationship("Coupon", back_populates="promotion", cascade="all, delete-orphan")


class PromotionProduct(Base, UUIDMixin, TimestampMixin):
    """Products applicable under a promotion."""

    __tablename__ = "promotion_products"
    __table_args__ = (
        UniqueConstraint("promotion_id", "product_id", name="uq_promo_product"),
    )

    promotion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_gift_item: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # For Buy X Get Y

    # Relationships
    promotion: Mapped[Promotion] = relationship("Promotion", back_populates="products")
    product: Mapped[Product] = relationship("Product")


class PromotionCategory(Base, UUIDMixin, TimestampMixin):
    """Categories applicable under a promotion."""

    __tablename__ = "promotion_categories"
    __table_args__ = (
        UniqueConstraint("promotion_id", "category_id", name="uq_promo_category"),
    )

    promotion_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("promotions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    promotion: Mapped[Promotion] = relationship("Promotion", back_populates="categories")
    category: Mapped[Category] = relationship("Category")


class Coupon(Base, UUIDMixin, TimestampMixin):
    """Discount coupon code."""

    __tablename__ = "coupons"
    __table_args__ = (
        UniqueConstraint("company_id", "code", name="uq_coupon_company_code"),
    )

    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    promotion_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("promotions.id", ondelete="SET NULL"),
        nullable=True,
    )
    code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    discount_type: Mapped[str] = mapped_column(String(30), default="PERCENTAGE", nullable=False)  # PERCENTAGE, FIXED
    discount_value: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    min_spend: Mapped[float] = mapped_column(Numeric(12, 2), default=0.00, nullable=False)
    max_discount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    usage_limit: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    times_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    valid_from: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    valid_to: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    promotion: Mapped[Promotion | None] = relationship("Promotion", back_populates="coupons")
