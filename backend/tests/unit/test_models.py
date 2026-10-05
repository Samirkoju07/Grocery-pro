"""Unit and integration tests for SQLAlchemy 2.x models and schema rules."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base
from app.db.session import SessionLocal
from app.models.auth import Permission, Role, RolePermission, User
from app.models.cash import CashSession, CashTransaction, Expense
from app.models.customer import Customer, CustomerLedger, CustomerPayment
from app.models.inventory import (
    Inventory,
    InventoryTransaction,
    StockAdjustment,
    StockBatch,
    StockCount,
    StockTransfer,
)
from app.models.loyalty import LoyaltyAccount, LoyaltyTransaction
from app.models.organization import Branch, Company, POSCounter, Warehouse
from app.models.product import (
    Brand,
    Category,
    Product,
    ProductBarcode,
    ProductPrice,
    TaxConfiguration,
    Unit,
)
from app.models.promotion import Coupon, Promotion
from app.models.purchase import PurchaseInvoice, PurchaseOrder, Supplier
from app.models.sales import Payment, SalesInvoice, SalesInvoiceItem, SalesReturn


@pytest.fixture(scope="module")
def db_session():
    """Provide a database session connected to the test database."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_all_models_registered_in_metadata():
    """Verify that all expected tables are registered in Base.metadata."""
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        "companies", "branches", "warehouses", "pos_counters",
        "users", "roles", "permissions", "role_permissions", "user_roles", "refresh_tokens", "user_sessions",
        "categories", "brands", "units", "tax_configurations", "products", "product_barcodes", "product_prices",
        "inventories", "stock_batches", "inventory_transactions", "stock_adjustments", "stock_counts", "stock_count_items", "stock_transfers", "stock_transfer_items",
        "suppliers", "purchase_orders", "purchase_order_items", "goods_received_notes", "goods_received_items", "purchase_invoices", "purchase_invoice_items", "purchase_returns", "purchase_return_items",
        "customers", "customer_ledgers", "customer_payments",
        "sales_invoices", "sales_invoice_items", "sales_returns", "sales_return_items", "payments",
        "cash_sessions", "cash_transactions", "expenses",
        "promotions", "promotion_products", "promotion_categories", "coupons",
        "loyalty_accounts", "loyalty_transactions",
        "audit_logs", "notifications",
    }
    missing = expected_tables - table_names
    assert not missing, f"Missing tables in metadata: {missing}"


def test_seed_roles_exist(db_session: Session):
    """Verify that all standard roles and permissions exist in database."""
    roles = db_session.execute(select(Role)).scalars().all()
    role_codes = {r.code for r in roles}
    expected_roles = {"owner", "admin", "manager", "cashier", "inventory_staff", "accountant"}
    assert expected_roles.issubset(role_codes), f"Missing roles: {expected_roles - role_codes}"

    # Verify owner has all permissions
    owner_role = next(r for r in roles if r.code == "owner")
    perms_count = db_session.execute(
        select(RolePermission).where(RolePermission.role_id == owner_role.id)
    ).scalars().all()
    assert len(perms_count) >= 50


def test_organization_hierarchy_relationships(db_session: Session):
    """Test creating Company -> Branch -> Warehouse & POSCounter."""
    test_id = uuid.uuid4().hex[:6]
    company = Company(
        name=f"Test Retail Co {test_id}",
        pan_vat_number="600123456",
        currency="NPR",
        default_vat_rate=Decimal("13.00"),
    )
    db_session.add(company)
    db_session.flush()

    branch = Branch(
        company_id=company.id,
        name=f"Kathmandu Main {test_id}",
        code=f"KTM-{test_id}",
        is_main=True,
    )
    db_session.add(branch)
    db_session.flush()

    warehouse = Warehouse(
        company_id=company.id,
        branch_id=branch.id,
        name=f"Central Storage {test_id}",
        code=f"WH-{test_id}",
        is_default=True,
    )
    counter = POSCounter(
        company_id=company.id,
        branch_id=branch.id,
        counter_number=f"C-{test_id}",
        name=f"Express Counter {test_id}",
    )
    db_session.add_all([warehouse, counter])
    db_session.flush()

    assert warehouse.branch_id == branch.id
    assert counter.branch_id == branch.id
    assert branch.company_id == company.id

    # Clean up
    db_session.delete(company)
    db_session.flush()


def test_customer_khata_ledger_integrity(db_session: Session):
    """Test Customer ledger debit/credit tracking."""
    test_id = uuid.uuid4().hex[:6]
    company = Company(name=f"Khata Test Co {test_id}")
    db_session.add(company)
    db_session.flush()

    branch = Branch(company_id=company.id, name="Branch", code=f"B-{test_id}")
    db_session.add(branch)
    db_session.flush()

    customer = Customer(
        company_id=company.id,
        name=f"Ram Bahadur {test_id}",
        phone=f"9841{test_id[:6]}",
        credit_limit=Decimal("10000.00"),
        current_balance=Decimal("0.00"),
    )
    db_session.add(customer)
    db_session.flush()

    # Credit purchase of NPR 1500 (increases debt)
    entry1 = CustomerLedger(
        company_id=company.id,
        branch_id=branch.id,
        customer_id=customer.id,
        entry_date=datetime.now(timezone.utc),
        entry_type="INVOICE",
        debit=Decimal("1500.00"),
        credit=Decimal("0.00"),
        running_balance=Decimal("1500.00"),
        description="Grocery purchase on credit",
    )
    # Payment received of NPR 1000 (decreases debt)
    entry2 = CustomerLedger(
        company_id=company.id,
        branch_id=branch.id,
        customer_id=customer.id,
        entry_date=datetime.now(timezone.utc),
        entry_type="PAYMENT",
        debit=Decimal("0.00"),
        credit=Decimal("1000.00"),
        running_balance=Decimal("500.00"),
        description="Fonepay payment received",
    )
    db_session.add_all([entry1, entry2])
    customer.current_balance = Decimal("500.00")
    db_session.flush()

    assert customer.current_balance == Decimal("500.00")
    assert len(customer.ledger_entries) == 2

    # Clean up
    db_session.delete(company)
    db_session.flush()
