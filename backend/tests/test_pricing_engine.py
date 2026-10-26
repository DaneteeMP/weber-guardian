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
    # raw = 12 (round trip: 3h x 2 days x 2 legs) + 10 + 0 + 2 = 24 -> 24h, 3 days.
    assert out.total_hours == Decimal("24.0")
    assert out.num_days == 3
    # The breakdown adds up to the total: the work row takes the rounding
    # padding, the travel and report rows keep their own hours.
    assert out.work_hours == Decimal("10.0")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )


def test_nearby_km_under_200_repeats_once_per_day():
    out = calculate(_base())
    # Nearby travel repeats per working day (legacy NumeroViajes = work/8:
    # work 10 -> ceil(10/8) = 2 days, independent of report hours).
    assert out.trip_cost == Decimal("100.00")  # 50 km x 0.5 x 2 days x 2 legs
    assert out.trip_hours == Decimal("12.0")  # 3h base x 2 days x 2 legs
    # Hotel applies to nearby too: floor((10 + 12)/8) = 2 nights; both
    # working days carry a hotel night, so both diets are full.
    assert out.hotel_nights_cost == Decimal("160.00")
    assert out.diets == Decimal("80.00")  # 2 full, 0 leftover half diets
    assert out.expenses == Decimal("340.00")  # 100 trip + 80 diets + 160 hotel


def test_nearby_half_diet_for_days_without_hotel():
    # A working day without a hotel night keeps the legacy half diet.
    # work 9 -> ceil(9/8) = 2 working days, legs = 2 x 1h x 2 = 4h;
    # floor((9 + 4)/8) = 1 night -> 1 full diet + 1 half diet.
    out = calculate(
        _base(work_hours=Decimal("9"), trip_hours_base=Decimal("1"), report_hours=Decimal("2"))
    )
    assert out.hotel_nights_cost == Decimal("80.00")
    assert out.diets == Decimal("60.00")  # 1 full (hotel) + 1 half (no hotel)


def test_nearby_hotel_ignores_report_hours():
    """The report row must not add hotel nights or upgrade diets (same as far)."""
    lean = calculate(_base(report_hours=Decimal("2")))
    loaded = calculate(_base(report_hours=Decimal("10")))
    assert lean.hotel_nights_cost == loaded.hotel_nights_cost == Decimal("160.00")
    assert lean.diets == loaded.diets == Decimal("80.00")


def test_nearby_report_hours_do_not_inflate_trips():
    """Legacy NumeroViajes = HorasGuardian/8: trips scale with work days only.
    Adding machines (report hours) must not add trips, trip cost or diets."""
    two_machines = calculate(_base(report_hours=Decimal("2")))  # 2 machines
    five_machines = calculate(_base(report_hours=Decimal("10")))  # 5 machines
    assert two_machines.trip_cost == five_machines.trip_cost
    assert two_machines.trip_hours == five_machines.trip_hours
    assert two_machines.diets == five_machines.diets
    # Same work days (ceil(10/8) = 2) regardless of the report row.
    assert two_machines.trip_hours == Decimal("12.0")


def test_nearby_one_day_repeats_once():
    # One 8h day (work 3 + round trip 2 + report 2): one round trip and one diet.
    out = calculate(_base(work_hours=Decimal("3"), trip_hours_base=Decimal("1")))
    assert out.num_days == 1
    assert out.trip_cost == Decimal("50.00")
    assert out.trip_hours == Decimal("2.0")
    assert out.diets == Decimal("20.00")
    assert out.work_hours == Decimal("4.0")  # 8 - trip 2 - report 2


def test_far_km_over_200():
    out = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("4")))
    # trip = (km*rate + base*tech) x 2 legs; hotel = 1 night per 8h block of
    # work+trip; full diet per night + a half diet on the travel day.
    assert out.trip_cost == (Decimal("300") * Decimal("0.5") + Decimal("4") * Decimal("60")) * 2
    assert out.hotel_nights_cost == Decimal("160.00")  # floor((10 + 8)/8) = 2 nights
    assert out.diets == Decimal("100.00")  # 2 x 40 + 20
    # Far travel is a single round trip for the whole contract (no day scaling).
    assert out.trip_hours == Decimal("8.0")


def test_far_hotel_nights_ignore_report_hours():
    """One hotel night per full 8h block of work + travel (legacy rule); the
    report row must not extend the stay or add nights/diets."""
    lean = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("5"), report_hours=Decimal("2")))
    loaded = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("5"), report_hours=Decimal("10")))
    # work 10 + round trip 10 = 20 -> floor(20/8) = 2 nights, regardless of report.
    assert lean.hotel_nights_cost == Decimal("160.00")
    assert loaded.hotel_nights_cost == Decimal("160.00")
    assert lean.diets == loaded.diets == Decimal("100.00")  # 2 full + 1 half


def test_far_two_hotel_nights_for_long_work():
    out = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("5"), work_hours=Decimal("16")))
    # work 16 + round trip 10 = 26 -> floor(26/8) = 3 nights.
    assert out.hotel_nights_cost == Decimal("240.00")
    assert out.diets == Decimal("140.00")  # 3 full + 1 half


def test_total_and_total_end_fixed():
    """Locks the legacy amounts (WeberAssistant).

    Total amount = hours import + expenses import (what the client pays).
    Total = total amount + discount: the gross the module lines sum to,
    the discount is added to it and taken off the net.
    """
    out = calculate(_base())
    assert out.hours_import == Decimal("1440.00")
    assert out.discount == Decimal("216.00")
    # Gross: hours import + expenses + discount.
    assert out.total == Decimal("1996.00")
    # Net: hours import + expenses (the kit is added on top).
    assert out.total_end == Decimal("1780.00")
    assert out.total - out.discount == out.total_end


def test_basic_kit_splits_rounding_and_prices_spares():
    out = calculate(
        _base(basic_kit=True, bk_hours=Decimal("2")), bk_price=Decimal("100")
    )
    # raw = 12 (round trip) + 10 + 2 + 2 = 26 -> 32h (4 days). Adjustment = 6:
    # half to the kit (3), the rest to work. Trip = 3h x 2 work days x 2 legs
    # (ceil(12/8)) = 12; work absorbs the rest.
    assert out.total_hours == Decimal("32.0")
    assert out.bk_hours == Decimal("5.0")
    assert out.work_hours == Decimal("13.0")  # 32 - trip 12 - report 2 - bk 5
    assert out.bk_price == Decimal("100.00")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )
    # hours = 32 * 60; total = hours + expenses + spares. Expenses = trip 100
    # + diets 120 (3 nights) + hotel 240.
    assert out.hours_import == Decimal("1920.00")
    assert out.total == Decimal("2668.00")  # gross: 1920 + 460 expenses + 288 discount
    assert out.total_end == Decimal("2480.00")  # net: 1920 + 460 expenses + 100 kit


def test_no_basic_kit_keeps_rounding_on_work():
    out = calculate(_base(bk_hours=Decimal("2")), bk_price=Decimal("100"))
    # Same raw numbers but the selector is off: no split, bk_hours stays raw.
    assert out.bk_hours == Decimal("2.0")
    # work = 32 - trip 12 - report 2 - bk 2 = 16.
    assert out.work_hours == Decimal("16.0")
    assert out.total_hours == Decimal("32.0")


def test_work_floor_borrows_from_kit():
    # raw = 4.6 (round trip) + 0.2 + 2 + 1 = 7.8 -> 8h, adjustment 0.2. The
    # split leaves the work row below 1h, so the missing time is borrowed from
    # the kit row.
    out = calculate(
        _base(
            work_hours=Decimal("0.2"),
            bk_hours=Decimal("2"),
            report_hours=Decimal("1"),
            trip_hours_base=Decimal("2.3"),
            basic_kit=True,
        )
    )
    assert out.total_hours == Decimal("8.0")
    assert out.work_hours >= Decimal("1.0")
    assert out.bk_hours == Decimal("1.4")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )


def test_off_guardian_never_discounts():
    out = calculate(_base(apply_discount=False))
    assert out.discount == Decimal("0.00")
    assert out.total_end == out.total
    assert out.total_end == Decimal("1780.00")


def test_repeated_travel_legs_are_inside_the_billed_total():
    # Nearby round trips (2 work days x 12h x 2 legs = 48h) belong to the
    # billed total: raw = 48 + 9 + 0 + 2 = 59 -> 64h (8 days). The work row
    # takes the rounding padding and the report row keeps its hours.
    out = calculate(
        _base(
            work_hours=Decimal("9"),
            trip_hours_base=Decimal("12"),
            report_hours=Decimal("2"),
        )
    )
    assert out.total_hours == Decimal("64.0")
    assert out.trip_hours == Decimal("48.0")
    assert out.work_hours == Decimal("14.0")  # 64 - trip 48 - report 2
    assert out.report_hours == Decimal("2.0")


def test_work_row_is_never_below_the_real_work():
    """Rounding to 8h days may only add hours to the work row.

    The travel counted in the total is the one of the breakdown (the
    repeated legs of a nearby trip), so the work row can never be reduced
    below the work the modules really need.
    """
    for work_hours, trip_base in (("16", "6"), ("10", "3"), ("9", "12"), ("3", "1")):
        out = calculate(
            _base(
                work_hours=Decimal(work_hours),
                trip_hours_base=Decimal(trip_base),
            )
        )
        assert out.work_hours >= Decimal(work_hours)
        assert (
            out.work_hours + out.trip_hours + out.report_hours + out.bk_hours
            == out.total_hours
        )


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