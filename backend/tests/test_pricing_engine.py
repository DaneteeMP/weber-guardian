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
    # raw = 6 (travel: 3h x 2 days) + 10 + 0 + 2 = 18 -> 24h, 3 days.
    assert out.total_hours == Decimal("24.0")
    assert out.num_days == 3
    # The breakdown adds up to the total: the work row takes the rounding
    # padding, the travel and report rows keep their own hours.
    assert out.work_hours == Decimal("16.0")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )


def test_nearby_km_under_200_repeats_once_per_day():
    out = calculate(_base())
    # Nearby travel repeats per working day (legacy NumeroViajes = work/8:
    # work 10 -> ceil(10/8) = 2 days, independent of report hours).
    assert out.trip_cost == Decimal("50.00")  # 50 km x 0.5 x 2 days
    assert out.trip_hours == Decimal("6.0")  # 3h base x 2 days
    # Hotel applies to nearby too: floor((10 + 6)/8) = 2 nights; both
    # working days carry a hotel night, so both diets are full.
    assert out.hotel_nights_cost == Decimal("160.00")
    assert out.diets == Decimal("80.00")  # 2 full, 0 leftover half diets
    assert out.expenses == Decimal("290.00")  # 50 trip + 80 diets + 160 hotel


def test_nearby_half_diet_for_days_without_hotel():
    # A working day without a hotel night keeps the legacy half diet.
    # work 9 -> ceil(9/8) = 2 working days, legs = 2 x 1h = 2h;
    # floor((9 + 2)/8) = 1 night -> 1 full diet + 1 half diet.
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
    assert two_machines.trip_hours == Decimal("6.0")


def test_nearby_one_day_repeats_once():
    # One 8h day (work 3 + trip 1 + report 2): a single leg and a single diet.
    out = calculate(_base(work_hours=Decimal("3"), trip_hours_base=Decimal("1")))
    assert out.num_days == 1
    assert out.trip_cost == Decimal("25.00")
    assert out.trip_hours == Decimal("1.0")
    assert out.diets == Decimal("20.00")
    assert out.work_hours == Decimal("5.0")  # 8 - trip 1 - report 2


def test_far_km_over_200():
    out = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("4")))
    # trip = km*rate + base*tech; hotel = 1 night per 8h block of work+trip;
    # full diet per night + a half diet on the travel day.
    assert out.trip_cost == Decimal("300") * Decimal("0.5") + Decimal("4") * Decimal("60")
    assert out.hotel_nights_cost == Decimal("80.00")  # floor((10 + 4)/8) = 1 night
    assert out.diets == Decimal("60.00")  # 1 x 40 + 20
    # Far travel keeps a single leg for the whole contract (no day scaling).
    assert out.trip_hours == Decimal("4.0")


def test_far_hotel_nights_ignore_report_hours():
    """One hotel night per full 8h block of work + travel (legacy rule); the
    report row must not extend the stay or add nights/diets."""
    lean = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("5"), report_hours=Decimal("2")))
    loaded = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("5"), report_hours=Decimal("10")))
    # work 10 + trip 5 = 15 -> floor(15/8) = 1 night, regardless of report.
    assert lean.hotel_nights_cost == Decimal("80.00")
    assert loaded.hotel_nights_cost == Decimal("80.00")
    assert lean.diets == loaded.diets == Decimal("60.00")  # 1 full + 1 half


def test_far_two_hotel_nights_for_long_work():
    out = calculate(_base(km=Decimal("300"), trip_hours_base=Decimal("5"), work_hours=Decimal("16")))
    # work 16 + trip 5 = 21 -> floor(21/8) = 2 nights.
    assert out.hotel_nights_cost == Decimal("160.00")
    assert out.diets == Decimal("100.00")  # 2 full + 1 half


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
    assert out.total == Decimal("1946.00")
    # Net: hours import + expenses (the kit is added on top).
    assert out.total_end == Decimal("1730.00")
    assert out.total - out.discount == out.total_end


def test_basic_kit_splits_rounding_and_prices_spares():
    out = calculate(
        _base(basic_kit=True, bk_hours=Decimal("2")), bk_price=Decimal("100")
    )
    # raw = 6 (travel) + 10 + 2 + 2 = 20 -> 24h (3 days). Adjustment = 4:
    # half to the kit (2), the rest to work. Trip = 3h x 2 work days
    # (ceil(12/8)) = 6; work absorbs the rest.
    assert out.total_hours == Decimal("24.0")
    assert out.bk_hours == Decimal("4.0")
    assert out.work_hours == Decimal("12.0")  # 24 - trip 6 - report 2 - bk 4
    assert out.bk_price == Decimal("100.00")
    assert (
        out.work_hours + out.trip_hours + out.report_hours + out.bk_hours == out.total_hours
    )
    # hours = 24 * 60; total = hours + expenses + spares. Expenses = trip 50
    # + diets 80 (2 nights) + hotel 160.
    assert out.hours_import == Decimal("1440.00")
    assert out.total == Decimal("1946.00")  # gross: 1440 + 290 expenses + 216 discount
    assert out.total_end == Decimal("1830.00")  # net: 1440 + 290 expenses + 100 kit


def test_no_basic_kit_keeps_rounding_on_work():
    out = calculate(_base(bk_hours=Decimal("2")), bk_price=Decimal("100"))
    # Same raw numbers but the selector is off: no split, bk_hours stays raw.
    assert out.bk_hours == Decimal("2.0")
    # work = 24 - trip 6 - report 2 - bk 2 = 14.
    assert out.work_hours == Decimal("14.0")
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
    assert out.total_end == Decimal("1730.00")


def test_repeated_travel_legs_are_inside_the_billed_total():
    # Nearby trip legs (2 work days x 12h = 24h) belong to the billed
    # total: raw = 24 + 9 + 0 + 2 = 35 -> 40h (5 days). The work row takes
    # the rounding padding and the report row keeps its hours.
    out = calculate(
        _base(
            work_hours=Decimal("9"),
            trip_hours_base=Decimal("12"),
            report_hours=Decimal("2"),
        )
    )
    assert out.total_hours == Decimal("40.0")
    assert out.trip_hours == Decimal("24.0")
    assert out.work_hours == Decimal("14.0")  # 40 - trip 24 - report 2
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