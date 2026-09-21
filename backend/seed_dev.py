"""Dev-only seed for scope testing and catalog demos. Never run in production.

Creates demo users (admin + sales per subsidiary), subsidiary-tagged
customers and catalog rows (prices, distances, basic kits) with the demo
values the UI used to type by hand. Idempotent: existing rows are skipped.
Refuses to run unless DEV_AUTH_ENABLED=true.

Usage:
    DEV_AUTH_ENABLED=true python seed_dev.py
    docker compose run --rm -e DEV_AUTH_ENABLED=true api python seed_dev.py
"""
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.modules.basic_kit.models import BasicKit
from app.modules.customers.models import Customer
from app.modules.distances.models import Distance
from app.modules.prices.models import PriceList
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

PRICES = [
    {"subsidiary_id": "ES", "km_rate": Decimal("0.5"), "tech_rate": Decimal("60"),
     "diet_full_rate": Decimal("40"), "diet_half_rate": Decimal("20"), "hotel_rate": Decimal("80")},
    {"subsidiary_id": "DE", "km_rate": Decimal("0.5"), "tech_rate": Decimal("60"),
     "diet_full_rate": Decimal("40"), "diet_half_rate": Decimal("20"), "hotel_rate": Decimal("80")},
]

DISTANCES = [
    {"province": "Madrid", "km": Decimal("350"), "trip_hours": Decimal("4")},
    {"province": "Barcelona", "km": Decimal("120"), "trip_hours": Decimal("1.5")},
]

BASIC_KITS = [
    {"model": "CCS304", "workload_basic_kit": Decimal("4"), "spare_parts": Decimal("500")},
]


def main() -> int:
    if not settings.dev_auth_enabled:
        print("Refusing to seed: set DEV_AUTH_ENABLED=true (dev only).")
        return 1
    db = SessionLocal()
    created_users = skipped_users = 0
    created_customers = skipped_customers = 0
    created_catalogs = skipped_catalogs = 0
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
        for data in PRICES:
            exists = db.scalar(select(PriceList).where(PriceList.subsidiary_id == data["subsidiary_id"]))
            if exists is None:
                db.add(PriceList(**data))
                created_catalogs += 1
            else:
                skipped_catalogs += 1
        for data in DISTANCES:
            exists = db.scalar(select(Distance).where(Distance.province == data["province"]))
            if exists is None:
                db.add(Distance(**data))
                created_catalogs += 1
            else:
                skipped_catalogs += 1
        for data in BASIC_KITS:
            exists = db.scalar(select(BasicKit).where(BasicKit.model == data["model"]))
            if exists is None:
                db.add(BasicKit(**data))
                created_catalogs += 1
            else:
                skipped_catalogs += 1
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"users: {created_users} created, {skipped_users} skipped")
    print(f"customers: {created_customers} created, {skipped_customers} skipped")
    print(f"catalogs: {created_catalogs} created, {skipped_catalogs} skipped")
    print("Dev identities: dev-admin (admin), dev-es (sales/ES), dev-de (sales/DE), dev-viewer (viewer/ES)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
