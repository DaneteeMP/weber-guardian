"""Offer service tests (F1). SQLite in-memory, no API."""
from decimal import Decimal

import pytest

from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import create_customer
from app.modules.offers.schemas import OfferCalculateIn, OfferCreate, OfferItemCreate
from app.modules.offers.service import (
    OfferAlreadyExists,
    UnknownCustomer,
    calculate_price,
    create_offer,
    list_offers,
)


def _customer(db, cid="0001012933"):
    return create_customer(db, CustomerCreate(customer_id=cid, account_name="UAB Riela servisas", country="Lithuania"))


def _pricing(**overrides):
    params = {
        "work_hours": Decimal("10"),
        "report_hours": Decimal("2"),
        "trip_hours_base": Decimal("3"),
        "km": Decimal("50"),
        "km_rate": Decimal("0.5"),
        "tech_rate": Decimal("60"),
        "diet_full_rate": Decimal("40"),
        "diet_half_rate": Decimal("20"),
        "hotel_rate": Decimal("80"),
    }
    params.update(overrides)
    return OfferCalculateIn(**params)


def _offer_data(cid="0001012933", number="W-02-2026-0001"):
    return OfferCreate(
        customer_id=cid,
        id_guardian_offer=number,
        pricing=_pricing(),
        items=[
            OfferItemCreate(equipment="304-565", description="Slicer", import_amount=Decimal("100.00"), workload=Decimal("6")),
            OfferItemCreate(equipment="304-565", description="Checkweigher", import_amount=Decimal("50.00"), workload=Decimal("4")),
        ],
    )


def test_calculate_is_dry_run_with_fixed_totals():
    out = calculate_price(_pricing())
    assert out.total == Decimal("1050.00")
    assert out.total_end == Decimal("906.00")


def test_create_offer_persists_header_and_items_with_server_totals(db):
    _customer(db)
    offer = create_offer(db, _offer_data())
    assert offer.id_guardian_offer == "W-02-2026-0001"
    assert offer.total == Decimal("1050.00")
    assert offer.total_end == Decimal("906.00")
    assert len(offer.items) == 2
    assert [i.row_no for i in offer.items] == [1, 2]


def test_create_offer_unknown_customer_raises_404_domain(db):
    with pytest.raises(UnknownCustomer):
        create_offer(db, _offer_data(cid="NOPE"))


def test_duplicate_number_raises_409_and_leaves_no_orphans(db):
    from sqlalchemy import func, select

    from app.modules.offers.models import Offer, OfferItem

    _customer(db)
    create_offer(db, _offer_data(number="W-02-2026-0001"))
    with pytest.raises(OfferAlreadyExists):
        create_offer(db, _offer_data(number="W-02-2026-0001"))
    assert db.scalar(select(func.count()).select_from(Offer)) == 1
    assert db.scalar(select(func.count()).select_from(OfferItem)) == 2


def test_list_offers_filters_by_customer(db):
    _customer(db, "0001012933")
    _customer(db, "0001052941")
    create_offer(db, _offer_data(cid="0001012933", number="W-02-2026-0001"))
    create_offer(db, _offer_data(cid="0001052941", number="W-02-2026-0002"))
    assert len(list_offers(db)) == 2
    only = list_offers(db, customer_id="0001012933")
    assert len(only) == 1
    assert only[0].customer_id == "0001012933"
