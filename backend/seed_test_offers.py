"""Seed German test offers for the Offers dashboard (local/test only).

Idempotent: every generated offer uses a fixed G-02-2026-TSTxxx number and is
skipped when it already exists. The rows are real offers created through the
normal service, so pricing, totals, status and dates go through the same path
as the UI.

Usage (inside the api container):
    docker compose exec -T api python - < seed_test_offers.py
"""
from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.db import SessionLocal
from app.modules.customers.models import Customer
from app.modules.equipment.models import Equipment
from app.modules.offers.models import Offer
from app.modules.users.models import User  # noqa: F401  (registers the FK target)
from app.modules.offers.schemas import OfferCalculateIn, OfferCreate, OfferItemCreate
from app.modules.offers.service import create_offer

SUBSIDIARY = "Weber Germany"
MARKER = "TEST DATA - seeded offer"

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


def main() -> None:
    with SessionLocal() as db:
        customers = list(
            db.scalars(
                select(Customer)
                .where(Customer.subsidiary_id == SUBSIDIARY)
                .order_by(Customer.customer_id)
                .limit(10)
            )
        )
        if not customers:
            raise SystemExit(f"No customers for {SUBSIDIARY}; run seed_dev.py first.")

        created = 0
        skipped = 0
        for index, spec in enumerate(SPECS, start=1):
            status, offer_date, work_hours, km, item_count, offer_type, selections = spec
            number = f"G-02-2026-TST{index:03d}"
            if db.scalar(select(Offer).where(Offer.id_guardian_offer == number)) is not None:
                skipped += 1
                continue

            customer = customers[(index - 1) % len(customers)]
            equipment_names = list(
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
            if not equipment_names:
                equipment_names = [f"TEST-{index:02d}-{n}" for n in range(1, item_count + 1)]
            chosen = equipment_names[:item_count]

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
            )
            created += 1

        print(f"German test offers: {created} created, {skipped} already present.")


if __name__ == "__main__":
    main()
