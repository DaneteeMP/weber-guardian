"""Catalog tests: seeded reads, unknown keys, prices scope. SQLite only."""
from decimal import Decimal

from app.modules.basic_kit.models import BasicKit
from app.modules.basic_kit.service import get_kit
from app.modules.distances.models import Distance
from app.modules.distances.service import get_distance
from app.modules.prices.models import PriceList
from app.modules.prices.service import get_prices


def _seed(db):
    db.add(
        PriceList(
            subsidiary_id="ES",
            km_rate=Decimal("0.5"),
            tech_rate=Decimal("60"),
            diet_full_rate=Decimal("40"),
            diet_half_rate=Decimal("20"),
            hotel_rate=Decimal("80"),
        )
    )
    db.add(Distance(province="Madrid", km=Decimal("350"), trip_hours=Decimal("4")))
    db.add(BasicKit(model="CCS304", workload_basic_kit=Decimal("4"), spare_parts=Decimal("500")))
    db.commit()


def test_price_lookup_by_subsidiary(db):
    _seed(db)
    row = get_prices(db, "ES")
    assert row is not None and row.tech_rate == Decimal("60")
    assert get_prices(db, "NOWHERE") is None


def test_distance_and_kit_lookups(db):
    _seed(db)
    distance = get_distance(db, "Madrid")
    assert distance is not None and distance.km == Decimal("350")
    assert get_distance(db, "Atlantis") is None
    kit = get_kit(db, "CCS304")
    assert kit is not None and kit.spare_parts == Decimal("500")
    assert get_kit(db, "NOPE") is None
