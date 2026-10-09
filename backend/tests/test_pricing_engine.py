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


def test_rounds_up_to_8h_days_and_breaks_down_exactly():
    out = calculate(_base())
    # raw = 3 + 10 + 0 + 2 = 15 -> 16h, 2 days.
    assert out.total_hours == Decimal("16.0")
    assert out.num_days == 2
    # Final adjustment: work = 16 - (trip 3 + report 2 + bk 0) = 11. The
    # breakdown always sums to TOTAL HOURS (= TOTAL GUARDIAN H).
    assert out.work_hours == Decimal("11.0")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )


def test_nearby_km_under_200_scales_with_num_trips():
    out = calculate(_base())
    # Nearby travel repeats per trip (default 1): cost, hours and half diet.
    assert out.trip_cost == Decimal("25.00")
    assert out.trip_hours == Decimal("3.0")
    assert out.diets == Decimal("20.00")
    assert out.hotel_nights_cost == Decimal("0.00")
    assert out.expenses == Decimal("45.00")


def test_two_trips_multiply_nearby_legs_and_diets():
    out = calculate(_base(num_trips=2))
    # Twice the trip cost, hours and half diet. The breakdown still sums to
    # TOTAL HOURS: work shrinks to absorb the doubled trip hours.
    assert out.trip_cost == Decimal("50.00")
    assert out.trip_hours == Decimal("6.0")
    assert out.diets == Decimal("40.00")
    assert out.work_hours == Decimal("8.0")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )


def test_far_km_over_200():
    out = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("4")))
    # trip = km*rate + base*tech; hotel for extra days; full+half diets.
    assert out.trip_cost == Decimal("300") * Decimal("0.5") + Decimal("4") * Decimal("60")
    assert out.hotel_nights_cost == Decimal("80.00")  # (2 days - 1) * 80
    assert out.diets == Decimal("60.00")  # 1 x 40 + 20
    # Far travel ignores num_trips (single contract trip over several days).
    assert out.trip_hours == Decimal("4.0")


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
    assert out.total == Decimal("1005.00")
    assert out.total_end == Decimal("861.00")
    assert out.total - out.total_end == out.discount


def test_basic_kit_splits_rounding_and_prices_spares():
    out = calculate(_base(basic_kit=True, bk_hours=Decimal("2"), bk_price=Decimal("100")))
    # raw = 3 + 10 + 2 + 2 = 17 -> 24h (3 days). Adjustment = 7: half to the
    # kit (3), the rest to work. Final work absorbs what is left.
    assert out.total_hours == Decimal("24.0")
    assert out.bk_hours == Decimal("5.0")
    assert out.work_hours == Decimal("14.0")
    assert out.bk_price == Decimal("100.00")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )
    # hours = 24 * 60; total = hours + expenses + spares.
    assert out.hours_import == Decimal("1440.00")
    assert out.total == Decimal("1585.00")
    assert out.total_end == Decimal("1369.00")


def test_no_basic_kit_keeps_rounding_on_work():
    out = calculate(_base(bk_hours=Decimal("2"), bk_price=Decimal("100")))
    # Same raw numbers but the selector is off: no split, bk_hours stays raw.
    assert out.bk_hours == Decimal("2.0")
    # work = 24 - trip 3 - report 2 - bk 2 = 17.
    assert out.work_hours == Decimal("17.0")
    assert out.total_hours == Decimal("24.0")


def test_work_floor_borrows_from_kit():
    # raw = 3 + 0.2 + 3 + 1.5 = 7.7 -> 8h, adjustment 0.3. After the split work
    # stays below 1h, so the missing hour is borrowed from the kit row.
    out = calculate(
        _base(
            work_hours=Decimal("0.2"),
            bk_hours=Decimal("3"),
            report_hours=Decimal("1.5"),
            trip_hours_base=Decimal("3"),
            basic_kit=True,
        )
    )
    assert out.total_hours == Decimal("8.0")
    assert out.work_hours >= Decimal("1.0")
    assert out.bk_hours == Decimal("2.5")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )


def test_off_guardian_never_discounts():
    out = calculate(_base(apply_discount=False))
    assert out.discount == Decimal("0.00")
    assert out.total_end == out.total
    assert out.total_end == Decimal("1005.00")


def test_reajuste_final_zeroes_work_and_report_on_impossible_total():
    # Trip legs (4 trips x 4h) exceed the rounded 8h total: nothing left for
    # work or the report row, so both collapse to zero (legacy behaviour).
    out = calculate(
        _base(
            work_hours=Decimal("1"),
            trip_hours_base=Decimal("4"),
            report_hours=Decimal("1"),
            num_trips=4,
        )
    )
    assert out.total_hours == Decimal("8.0")
    assert out.work_hours == Decimal("0.0")
    assert out.report_hours == Decimal("0.0")
    assert out.trip_hours == Decimal("16.0")


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
    with pytest.raises(ValueError):
        calculate(_base(num_trips=0))