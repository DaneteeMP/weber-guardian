"""Catalog tests: seeded reads, unknown keys, prices scope. SQLite only."""
from decimal import Decimal

import pytest

from app.modules.basic_kit.models import BasicKit
from app.modules.basic_kit.schemas import BasicKitCreate, BasicKitUpsert
from app.modules.basic_kit.service import delete_kit, get_kit, KitAlreadyExists, create_kit, list_kits, upsert_kit
from app.modules.distances.models import Distance
from app.modules.distances.schemas import DistanceUpdate
from app.modules.distances.service import (
    GERMAN_SERVICE_CENTERS,
    InvalidServiceCenter,
    UnknownSubsidiary,
    delete_distance,
    get_distance,
    list_distances,
    upsert_distance,
)
from app.modules.prices.models import PriceList
from app.modules.prices.schemas import PriceUpdate
from app.modules.prices.service import get_prices, update_prices
from app.modules.subsidiaries.models import Subsidiary


def _seed(db):
    db.add_all(
        [
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
            Subsidiary(name="Weber Germany", short_label="Germany"),
            Subsidiary(name="Weber Italy", short_label="Italy"),
        ]
    )
    db.add(
        PriceList(
            subsidiary_id="Weber Iberica",
            km_rate=Decimal("0.5"),
            tech_rate=Decimal("60"),
            diet_full_rate=Decimal("40"),
            diet_half_rate=Decimal("20"),
            hotel_rate=Decimal("80"),
        )
    )
    db.add(
        Distance(
            subsidiary_id="Weber Iberica",
            province="Madrid",
            km=Decimal("350"),
            trip_hours=Decimal("4"),
        )
    )
    db.add(BasicKit(model="CCS304", workload_basic_kit=Decimal("4"), spare_parts=Decimal("500")))
    db.commit()


def test_price_lookup_by_subsidiary(db):
    _seed(db)
    row = get_prices(db, "Weber Iberica")
    assert row is not None and row.tech_rate == Decimal("60")
    assert get_prices(db, "NOWHERE") is None


def test_price_update_replaces_whole_row(db):
    _seed(db)
    updated = update_prices(
        db,
        "Weber Iberica",
        PriceUpdate(
            currency="EUR",
            km_rate=Decimal("0.7"),
            tech_rate=Decimal("65"),
            diet_full_rate=Decimal("45"),
            diet_half_rate=Decimal("22"),
            hotel_rate=Decimal("90"),
            discount_rate=Decimal("0.20"),
        ),
    )
    assert updated is not None
    assert updated.tech_rate == Decimal("65") and updated.km_rate == Decimal("0.7")
    assert updated.discount_rate == Decimal("0.20")
    assert get_prices(db, "NOWHERE") is None
    assert (
        update_prices(
            db,
            "NOWHERE",
            PriceUpdate(
                currency="EUR",
                km_rate=Decimal("1"),
                tech_rate=Decimal("1"),
                diet_full_rate=Decimal("1"),
                diet_half_rate=Decimal("1"),
                hotel_rate=Decimal("1"),
                discount_rate=Decimal("0.15"),
            ),
        )
        is None
    )


def test_price_update_creates_missing_row_only_for_registered_subsidiary(db):
    _seed(db)
    assert get_prices(db, "Weber Italy") is None

    created = update_prices(
        db,
        "Weber Italy",
        PriceUpdate(
            currency="EUR",
            km_rate=Decimal("0.62"),
            tech_rate=Decimal("78"),
            diet_full_rate=Decimal("48"),
            diet_half_rate=Decimal("24"),
            hotel_rate=Decimal("110"),
            discount_rate=Decimal("0.18"),
        ),
    )

    assert created is not None
    assert created.currency == "EUR"
    assert created.km_rate == Decimal("0.6200")
    assert created.tech_rate == Decimal("78.00")
    assert created.discount_rate == Decimal("0.1800")
    assert get_prices(db, "Weber Unknown") is None
    assert update_prices(
        db,
        "Weber Unknown",
        PriceUpdate(
            currency="EUR",
            km_rate=Decimal("1"),
            tech_rate=Decimal("1"),
            diet_full_rate=Decimal("1"),
            diet_half_rate=Decimal("1"),
            hotel_rate=Decimal("1"),
            discount_rate=Decimal("0.15"),
        ),
    ) is None


def test_distance_and_kit_lookups(db):
    _seed(db)
    distance = get_distance(db, "Weber Iberica", "Madrid")
    assert distance is not None and distance.km == Decimal("350")
    assert get_distance(db, "Weber Iberica", "Atlantis") is None
    kit = get_kit(db, "CCS304")
    assert kit is not None and kit.spare_parts == Decimal("500")
    assert get_kit(db, "NOPE") is None


def test_kit_create_duplicate_and_delete(db):
    created = create_kit(
        db, BasicKitCreate(model="CCS402", workload_basic_kit=Decimal("3"), spare_parts=Decimal("400"))
    )
    assert created.model == "CCS402"
    with pytest.raises(KitAlreadyExists):
        create_kit(
            db, BasicKitCreate(model="CCS402", workload_basic_kit=Decimal("1"), spare_parts=Decimal("1"))
        )
    assert delete_kit(db, "CCS402") is True
    assert get_kit(db, "CCS402") is None
    assert delete_kit(db, "CCS402") is False


def test_kit_upsert_creates_and_replaces(db):
    created = upsert_kit(db, "CCS500", BasicKitUpsert(workload_basic_kit=Decimal("2"), spare_parts=Decimal("100")))
    assert created.model == "CCS500"
    replaced = upsert_kit(db, "CCS500", BasicKitUpsert(workload_basic_kit=Decimal("5"), spare_parts=Decimal("200")))
    assert replaced.spare_parts == Decimal("200")
    assert replaced.id == created.id


def test_distance_upsert_creates_and_replaces(db):
    _seed(db)
    created = upsert_distance(
        db,
        "Weber Germany",
        "Hesse",
        DistanceUpdate(service_center="Frankfurt", km=Decimal("200"), trip_hours=Decimal("2.5")),
    )
    assert created.province == "Hesse" and created.km == Decimal("200")
    replaced = upsert_distance(
        db,
        "Weber Germany",
        "Hesse",
        DistanceUpdate(service_center="Frankfurt", km=Decimal("210"), trip_hours=Decimal("3")),
    )
    assert replaced.km == Decimal("210")
    assert replaced.id == created.id
    assert {d.province for d in list_distances(db, "Weber Germany")} == {"Hesse"}
    assert [kit.model for kit in list_kits(db)] == ["CCS304"]
    assert delete_distance(db, "Weber Germany", "Hesse") is True
    assert get_distance(db, "Weber Germany", "Hesse") is None
    assert delete_distance(db, "Weber Germany", "Hesse") is False


def test_distance_same_province_can_have_different_subsidiaries(db):
    _seed(db)
    iberica = get_distance(db, "Weber Iberica", "Madrid")
    germany = upsert_distance(
        db,
        "Weber Germany",
        "Madrid",
        DistanceUpdate(service_center="Frankfurt", km=Decimal("10"), trip_hours=Decimal("1")),
    )
    assert iberica is not None and iberica.km == Decimal("350")
    assert germany.km == Decimal("10")
    assert len(list_distances(db)) == 2


def test_germany_distance_requires_an_approved_service_center(db):
    _seed(db)
    with pytest.raises(InvalidServiceCenter):
        upsert_distance(
            db,
            "Weber Germany",
            "Lower Saxony",
            DistanceUpdate(service_center="Hamburg", km=Decimal("120"), trip_hours=Decimal("1.5")),
        )
    assert GERMAN_SERVICE_CENTERS == ("Oldenburg", "Werther", "Frankfurt", "Wolfertschwenden")


def test_distance_rejects_a_subsidiary_missing_from_catalog(db):
    _seed(db)
    with pytest.raises(UnknownSubsidiary):
        upsert_distance(
            db,
            "Unknown Filial",
            "Somewhere",
            DistanceUpdate(km=Decimal("10"), trip_hours=Decimal("1")),
        )
