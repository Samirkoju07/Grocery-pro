"""Database seed script – creates core roles and a super‑admin user.
Run with:  
    python -m app.scripts.seed
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.auth import Role, Permission, RolePermission, User, UserRole
from app.models.organization import Company
from app.core.security import hash_password

# ---------------------------------------------------------------------------
# Core permissions (a subset – you can extend this list later)
# ---------------------------------------------------------------------------
CORE_PERMISSIONS = [
    "sales.create",
    "sales.cancel",
    "sales.void",
    "sales.return",
    "sales.refund",
    "sales.view",
    "sales.discount",
    "sales.change_price",
    "products.create",
    "products.update",
    "products.delete",
    "products.view",
    "inventory.view",
    "inventory.adjust",
    "inventory.approve_adjustment",
    "inventory.transfer",
    "inventory.count",
    "purchase.create",
    "purchase.approve",
    "purchase.receive",
    "purchase.return",
    "purchase.view",
    "users.create",
    "users.update",
    "users.disable",
    "settings.manage",
    "audit.view",
]

# ---------------------------------------------------------------------------
# Role definitions – name, code, and which permissions they get
# ---------------------------------------------------------------------------
ROLE_DEFINITIONS = {
    "Owner": {
        "code": "owner",
        "permissions": CORE_PERMISSIONS,
    },
    "Manager": {
        "code": "manager",
        "permissions": [
            "sales.create",
            "sales.view",
            "products.create",
            "products.view",
            "inventory.view",
            "inventory.adjust",
        ],
    },
    "Cashier": {
        "code": "cashier",
        "permissions": ["sales.create", "sales.view", "cash.open", "cash.close"],
    },
    "Inventory Staff": {
        "code": "inventory_staff",
        "permissions": ["inventory.view", "inventory.adjust", "inventory.transfer"],
    },
    "Accountant": {
        "code": "accountant",
        "permissions": ["cash.view", "expenses.view", "reports.profit"],
    },
    "Admin": {
        "code": "admin",
        "permissions": CORE_PERMISSIONS,
    },
}


def create_permission(session, code: str) -> Permission:
    module, action = code.split(".")
    perm = Permission(
        module=module,
        action=action,
        code=code,
        description=f"{module} {action}",
    )
    session.add(perm)
    return perm


def seed(db):
    # 1️⃣ Create a demo company (tenant)
    company = Company(name="Demo Co", currency="NPR")
    db.add(company)
    db.flush()  # assign id

    # 2️⃣ Insert all core permissions (skip duplicates)
    existing_perms = {p.code for p in db.execute(select(Permission)).scalars()}
    for code in CORE_PERMISSIONS:
        if code not in existing_perms:
            create_permission(db, code)
    db.commit()

    # 3️⃣ Create roles + role‑permission links
    for role_name, spec in ROLE_DEFINITIONS.items():
        role = db.execute(select(Role).where(Role.code == spec["code"]))
        role_obj = role.scalar_one_or_none()
        if not role_obj:
            role_obj = Role(
                name=role_name,
                code=spec["code"],
                company_id=company.id,
                is_system=True,
                is_active=True,
            )
            db.add(role_obj)
            db.flush()
        # link permissions
        for perm_code in spec["permissions"]:
            perm = db.execute(select(Permission).where(Permission.code == perm_code)).scalar_one()
            # avoid duplicate role‑permission rows
            exists = db.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role_obj.id,
                    RolePermission.permission_id == perm.id,
                )
            ).first()
            if not exists:
                db.add(RolePermission(role_id=role_obj.id, permission_id=perm.id))
    db.commit()

    # 4️⃣ Create a super‑admin user and assign the Owner role
    admin_user = User(
        email="admin@example.com",
        username="admin",
        full_name="Super Admin",
        hashed_password=hash_password("SuperSecret123!"),
        company_id=company.id,
        is_superuser=True,
    )
    db.add(admin_user)
    db.flush()
    owner_role = db.execute(select(Role).where(Role.code == "owner")).scalar_one()
    db.add(UserRole(user_id=admin_user.id, role_id=owner_role.id, branch_id=None))
    db.commit()

    print("✅ Seed completed – demo company, permissions, roles, and admin user created.")


if __name__ == "__main__":
    with SessionLocal() as session:
        seed(session)
