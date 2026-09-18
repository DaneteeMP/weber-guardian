"""Pricing engine tests (F1). 100% of the rules, no DB, no API."""
from decimal import Decimal

import pytest

from app.modules.offers.pricing_engine import PricingInput, calculate


def _base(**overrides):
    params = {
        "work_hours": Decimal("10"),
        "bk_hours": Decimal("0"),
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
    return PricingInput(**params)


def test_rounds_up_to_8h_days():
    out = calculate(_base())
    # raw = 3 + 10 + 0 + 2 = 15 -> 16h, 2 days. Adjustment goes to work.
    assert out.total_hours == Decimal("16.0")
    assert out.num_days == 2
    assert out.work_hours == Decimal("11.0")


def test_nearby_km_under_200():
    out = calculate(_base())
    # trip scales per day, half diets only, no hotel.
    assert out.trip_cost == Decimal("50.00")
    assert out.trip_hours == Decimal("6.0")
    assert out.diets == Decimal("40.00")
    assert out.hotel_nights_cost == Decimal("0.00")
    assert out.expenses == Decimal("90.00")


def test_far_km_over_200():
    out = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("4")))
    # trip = km*rate + base*tech; hotel for extra days; full+half diets.
    assert out.trip_cost == Decimal("300") * Decimal("0.5") + Decimal("4") * Decimal("60")
    assert out.hotel_nights_cost == Decimal("80.00")  # (2 days - 1) * 80
    assert out.diets == Decimal("60.00")  # 1 x 40 + 20


def test_total_and_total_end_fixed():
    """Locks the inherited OfferBuilder bug fix.

    Buggy JS: total = hours + discount + expenses + kit (1194),
    total_end = total - discount (1050, client never got 15% off).
    Fixed: total = hours + expenses + kit (1050 gross),
    total_end = total - discount (906 net).
    """
    out = calculate(_base())
    assert out.hours_import == Decimal("960.00")
    assert out.discount == Decimal("144.00")
    assert out.total == Decimal("1050.00")
    assert out.total_end == Decimal("906.00")
    assert out.total - out.total_end == out.discount


def test_money_uses_decimal_with_two_places():
    out = calculate(_base())
    for amount in (out.trip_cost, out.diets, out.expenses, out.hours_import, out.discount, out.total, out.total_end):
        assert isinstance(amount, Decimal)
        assert amount.as_tuple().exponent == -2
    assert out.currency == "EUR"


def test_negative_inputs_raise():
    with pytest.raises(ValueError):
        calculate(_base(work_hours=Decimal("-1")))
    with pytest.raises(ValueError):
        calculate(_base(km=Decimal("-5")))
