"""Dev-only seed for F2 scope testing. Never run in production.

Creates demo users (admin + sales per subsidiary) and subsidiary-tagged
customers. Idempotent: existing rows (by external_id / customer_id) are
skipped. Refuses to run unless DEV_AUTH_ENABLED=true.

Usage:
    DEV_AUTH_ENABLED=true python seed_dev.py
    docker compose run --rm -e DEV_AUTH_ENABLED=true api python seed_dev.py
"""
from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.modules.customers.models import Customer
from app.modules.users.models import User

USERS = [
    {"external_id": "dev-admin", "email": "admin@local", "display_name": "Dev Admin", "role": "admin", "subsidiary_id": None},
    {"external_id": "dev-es", "email": "es@local", "display_name": "Dev Sales ES", "role": "sales", "subsidiary_id": "ES"},
    {"external_id": "dev-de", "email": "de@local", "display_name": "Dev Sales DE", "role": "sales", "subsidiary_id": "DE"},
    {"external_id": "dev-viewer", "email": "viewer@local", "display_name": "Dev Viewer", "role": "viewer", "subsidiary_id": "ES"},
]

CUSTOMERS = [
    {"customer_id": "0001012933", "account_name": "UAB Riela servisas", "country": "Lithuania", "subsidiary_id": "ES"},
    {"customer_id": "0010027007", "account_name": "E. W. Grobbel St. Clair Shores", "country": "USA", "subsidiary_id": "DE"},
]


def main() -> int:
    if not settings.dev_auth_enabled:
        print("Refusing to seed: set DEV_AUTH_ENABLED=true (dev only).")
        return 1
    db = SessionLocal()
    created_users = skipped_users = 0
    created_customers = skipped_customers = 0
    try:
        for data in USERS:
            exists = db.scalar(select(User).where(User.external_id == data["external_id"]))
            if exists is None:
                db.add(User(**data))
                created_users += 1
            else:
                skipped_users += 1
        for data in CUSTOMERS:
            exists = db.scalar(select(Customer).where(Customer.customer_id == data["customer_id"]))
            if exists is None:
                db.add(Customer(**data))
                created_customers += 1
            else:
                skipped_customers += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"users: {created_users} created, {skipped_users} skipped")
    print(f"customers: {created_customers} created, {skipped_customers} skipped")
    print("Dev identities: dev-admin (admin), dev-es (sales/ES), dev-de (sales/DE), dev-viewer (viewer/ES)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
