"""Database seed script.

Seeds standard roles and granular permissions.
Does NOT create fake product or transaction data.
"""
from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.db.session import SessionLocal, engine
from app.models.auth import Permission, Role, RolePermission

log = get_logger(__name__)

# -----------------------------------------------------------------------------
# System permissions categorized by module
# -----------------------------------------------------------------------------
SYSTEM_PERMISSIONS: list[dict[str, str]] = [
    # Organization
    {"module": "organization", "action": "company:read", "code": "company:read", "description": "View company profile"},
    {"module": "organization", "action": "company:update", "code": "company:update", "description": "Update company profile"},
    {"module": "organization", "action": "branch:create", "code": "branch:create", "description": "Create new branch"},
    {"module": "organization", "action": "branch:read", "code": "branch:read", "description": "View branches"},
    {"module": "organization", "action": "branch:update", "code": "branch:update", "description": "Update branch"},
    {"module": "organization", "action": "warehouse:create", "code": "warehouse:create", "description": "Create warehouse"},
    {"module": "organization", "action": "warehouse:read", "code": "warehouse:read", "description": "View warehouses"},
    {"module": "organization", "action": "warehouse:update", "code": "warehouse:update", "description": "Update warehouse"},
    {"module": "organization", "action": "pos_counter:manage", "code": "pos_counter:manage", "description": "Manage POS counters"},

    # Users & Roles
    {"module": "auth", "action": "user:create", "code": "user:create", "description": "Create user account"},
    {"module": "auth", "action": "user:read", "code": "user:read", "description": "View user accounts"},
    {"module": "auth", "action": "user:update", "code": "user:update", "description": "Update user account"},
    {"module": "auth", "action": "user:delete", "code": "user:delete", "description": "Deactivate user account"},
    {"module": "auth", "action": "role:manage", "code": "role:manage", "description": "Manage roles and permissions"},

    # Products & Catalog
    {"module": "product", "action": "product:create", "code": "product:create", "description": "Create product"},
    {"module": "product", "action": "product:read", "code": "product:read", "description": "View products and catalog"},
    {"module": "product", "action": "product:update", "code": "product:update", "description": "Update product details"},
    {"module": "product", "action": "product:delete", "code": "product:delete", "description": "Archive/delete product"},
    {"module": "product", "action": "price:update", "code": "price:update", "description": "Update product selling or cost prices"},
    {"module": "product", "action": "category:manage", "code": "category:manage", "description": "Manage categories and brands"},
    {"module": "product", "action": "unit:manage", "code": "unit:manage", "description": "Manage measurement units"},
    {"module": "product", "action": "tax:manage", "code": "tax:manage", "description": "Manage tax configurations"},

    # Inventory
    {"module": "inventory", "action": "inventory:read", "code": "inventory:read", "description": "View stock levels"},
    {"module": "inventory", "action": "adjustment:create", "code": "adjustment:create", "description": "Create stock adjustment"},
    {"module": "inventory", "action": "adjustment:approve", "code": "adjustment:approve", "description": "Approve stock adjustment"},
    {"module": "inventory", "action": "stock_count:perform", "code": "stock_count:perform", "description": "Perform physical stock count"},
    {"module": "inventory", "action": "stock_count:reconcile", "code": "stock_count:reconcile", "description": "Reconcile stock discrepancies"},
    {"module": "inventory", "action": "transfer:create", "code": "transfer:create", "description": "Initiate stock transfer"},
    {"module": "inventory", "action": "transfer:receive", "code": "transfer:receive", "description": "Receive stock transfer"},

    # Purchase
    {"module": "purchase", "action": "supplier:manage", "code": "supplier:manage", "description": "Manage suppliers"},
    {"module": "purchase", "action": "supplier:read", "code": "supplier:read", "description": "View suppliers"},
    {"module": "purchase", "action": "po:create", "code": "po:create", "description": "Create purchase order"},
    {"module": "purchase", "action": "grn:receive", "code": "grn:receive", "description": "Receive goods (GRN)"},
    {"module": "purchase", "action": "invoice:create", "code": "purchase_invoice:create", "description": "Create purchase invoice"},
    {"module": "purchase", "action": "invoice:read", "code": "purchase_invoice:read", "description": "View purchase invoices"},
    {"module": "purchase", "action": "return:create", "code": "purchase_return:create", "description": "Create purchase return"},

    # Customer & Khata
    {"module": "customer", "action": "customer:manage", "code": "customer:manage", "description": "Manage customer accounts"},
    {"module": "customer", "action": "customer:read", "code": "customer:read", "description": "View customer directory"},
    {"module": "customer", "action": "khata:credit", "code": "khata:credit", "description": "Issue customer credit (Khata)"},
    {"module": "customer", "action": "khata:collect", "code": "khata:collect", "description": "Receive customer credit payment"},
    {"module": "customer", "action": "ledger:read", "code": "customer_ledger:read", "description": "View customer ledger history"},

    # POS & Sales
    {"module": "sales", "action": "pos:bill", "code": "pos:bill", "description": "Create sales invoice / POS billing"},
    {"module": "sales", "action": "invoice:read", "code": "sales_invoice:read", "description": "View sales invoices"},
    {"module": "sales", "action": "invoice:void", "code": "sales_invoice:void", "description": "Void/cancel sales invoice"},
    {"module": "sales", "action": "discount:apply", "code": "discount:apply", "description": "Apply invoice/item discount"},
    {"module": "sales", "action": "return:create", "code": "sales_return:create", "description": "Process sales return / refund"},

    # Cash Drawer & Expenses
    {"module": "cash", "action": "session:open", "code": "cash_session:open", "description": "Open cashier shift session"},
    {"module": "cash", "action": "session:close", "code": "cash_session:close", "description": "Close cashier shift session"},
    {"module": "cash", "action": "drawer:transaction", "code": "cash_drawer:transaction", "description": "Perform cash in / cash out / safe drop"},
    {"module": "cash", "action": "expense:create", "code": "expense:create", "description": "Record store expense"},
    {"module": "cash", "action": "expense:approve", "code": "expense:approve", "description": "Approve store expense"},
    {"module": "cash", "action": "expense:read", "code": "expense:read", "description": "View expense reports"},

    # Promotions & Loyalty
    {"module": "promotion", "action": "promotion:manage", "code": "promotion:manage", "description": "Create and manage promotions and coupons"},
    {"module": "loyalty", "action": "loyalty:manage", "code": "loyalty:manage", "description": "Manage loyalty program and points"},

    # Reports & Audit
    {"module": "reports", "action": "sales:view", "code": "report:sales", "description": "View sales reports and analytics"},
    {"module": "reports", "action": "inventory:view", "code": "report:inventory", "description": "View stock reports and valuation"},
    {"module": "reports", "action": "financial:view", "code": "report:financial", "description": "View financial and VAT reports"},
    {"module": "audit", "action": "audit:view", "code": "audit:view", "description": "View system audit logs"},
]

# -----------------------------------------------------------------------------
# Standard System Roles with Codes and Permissions mapping
# -----------------------------------------------------------------------------
STANDARD_ROLES = [
    {
        "name": "Owner",
        "code": "owner",
        "description": "Full access to all modules, financial data, and system configurations.",
        "is_system": True,
        "permissions": "*",  # all
    },
    {
        "name": "Admin",
        "code": "admin",
        "description": "System administrator with organization, user, and catalog management access.",
        "is_system": True,
        "permissions": "*",  # all
    },
    {
        "name": "Manager",
        "code": "manager",
        "description": "Store/branch manager with inventory, cash, billing, approval, and reporting authority.",
        "is_system": True,
        "permissions": [
            "company:read", "branch:read", "warehouse:read", "pos_counter:manage",
            "user:read", "product:create", "product:read", "product:update",
            "price:update", "category:manage", "unit:manage", "tax:manage",
            "inventory:read", "adjustment:create", "adjustment:approve",
            "stock_count:perform", "stock_count:reconcile", "transfer:create", "transfer:receive",
            "supplier:manage", "supplier:read", "po:create", "grn:receive",
            "purchase_invoice:create", "purchase_invoice:read", "purchase_return:create",
            "customer:manage", "customer:read", "khata:credit", "khata:collect", "customer_ledger:read",
            "pos:bill", "sales_invoice:read", "sales_invoice:void", "discount:apply", "sales_return:create",
            "cash_session:open", "cash_session:close", "cash_drawer:transaction",
            "expense:create", "expense:approve", "expense:read",
            "promotion:manage", "loyalty:manage",
            "report:sales", "report:inventory", "report:financial", "audit:view",
        ],
    },
    {
        "name": "Cashier",
        "code": "cashier",
        "description": "POS billing, cash drawer operations, and customer checkouts.",
        "is_system": True,
        "permissions": [
            "branch:read", "product:read", "inventory:read",
            "customer:read", "customer:manage", "khata:credit",
            "pos:bill", "sales_invoice:read", "discount:apply", "sales_return:create",
            "cash_session:open", "cash_session:close", "cash_drawer:transaction",
            "expense:create",
        ],
    },
    {
        "name": "Inventory Staff",
        "code": "inventory_staff",
        "description": "Stock management, receiving goods, counts, and warehouse transfers.",
        "is_system": True,
        "permissions": [
            "branch:read", "warehouse:read", "product:read", "product:create", "product:update",
            "category:manage", "unit:manage",
            "inventory:read", "adjustment:create",
            "stock_count:perform", "transfer:create", "transfer:receive",
            "supplier:read", "grn:receive", "purchase_return:create",
            "report:inventory",
        ],
    },
    {
        "name": "Accountant",
        "code": "accountant",
        "description": "Financial records, customer/supplier ledgers, expenses, and tax/VAT reporting.",
        "is_system": True,
        "permissions": [
            "company:read", "branch:read", "supplier:read", "supplier:manage",
            "purchase_invoice:read", "purchase_invoice:create", "purchase_return:create",
            "customer:read", "customer:manage", "khata:collect", "customer_ledger:read",
            "sales_invoice:read", "expense:create", "expense:approve", "expense:read",
            "report:sales", "report:inventory", "report:financial", "audit:view",
        ],
    },
]


def seed_database(db: Session) -> dict[str, int]:
    """Seed initial permissions and roles. Idempotent."""
    log.info("Starting database seed...")

    # 1. Seed Permissions
    created_perms = 0
    perm_cache: dict[str, Permission] = {}

    for perm_data in SYSTEM_PERMISSIONS:
        stmt = select(Permission).where(Permission.code == perm_data["code"])
        perm = db.execute(stmt).scalar_one_or_none()
        if not perm:
            perm = Permission(
                module=perm_data["module"],
                action=perm_data["action"],
                code=perm_data["code"],
                description=perm_data["description"],
            )
            db.add(perm)
            db.flush()
            created_perms += 1
        perm_cache[perm.code] = perm

    log.info("Permissions processed", total=len(perm_cache), newly_created=created_perms)

    # 2. Seed Roles
    created_roles = 0
    created_mappings = 0

    for role_def in STANDARD_ROLES:
        stmt = select(Role).where(Role.code == role_def["code"], Role.company_id.is_(None))
        role = db.execute(stmt).scalar_one_or_none()
        if not role:
            role = Role(
                name=role_def["name"],
                code=role_def["code"],
                description=role_def["description"],
                is_system=role_def["is_system"],
                is_active=True,
                company_id=None,
            )
            db.add(role)
            db.flush()
            created_roles += 1

        # Determine permissions to assign
        target_perm_codes: list[str]
        if role_def["permissions"] == "*":
            target_perm_codes = list(perm_cache.keys())
        else:
            target_perm_codes = role_def["permissions"]

        # Assign permissions
        for code in target_perm_codes:
            if code not in perm_cache:
                continue
            perm_id = perm_cache[code].id
            # Check existing mapping
            check_stmt = select(RolePermission).where(
                RolePermission.role_id == role.id,
                RolePermission.permission_id == perm_id,
            )
            if not db.execute(check_stmt).scalar_one_or_none():
                db.add(RolePermission(role_id=role.id, permission_id=perm_id))
                created_mappings += 1

    db.commit()
    log.info(
        "Database seed completed successfully",
        created_permissions=created_perms,
        created_roles=created_roles,
        created_role_permissions=created_mappings,
    )

    return {
        "permissions": len(perm_cache),
        "roles": len(STANDARD_ROLES),
        "new_roles": created_roles,
        "new_mappings": created_mappings,
    }


if __name__ == "__main__":
    with SessionLocal() as session:
        results = seed_database(session)
        print("Seed finished:", results)
