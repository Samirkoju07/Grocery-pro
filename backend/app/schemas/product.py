"""Pydantic schemas for Product module."""
from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------
# Category
# ---------------------------------------------------------
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    parent_id: uuid.UUID | None = None
    description: str | None = None
    is_active: bool = True


class CategoryCreate(CategoryBase):
    company_id: uuid.UUID


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------
# Brand
# ---------------------------------------------------------
class BrandBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=50)
    description: str | None = None
    is_active: bool = True


class BrandCreate(BrandBase):
    company_id: uuid.UUID


class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------
# Unit
# ---------------------------------------------------------
class UnitBase(BaseModel):
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=20)
    allow_decimal: bool = False
    is_active: bool = True


class UnitCreate(UnitBase):
    company_id: uuid.UUID


class UnitResponse(UnitBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------
# Tax Configuration
# ---------------------------------------------------------
class TaxConfigurationBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=30)
    rate: Decimal = Field(..., ge=0, le=100)
    is_inclusive: bool = True
    is_default: bool = False
    is_active: bool = True


class TaxConfigurationCreate(TaxConfigurationBase):
    company_id: uuid.UUID


class TaxConfigurationResponse(TaxConfigurationBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    created_at: datetime


# ---------------------------------------------------------
# Product Barcode
# ---------------------------------------------------------
class ProductBarcodeBase(BaseModel):
    barcode: str = Field(..., max_length=100)
    barcode_type: str = "EAN13"
    is_primary: bool = False


class ProductBarcodeResponse(ProductBarcodeBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID


# ---------------------------------------------------------
# Product Price
# ---------------------------------------------------------
class ProductPriceBase(BaseModel):
    cost_price: Decimal = Field(Decimal("0.00"), ge=0)
    selling_price: Decimal = Field(..., ge=0)
    marked_price: Decimal = Field(..., ge=0)
    effective_from: datetime
    effective_to: datetime | None = None
    is_active: bool = True


class ProductPriceResponse(ProductPriceBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    branch_id: uuid.UUID | None


# ---------------------------------------------------------
# Product Master
# ---------------------------------------------------------
class ProductBase(BaseModel):
    name: str = Field(..., max_length=200)
    name_nepali: str | None = None
    sku: str = Field(..., max_length=100)
    barcode: str | None = None
    description: str | None = None
    is_weighted: bool = False
    is_batch_tracked: bool = False
    min_stock_alert: Decimal = Decimal("0.000")
    max_stock_alert: Decimal | None = None
    is_active: bool = True


class ProductCreate(ProductBase):
    company_id: uuid.UUID
    category_id: uuid.UUID | None = None
    brand_id: uuid.UUID | None = None
    unit_id: uuid.UUID
    tax_id: uuid.UUID | None = None
    cost_price: Decimal = Decimal("0.00")
    selling_price: Decimal = Decimal("0.00")
    marked_price: Decimal = Decimal("0.00")


class ProductResponse(ProductBase):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    company_id: uuid.UUID
    category_id: uuid.UUID | None
    brand_id: uuid.UUID | None
    unit_id: uuid.UUID
    tax_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
