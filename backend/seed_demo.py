"""Demo seed for the public MVP database. All data here is invented.

Why it exists: the public demo runs on an empty database, so the dashboard
charts would show nothing. This script creates a handful of fictional customers
spread over several subsidiaries plus offers spread over the last months, so
the status donut, the monthly bars and the ranking have something to draw.

Safety: it refuses to run when the offers table is not empty. The development
database holds real Weber data, and this script must never touch it. There is
no "clean up" mode on purpose: a demo database is cheap to drop and recreate.

Usage (against the demo database only):
    python seed_demo.py
    docker compose run --rm -e DATABASE_URL=postgres://... api python seed_demo.py
"""
import hashlib
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func, select

from app.core.db import SessionLocal
from app.modules.customers.models import Customer
from app.modules.equipment.models import Equipment
from app.modules.offers.models import Offer, OfferItem
from app.modules.users.models import User

# Fictional customers. customer_id follows the SAP Debitor shape (10 digits)
# so the column widths and the offer URLs behave like the real thing.
CUSTOMERS = [
    {"customer_id": "0099000001", "account_name": "Demo Construcciones del Norte SL", "city": "Pamplona", "province": "Navarra", "country": "Spain", "subsidiary_id": "Weber Iberica"},
    {"customer_id": "0099000002", "account_name": "Demo Molins de Quarry SA", "city": "Barcelona", "province": "Barcelona", "country": "Spain", "subsidiary_id": "Weber Iberica"},
    {"customer_id": "0099000003", "account_name": "Demo Rheinwerk GmbH", "city": "Duisburg", "province": "Nordrhein-Westfalen", "country": "Germany", "subsidiary_id": "Weber Germany"},
    {"customer_id": "0099000004", "account_name": "Demo Maas Beton BV", "city": "Maastricht", "province": "Limburg", "country": "Netherlands", "subsidiary_id": "Weber Benelux"},
    {"customer_id": "0099000005", "account_name": "Demo PAYSAGE SAS", "city": "Lyon", "province": "Rhone", "country": "France", "subsidiary_id": "Weber France"},
    {"customer_id": "0099000006", "account_name": "Demo Adriatica Costruzioni SpA", "city": "Bologna", "province": "Emilia-Romagna", "country": "Italy", "subsidiary_id": "Weber Italy"},
    {"customer_id": "0099000007", "account_name": "Demo Cerramientos Norte SA", "city": "Buenos Aires", "province": "Buenos Aires", "country": "Argentina", "subsidiary_id": "Weber Latina"},
    {"customer_id": "0099000008", "account_name": "Demo Zuid Aggregate BV", "city": "Antwerpen", "province": "Antwerpen", "country": "Belgium", "subsidiary_id": "Weber Benelux"},
]

# One or two machines per customer. row_hash is the import fingerprint, so it
# is derived from the same values a CSV import would hash.
EQUIPMENT = [
    {"customer_id": "0099000001", "equipment_name": "CBS 4000", "machine_type": "Concrete pump", "material_no": "DEMO-1001"},
    {"customer_id": "0099000001", "equipment_name": "SP 66", "machine_type": "Concrete pump", "material_no": "DEMO-1002"},
    {"customer_id": "0099000002", "equipment_name": "CCS 309", "machine_type": "Concrete pump", "material_no": "DEMO-1003"},
    {"customer_id": "0099000003", "equipment_name": "SP 88", "machine_type": "Concrete pump", "material_no": "DEMO-1004"},
    {"customer_id": "0099000004", "equipment_name": "P 909", "machine_type": "Paver", "material_no": "DEMO-1005"},
    {"customer_id": "0099000005", "equipment_name": "MT 62", "machine_type": "Truck-mounted line", "material_no": "DEMO-1006"},
    {"customer_id": "0099000006", "equipment_name": "SP 45", "machine_type": "Concrete pump", "material_no": "DEMO-1007"},
    {"customer_id": "0099000007", "equipment_name": "CBS 5000", "machine_type": "Concrete pump", "material_no": "DEMO-1008"},
    {"customer_id": "0099000008", "equipment_name": "TF 3000", "machine_type": "Truck-mounted line", "material_no": "DEMO-1009"},
]

# (customer_id, days_ago, status, hours, net_total, responsible)
# Statuses are mixed on purpose so the donut has three slices: 8 Draft,
# 9 Finished, 7 Pending response. Days spread over roughly five and a half
# months so the monthly chart has more than one bar per month.
OFFER_PLAN = [
    ("0099000001", 3, "Draft", Decimal("4.0"), Decimal("680.00"), "Demo Sales ES"),
    ("0099000001", 41, "Finished", Decimal("6.5"), Decimal("1240.00"), "Demo Sales ES"),
    ("0099000001", 96, "Finished", Decimal("3.0"), Decimal("520.00"), "Demo Sales ES"),
    ("0099000002", 9, "Pending response", Decimal("5.0"), Decimal("910.00"), "Demo Sales ES"),
    ("0099000002", 58, "Finished", Decimal("7.5"), Decimal("1480.00"), "Demo Sales ES"),
    ("0099000003", 16, "Draft", Decimal("8.0"), Decimal("1720.00"), "Demo Sales DE"),
    ("0099000003", 74, "Finished", Decimal("4.0"), Decimal("860.00"), "Demo Sales DE"),
    ("0099000004", 23, "Pending response", Decimal("6.0"), Decimal("1180.00"), "Demo Sales NL"),
    ("0099000004", 101, "Finished", Decimal("2.5"), Decimal("430.00"), "Demo Sales NL"),
    ("0099000005", 31, "Draft", Decimal("9.0"), Decimal("2050.00"), "Demo Sales FR"),
    ("0099000005", 88, "Pending response", Decimal("5.5"), Decimal("1040.00"), "Demo Sales FR"),
    ("0099000006", 37, "Finished", Decimal("4.5"), Decimal("870.00"), "Demo Sales IT"),
    ("0099000006", 112, "Draft", Decimal("3.5"), Decimal("610.00"), "Demo Sales IT"),
    ("0099000007", 44, "Pending response", Decimal("7.0"), Decimal("1310.00"), "Demo Sales LATAM"),
    ("0099000007", 119, "Finished", Decimal("5.0"), Decimal("940.00"), "Demo Sales LATAM"),
    ("0099000008", 52, "Draft", Decimal("6.0"), Decimal("1120.00"), "Demo Sales NL"),
    ("0099000008", 126, "Pending response", Decimal("4.0"), Decimal("780.00"), "Demo Sales NL"),
    ("0099000002", 66, "Draft", Decimal("5.0"), Decimal("990.00"), "Demo Sales ES"),
    ("0099000003", 133, "Pending response", Decimal("3.0"), Decimal("540.00"), "Demo Sales DE"),
    ("0099000004", 140, "Finished", Decimal("6.5"), Decimal("1250.00"), "Demo Sales NL"),
    ("0099000001", 147, "Draft", Decimal("4.5"), Decimal("820.00"), "Demo Sales ES"),
    ("0099000005", 154, "Pending response", Decimal("8.0"), Decimal("1560.00"), "Demo Sales FR"),
    ("0099000006", 161, "Finished", Decimal("5.5"), Decimal("1010.00"), "Demo Sales IT"),
    ("0099000008", 168, "Draft", Decimal("7.5"), Decimal("1390.00"), "Demo Sales NL"),
]

# Gross is the net plus a fixed 21% discount, so total and total_end differ the
# way the pricing engine leaves them.
DISCOUNT_RATE = Decimal("0.21")


def equipment_hash(data: dict) -> str:
    return hashlib.sha256("|".join(str(data[k]) for k in sorted(data)).encode()).hexdigest()


def main() -> int:
    db = SessionLocal()
    try:
        existing = db.scalar(select(func.count()).select_from(Offer)) or 0
        if existing:
            # This is the whole point of the guard: never mix invented demo
            # rows into a database that already holds real offers.
            print(f"Refusing to seed: {existing} offers already exist (not an empty demo database).")
            return 1

        author = db.scalar(select(User).where(User.role == "admin"))
        if author is None:
            # Offers.created_by is nullable, but an empty user table means the
            # demo login cannot pick an identity, so fail loudly instead.
            print("Refusing to seed: no users exist. Run seed_dev.py first.")
            return 1

        for data in CUSTOMERS:
            if db.scalar(select(Customer).where(Customer.customer_id == data["customer_id"])) is None:
                db.add(Customer(**data))
        for data in EQUIPMENT:
            row = {**data, "row_hash": equipment_hash(data)}
            if db.scalar(select(Equipment).where(Equipment.row_hash == row["row_hash"])) is None:
                db.add(Equipment(**row))

        today = date.today()
        for index, (customer_id, days_ago, status, hours, net_total, responsible) in enumerate(OFFER_PLAN, start=1):
            gross = (net_total / (Decimal("1") - DISCOUNT_RATE)).quantize(Decimal("0.01"))
            offer = Offer(
                id_guardian_offer=f"DEMO-{today.year}-{index:04d}",
                customer_id=customer_id,
                status=status,
                responsible_person=responsible,
                language="es",
                currency="EUR",
                work_hours=hours,
                total_hours=hours,
                discount=(gross - net_total).quantize(Decimal("0.01")),
                total=gross,
                total_end=net_total,
                offer_date=today - timedelta(days=days_ago),
                created_by=author.id,
                general_comments="Oferta de demostración con datos inventados.",
            )
            offer.items.append(
                OfferItem(
                    row_no=1,
                    equipment=next(
                        (e["equipment_name"] for e in EQUIPMENT if e["customer_id"] == customer_id), None
                    ),
                    description="Revisión general y presupuesto de repuestos",
                    import_amount=gross,
                    workload=hours,
                )
            )
            db.add(offer)
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
    print(f"customers: {len(CUSTOMERS)}")
    print(f"equipment: {len(EQUIPMENT)}")
    print(f"offers: {len(OFFER_PLAN)} across {len({p[0] for p in OFFER_PLAN})} customers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
