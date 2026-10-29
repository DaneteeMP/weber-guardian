"""Dev-only seed for scope testing and catalog demos. Never run in production.

Creates demo users (admin + sales per subsidiary), subsidiary-tagged
customers and catalog rows (prices, distances, basic kits) with the demo
values the UI used to type by hand. Idempotent: existing rows are skipped.
Refuses to run unless DEV_AUTH_ENABLED=true.

Catalog line workloads are NOT seeded here: migration 0019 wrote the verified
legacy values into equipment_catalog, and the maintenance amount is workload
times the branch technician rate, so there is no demo figure left to invent.

Usage:
    DEV_AUTH_ENABLED=true python seed_dev.py
    docker compose run --rm -e DEV_AUTH_ENABLED=true api python seed_dev.py
"""
from decimal import Decimal

from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.modules.basic_kit.models import BasicKit
from app.modules.basic_kit.service import canonical_model
from app.modules.customers.models import Customer
from app.modules.distances.models import Distance
from app.modules.prices.models import PriceList
from app.modules.users.models import User

USERS = [
    {"external_id": "dev-admin", "email": "admin@local", "display_name": "Dev Admin", "role": "admin", "subsidiary_id": None},
    {"external_id": "dev-es", "email": "es@local", "display_name": "Dev Sales ES", "role": "sales", "subsidiary_id": "Weber Iberica"},
    {"external_id": "dev-de", "email": "de@local", "display_name": "Dev Sales DE", "role": "sales", "subsidiary_id": "Weber Germany"},
    {"external_id": "dev-viewer", "email": "viewer@local", "display_name": "Dev Viewer", "role": "viewer", "subsidiary_id": "Weber Iberica"},
]

CUSTOMERS = [
    {"customer_id": "0001012933", "account_name": "UAB Riela servisas", "country": "Lithuania", "subsidiary_id": "Weber Iberica"},
    {"customer_id": "0010027007", "account_name": "E. W. Grobbel St. Clair Shores", "country": "USA", "subsidiary_id": "Weber Germany"},
]

PRICES = [
    {"subsidiary_id": "Weber Iberica", "currency": "EUR", "km_rate": Decimal("0.5"), "tech_rate": Decimal("60"),
     "diet_full_rate": Decimal("40"), "diet_half_rate": Decimal("20"), "hotel_rate": Decimal("80"), "discount_rate": Decimal("0.15")},
    {"subsidiary_id": "Weber Germany", "currency": "EUR", "km_rate": Decimal("0.5"), "tech_rate": Decimal("60"),
     "diet_full_rate": Decimal("40"), "diet_half_rate": Decimal("20"), "hotel_rate": Decimal("80"), "discount_rate": Decimal("0.15"),
     "band1_rate_without": Decimal("120"), "band1_rate_with": Decimal("98"),
     "band2_rate_without": Decimal("210"), "band2_rate_with": Decimal("171.5"),
     "band3_rate_without": Decimal("270"), "band3_rate_with": Decimal("220.5")},
    {"subsidiary_id": "Weber Benelux", "currency": "EUR", "km_rate": Decimal("0.55"), "tech_rate": Decimal("65"),
     "diet_full_rate": Decimal("42"), "diet_half_rate": Decimal("21"), "hotel_rate": Decimal("90"), "discount_rate": Decimal("0.15")},
    {"subsidiary_id": "Weber France", "currency": "EUR", "km_rate": Decimal("0.6"), "tech_rate": Decimal("62"),
     "diet_full_rate": Decimal("38"), "diet_half_rate": Decimal("19"), "hotel_rate": Decimal("85"), "discount_rate": Decimal("0.15")},
    {"subsidiary_id": "Weber Italy", "currency": "EUR", "km_rate": Decimal("0.5"), "tech_rate": Decimal("58"),
     "diet_full_rate": Decimal("35"), "diet_half_rate": Decimal("18"), "hotel_rate": Decimal("78"), "discount_rate": Decimal("0.15")},
    {"subsidiary_id": "Weber Latina", "currency": "EUR", "km_rate": Decimal("0.45"), "tech_rate": Decimal("45"),
     "diet_full_rate": Decimal("30"), "diet_half_rate": Decimal("15"), "hotel_rate": Decimal("65"), "discount_rate": Decimal("0.15")},
]

DISTANCES = [
    {"subsidiary_id": "Weber Iberica", "province": "Madrid", "service_center": None, "km": Decimal("350"), "trip_hours": Decimal("4")},
    {"subsidiary_id": "Weber Iberica", "province": "Barcelona", "service_center": None, "km": Decimal("120"), "trip_hours": Decimal("1.5")},
]

# Basic kits in the same "Model  SpareParts  WorkloadBasicKit" shape of the
# WeberAssistant reference table. Offered as (model, spare_parts, kit hours).
#
# The reference spells machine configurations as "Model Suffix" (e.g. "304
# CCS"); equipment rows store the compact machine_type, suffix first ("CCS304"
# = "CCS" + "304", matching the equipment_catalog candidates of migration
# 0013). The keys are canonicalized with the same rule the basic-kit service
# applies on writes, so the seed and the admin UI agree. The duplicate "304
# UB" row of the reference is collapsed.
BASIC_KIT_SOURCE = [
    ("304 UB", Decimal("410"), Decimal("8")),
    ("304 CCL", Decimal("475"), Decimal("8")),
    ("304 CCS", Decimal("475"), Decimal("8")),
    ("304 MLC", Decimal("615"), Decimal("12")),
    ("305 CCL", Decimal("475"), Decimal("8")),
    ("305 MLC", Decimal("615"), Decimal("12")),
    ("305 SLC", Decimal("615"), Decimal("12")),
    ("305 UB", Decimal("410"), Decimal("8")),
    ("402 CCL", Decimal("475"), Decimal("8")),
    ("402 CCS", Decimal("475"), Decimal("8")),
    ("402 MLC", Decimal("615"), Decimal("12")),
    ("402 SLC", Decimal("615"), Decimal("12")),
    ("402 UB", Decimal("410"), Decimal("8")),
    ("404 CCL", Decimal("475"), Decimal("8")),
    ("404 MCS", Decimal("785"), Decimal("16")),
    ("404 MLC", Decimal("615"), Decimal("12")),
    ("404 SLC", Decimal("615"), Decimal("12")),
    ("405 MCS", Decimal("785"), Decimal("16")),
    ("405 MLC", Decimal("615"), Decimal("12")),
    ("405 SLC", Decimal("615"), Decimal("12")),
    ("5000 UB", Decimal("445"), Decimal("8")),
    ("501 SLC", Decimal("615"), Decimal("12")),
    ("602 CCL", Decimal("475"), Decimal("8")),
    ("602 MCS", Decimal("785"), Decimal("16")),
    ("602 MLC", Decimal("615"), Decimal("12")),
    ("602 SLC", Decimal("615"), Decimal("12")),
    ("602 UB", Decimal("410"), Decimal("8")),
    ("604 MCS", Decimal("785"), Decimal("16")),
    ("604 SLC", Decimal("615"), Decimal("12")),
    ("7000 CCB", Decimal("475"), Decimal("8")),
    ("7000 UB", Decimal("410"), Decimal("8")),
    ("802 CCL", Decimal("475"), Decimal("8")),
    ("804 MCS", Decimal("960"), Decimal("24")),
    ("804 SLC", Decimal("615"), Decimal("12")),
    ("9000 SLC", Decimal("615"), Decimal("12")),
    ("901 MCS", Decimal("615"), Decimal("12")),
    ("901 SLC", Decimal("615"), Decimal("12")),
    ("902 CCL", Decimal("615"), Decimal("12")),
    ("902 CCS", Decimal("615"), Decimal("12")),
    ("902 MCS", Decimal("785"), Decimal("16")),
    ("902 SLC", Decimal("615"), Decimal("12")),
    ("902 UB", Decimal("410"), Decimal("8")),
    ("903 MCS", Decimal("785"), Decimal("16")),
    ("904 MCS", Decimal("785"), Decimal("16")),
    ("904 RCS", Decimal("785"), Decimal("16")),
    ("904 SLC", Decimal("615"), Decimal("12")),
    ("905 MCS", Decimal("785"), Decimal("16")),
    ("905 RCS", Decimal("785"), Decimal("16")),
    ("906 SLC", Decimal("615"), Decimal("12")),
    ("KSG", Decimal("265"), Decimal("3")),
    ("KSG 470", Decimal("265"), Decimal("3")),
    ("SHA", Decimal("420"), Decimal("6")),
    ("SSG", Decimal("265"), Decimal("3")),
    ("SSM", Decimal("265"), Decimal("3")),
    ("TLN06001 MCS", Decimal("1295"), Decimal("16")),
    ("WLN03051 CCL", Decimal("475"), Decimal("8")),
    ("WLN03051 MLC", Decimal("615"), Decimal("12")),
    ("WLN03051 SLC", Decimal("615"), Decimal("12")),
    ("WLN03051 UB", Decimal("410"), Decimal("8")),
    ("WLN04041 SLC", Decimal("615"), Decimal("12")),
    ("WLN04051 CCL", Decimal("615"), Decimal("8")),
    ("WLN04051 CCS", Decimal("615"), Decimal("8")),
    ("WLN04051 MLC", Decimal("950"), Decimal("12")),
    ("WLN04051 SLC", Decimal("950"), Decimal("12")),
    ("WLN04051 UB", Decimal("410"), Decimal("8")),
    ("WLN04052 MLC", Decimal("950"), Decimal("12")),
    ("WLN04052 UB", Decimal("410"), Decimal("8")),
    ("WLN06001 MCS", Decimal("1295"), Decimal("16")),
    ("WLN06001 RCS", Decimal("1295"), Decimal("16")),
    ("WLN06002 RCS", Decimal("1295"), Decimal("16")),
    ("WLN06021 MCS", Decimal("1295"), Decimal("16")),
    ("WLN06041 RCS", Decimal("1295"), Decimal("16")),
    ("WLN06042 MCS", Decimal("1295"), Decimal("16")),
    ("WLN06042 MLC", Decimal("1295"), Decimal("12")),
    ("WLN06042 RCS", Decimal("1295"), Decimal("16")),
    ("WLN06042 SLC", Decimal("1295"), Decimal("12")),
    ("WLN07021 CCS", Decimal("1295"), Decimal("12")),
    ("WLN08041 CCL", Decimal("950"), Decimal("12")),
    ("WLN08041 MCS", Decimal("1295"), Decimal("16")),
    ("WLN08041 RCS", Decimal("1295"), Decimal("16")),
    ("WLN08041 SLC", Decimal("950"), Decimal("12")),
    ("WLN09041 MCS", Decimal("1295"), Decimal("16")),
    ("WLN09042 MCS", Decimal("950"), Decimal("16")),
    ("WLN09042 RCS", Decimal("1295"), Decimal("16")),
    ("WLN09051 MCS", Decimal("1295"), Decimal("16")),
    ("WLN09051 RCS", Decimal("1295"), Decimal("16")),
    ("WLN09051 SLC", Decimal("950"), Decimal("12")),
    ("WLN09061", Decimal("950"), Decimal("16")),
    ("WLN09061 MCS", Decimal("1295"), Decimal("16")),
    ("WLN09061 WSS", Decimal("1295"), Decimal("16")),
    ("WLN10001", Decimal("475"), Decimal("8")),
    ("WLN10001 VPM", Decimal("785"), Decimal("16")),
    ("WLN10002 UB", Decimal("410"), Decimal("8")),
    ("WLN40001", Decimal("615"), Decimal("12")),
    ("WLN40001 MLC", Decimal("950"), Decimal("12")),
    ("WLN40001 RCS", Decimal("950"), Decimal("16")),
    ("WLN40001 SLC", Decimal("950"), Decimal("12")),
    ("WLN45001 MCS", Decimal("950"), Decimal("16")),
    ("WLN50001 UB", Decimal("615"), Decimal("8")),
    ("WSS", Decimal("785"), Decimal("16")),
    ("Thera 450-650", Decimal("615"), Decimal("12")),
    ("WLN75001 MCS", Decimal("1295"), Decimal("16")),
    ("302 UB", Decimal("410"), Decimal("8")),
]

BASIC_KITS = [
    {
        "model": canonical_model(model),
        "spare_parts": spare_parts,
        "workload_basic_kit": workload,
    }
    for model, spare_parts, workload in BASIC_KIT_SOURCE
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
            exists = db.scalar(
                select(Distance).where(
                    Distance.subsidiary_id == data["subsidiary_id"],
                    Distance.province == data["province"],
                )
            )
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
