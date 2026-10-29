"""Seed a demo-only subsidiary and its test catalogue.

Creates "Test Mode (Germany)" with its own customers, sites, equipment,
distances, responsibles, rates (copied from Weber Germany) and demo offers.
Nothing real is modified: every row hangs from the test subsidiary or uses
TESTDE-/TST identifiers. Idempotent, so it can be re-run safely.

The price row is written with raw SQL because production may still be on
migration 0030, where the band columns do not exist yet; when they do exist
they are copied too.

Usage (inside the api container):
    SEED_DATABASE_URL=postgresql+psycopg://... python seed_test_subsidiary.py --confirm
"""
from __future__ import annotations

import argparse
import os
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.distances.models import Distance
from app.modules.equipment.models import CustomerSite, Equipment, row_hash_of, site_hash_of
from app.modules.offers.models import Offer
from app.modules.offers.schemas import OfferCalculateIn, OfferCreate, OfferItemCreate
from app.modules.offers.service import create_offer
from app.modules.responsibles.models import Responsible
from app.modules.subsidiaries.models import Subsidiary
from app.modules.users.models import User  # noqa: F401  (registers the FK target)

TEST_SUBSIDIARY = "Test Mode (Germany)"
TEST_SHORT_LABEL = "Test DE"
CUSTOMER_PREFIX = "TESTDE-"
OFFER_PREFIX = "G-02-2026-DEMO"
MARKER = "TEST DATA - seeded demo subsidiary"

# status, offer_date, work_hours, km, items, offer_type, guardian_selections
SPECS = [
    ("Pending response", date(2026, 10, 27), Decimal("6"), Decimal("120"), 2, "audit", ["maintenance_inspection", "inspection", "machine_checklist"]),
    ("Pending response", date(2026, 10, 20), Decimal("8"), Decimal("200"), 3, "guardian", ["service_support", "standard_hotline", "remote_support"]),
    ("Pending response", date(2026, 9, 18), Decimal("4"), Decimal("80"), 1, "off_guardian", ["parts_availability", "parts_discount"]),
    ("Pending response", date(2026, 9, 5), Decimal("10"), Decimal("260"), 3, "audit", ["training_optimization", "operator_training"]),
    ("Accepted", date(2026, 8, 14), Decimal("8"), Decimal("150"), 2, "guardian", ["digital_services", "factory_cockpit"]),
    ("Accepted", date(2026, 7, 22), Decimal("6"), Decimal("90"), 1, "audit", ["maintenance_inspection", "preventive_maintenance"]),
    ("Pending Service", date(2026, 8, 2), Decimal("12"), Decimal("320"), 3, "guardian", ["blade_solutions", "stock_agreement"]),
    ("Pending Service", date(2026, 6, 11), Decimal("5"), Decimal("70"), 1, "audit", ["service_support", "priority_response"]),
    ("In progress", date(2026, 10, 3), Decimal("14"), Decimal("180"), 3, "audit", ["maintenance_inspection", "inspection_report"]),
    ("In progress", date(2026, 5, 19), Decimal("7"), Decimal("110"), 2, "off_guardian", ["parts_availability", "priority_handling"]),
    ("Pending invoicing", date(2026, 9, 28), Decimal("9"), Decimal("140"), 2, "guardian", ["training_optimization", "line_optimization"]),
    ("Pending invoicing", date(2026, 4, 16), Decimal("6"), Decimal("60"), 1, "audit", ["maintenance_inspection", "maintenance_kit"]),
    ("Finished", date(2026, 3, 25), Decimal("8"), Decimal("160"), 2, "guardian", ["digital_services", "performance_review"]),
    ("Finished", date(2026, 2, 10), Decimal("5"), Decimal("75"), 1, "audit", ["service_support", "standard_hotline"]),
    ("Finished", date(2026, 1, 15), Decimal("12"), Decimal("300"), 3, "guardian", ["blade_solutions", "sharpening_assessment"]),
    ("Cancelled", date(2026, 7, 8), Decimal("4"), Decimal("50"), 1, "audit", []),
]


def _database_url() -> str:
    url = os.environ.get("SEED_DATABASE_URL") or os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("Set SEED_DATABASE_URL (or DATABASE_URL) to the target database.")
    # The container ships psycopg 3, not psycopg2.
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def _ensure_subsidiary(db: Session) -> None:
    if db.get(Subsidiary, TEST_SUBSIDIARY) is None:
        db.add(Subsidiary(name=TEST_SUBSIDIARY, short_label=TEST_SHORT_LABEL))
        db.flush()


def _ensure_prices(db: Session) -> None:
    exists = db.execute(
        text("select 1 from prices where subsidiary_id = :s"), {"s": TEST_SUBSIDIARY}
    ).first()
    if exists:
        return

    germany = db.execute(
        text(
            "select currency, km_rate, tech_rate, diet_full_rate, diet_half_rate, "
            "hotel_rate, discount_rate from prices where subsidiary_id = 'Weber Germany'"
        )
    ).mappings().first()
    values = {
        "id": str(uuid.uuid4()),
        "subsidiary_id": TEST_SUBSIDIARY,
        "currency": (germany or {}).get("currency", "EUR"),
        "km_rate": (germany or {}).get("km_rate", Decimal("0.5")),
        "tech_rate": (germany or {}).get("tech_rate", Decimal("60")),
        "diet_full_rate": (germany or {}).get("diet_full_rate", Decimal("40")),
        "diet_half_rate": (germany or {}).get("diet_half_rate", Decimal("20")),
        "hotel_rate": (germany or {}).get("hotel_rate", Decimal("80")),
        "discount_rate": (germany or {}).get("discount_rate", Decimal("0.15")),
    }
    columns = ["id", "subsidiary_id", "currency", "km_rate", "tech_rate", "diet_full_rate", "diet_half_rate", "hotel_rate", "discount_rate"]
    available = set(
        db.execute(
            text(
                "select column_name from information_schema.columns "
                "where table_name = 'prices'"
            )
        ).scalars()
    )
    bands = [
        "band1_rate_without",
        "band1_rate_with",
        "band2_rate_without",
        "band2_rate_with",
        "band3_rate_without",
        "band3_rate_with",
    ]
    if all(name in available for name in bands):
        for name in bands:
            values[name] = (germany or {}).get(name)
            columns.append(name)

    placeholders = ", ".join(f":{name}" for name in columns)
    db.execute(
        text(f"insert into prices ({', '.join(columns)}) values ({placeholders})"),
        values,
    )


def _ensure_responsibles(db: Session) -> None:
    for name in ("Test Admin", "Test Sales"):
        exists = db.scalar(
            select(Responsible).where(
                Responsible.subsidiary_id == TEST_SUBSIDIARY,
                Responsible.name == name,
            )
        )
        if exists is None:
            db.add(Responsible(subsidiary_id=TEST_SUBSIDIARY, name=name, active=True))


def _templates(db: Session) -> list[tuple[Customer, list[Equipment]]]:
    """Real German customers/equipment used to give the demo realistic machines."""
    result: list[tuple[Customer, list[Equipment]]] = []
    german = db.scalars(
        select(Customer)
        .where(Customer.subsidiary_id == "Weber Germany")
        .order_by(Customer.customer_id)
        .limit(100)
    )
    for customer in german:
        rows = list(
            db.scalars(
                select(Equipment)
                .where(Equipment.customer_id == customer.customer_id)
                .order_by(Equipment.equipment_name)
                .limit(3)
            )
        )
        if rows:
            result.append((customer, rows))
        if len(result) >= 10:
            break
    return result


def _ensure_customer(
    db: Session, index: int, template: Customer, equipment: list[Equipment]
) -> Customer:
    customer_id = f"{CUSTOMER_PREFIX}{index:04d}"
    customer = db.scalar(select(Customer).where(Customer.customer_id == customer_id))
    if customer is None:
        customer = Customer(
            customer_id=customer_id,
            account_name=f"Test Kunde {index:02d} - {template.account_name}"[:255],
            city="Teststadt",
            province="Test Province",
            country="Germany",
            subsidiary_id=TEST_SUBSIDIARY,
        )
        db.add(customer)
        db.flush()

    street = f"Teststrasse {index:02d}"
    postal = f"000{index:02d}"
    site_hash = site_hash_of(customer_id, street, "Teststadt", postal, "Test Province", "Germany")
    assert site_hash is not None
    site = db.scalar(select(CustomerSite).where(CustomerSite.site_hash == site_hash))
    if site is None:
        site = CustomerSite(
            customer_id=customer_id,
            site_hash=site_hash,
            physical_street=street,
            physical_city="Teststadt",
            physical_postal_code=postal,
            physical_province="Test Province",
            physical_country="Germany",
        )
        db.add(site)
        db.flush()

    copied: set[str] = set()
    for source in equipment:
        name = source.equipment_name or f"TEST-EQ-{index:02d}"
        if name in copied:
            continue
        copied.add(name)
        row_hash = row_hash_of(
            customer_id,
            name,
            source.machine_type,
            source.component_type,
            source.material_no,
            source.purchase_date,
            site_hash,
        )
        if db.scalar(select(Equipment).where(Equipment.row_hash == row_hash)) is None:
            db.add(
                Equipment(
                    customer_id=customer_id,
                    equipment_name=name,
                    machine_type=source.machine_type,
                    component_type=source.component_type,
                    material_no=source.material_no,
                    purchase_date=source.purchase_date,
                    site_id=site.id,
                    row_hash=row_hash,
                )
            )
        if len(copied) >= 3:
            break

    # Some customers have no equipment: give the demo at least three lines.
    while len(copied) < 3:
        name = f"TEST-EQ-{index:02d}-{len(copied) + 1}"
        copied.add(name)
        row_hash = row_hash_of(customer_id, name, "CCL 404", "Slicer", None, None, site_hash)
        if db.scalar(select(Equipment).where(Equipment.row_hash == row_hash)) is None:
            db.add(
                Equipment(
                    customer_id=customer_id,
                    equipment_name=name,
                    machine_type="CCL 404",
                    component_type="Slicer",
                    material_no=None,
                    purchase_date=None,
                    site_id=site.id,
                    row_hash=row_hash,
                )
            )
    db.flush()
    return customer


def _ensure_distance(db: Session, index: int, customer: Customer) -> None:
    exists = db.scalar(
        select(Distance).where(
            Distance.subsidiary_id == TEST_SUBSIDIARY,
            Distance.province == customer.customer_id,
        )
    )
    if exists is not None:
        return
    db.add(
        Distance(
            subsidiary_id=TEST_SUBSIDIARY,
            province=customer.customer_id,
            region="Germany",
            reference_city="Teststadt",
            service_center="Werther",
            origin_city="Werther",
            km=Decimal("100") + Decimal(index * 15),
            driving_hours=Decimal("1.50"),
            trip_hours=Decimal("2.00"),
            itinerary="Test route",
            route_data_date=date(2026, 10, 1),
        )
    )


def _ensure_offers(db: Session, customers: list[Customer]) -> int:
    created = 0
    for index, spec in enumerate(SPECS, start=1):
        status, offer_date, work_hours, km, item_count, offer_type, selections = spec
        number = f"{OFFER_PREFIX}{index:03d}"
        if db.scalar(select(Offer).where(Offer.id_guardian_offer == number)) is not None:
            continue

        customer = customers[(index - 1) % len(customers)]
        names = list(
            dict.fromkeys(
                name
                for name in db.scalars(
                    select(Equipment.equipment_name)
                    .where(Equipment.customer_id == customer.customer_id)
                    .limit(6)
                )
                if name
            )
        )
        if not names:
            names = [f"TEST-EQ-{index:02d}-{n}" for n in range(1, item_count + 1)]
        chosen = names[:item_count]

        items = [
            OfferItemCreate(
                equipment=name,
                description=f"Test machine line {pos}",
                import_amount=Decimal("250.00") + Decimal(pos * 75),
                workload=Decimal("2.0") + Decimal(pos),
            )
            for pos, name in enumerate(chosen, start=1)
        ]
        pricing = OfferCalculateIn(
            work_hours=work_hours,
            trip_hours_base=Decimal("2"),
            km=km,
            km_rate=Decimal("0.5"),
            tech_rate=Decimal("60"),
            diet_full_rate=Decimal("40"),
            diet_half_rate=Decimal("20"),
            hotel_rate=Decimal("80"),
            discount_rate=Decimal("0.15"),
            currency="EUR",
            offer_type=offer_type,
            equipment_count=len({item.equipment for item in items if item.equipment}),
        )
        create_offer(
            db,
            OfferCreate(
                customer_id=customer.customer_id,
                id_guardian_offer=number,
                status=status,
                responsible_person="Test Admin",
                language="German",
                inspection_frequency="Annual",
                general_comments=MARKER,
                offer_date=offer_date,
                guardian_selections=selections,
                pricing=pricing,
                items=items,
            ),
            scope_subsidiary=TEST_SUBSIDIARY,
        )
        created += 1
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm", action="store_true", help="allow writes to the target database")
    args = parser.parse_args()
    if not args.confirm:
        raise SystemExit("Refusing to write. Re-run with --confirm.")

    url = _database_url()
    print(f"Target: {make_url(url).render_as_string(hide_password=True)}")
    engine = create_engine(url)
    try:
        with Session(engine) as db:
            _ensure_subsidiary(db)
            _ensure_prices(db)
            _ensure_responsibles(db)
            templates = _templates(db)
            if not templates:
                raise SystemExit("No German equipment templates found; run seed_dev.py/import first.")
            customers = [
                _ensure_customer(db, index, customer, equipment)
                for index, (customer, equipment) in enumerate(
                    (templates[i % len(templates)] for i in range(10)), start=1
                )
            ]
            for index, customer in enumerate(customers, start=1):
                _ensure_distance(db, index, customer)
            db.commit()

            created = _ensure_offers(db, customers)
            print(
                f"{TEST_SUBSIDIARY}: {len(customers)} test customers, "
                f"{created} offers created, {len(SPECS) - created} already present."
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
