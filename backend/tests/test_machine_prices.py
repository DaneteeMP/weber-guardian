"""Machine-price tests: upsert, lookup, delete. SQLite only."""
from decimal import Decimal

from app.modules.machine_prices.schemas import MachinePriceUpsert
from app.modules.machine_prices.service import delete_price, get_price, list_prices, upsert_price


def _data(price="2900", inspections=4):
    return MachinePriceUpsert(annual_price=Decimal(price), inspections_per_year=inspections)


def test_upsert_creates_and_replaces(db):
    created = upsert_price(db, "804-227", _data())
    assert created.annual_price == Decimal("2900")
    replaced = upsert_price(db, "804-227", _data(price="3000", inspections=2))
    assert replaced.annual_price == Decimal("3000")
    assert replaced.inspections_per_year == 2
    assert replaced.id == created.id
    assert get_price(db, "804-227") is not None
    assert get_price(db, "NOPE") is None
    assert len(list_prices(db)) == 1


def test_delete_price(db):
    upsert_price(db, "804-227", _data())
    assert delete_price(db, "804-227") is True
    assert get_price(db, "804-227") is None
    assert delete_price(db, "804-227") is False
