"""Pricing engine for Guardian offers (F1).

Pure function: no DB, no FastAPI, no floats. All money is Decimal (EUR).
Migrates the rules from WeberAssistant OfferBuilder (8h working days,
km<200 nearby vs far travel, diets/hotel, 15% discount) with one fix:

Inherited bug (Rust frontend): total = hours + discount + expenses + kit,
total_end = total - discount. The displayed total was inflated and the
client never got the discount. Fixed here: total = hours + expenses + kit
(gross), total_end = total - discount (net).
"""
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, ROUND_HALF_UP

TWOPLACES = Decimal("0.01")
ONEPLACE = Decimal("0.1")
EIGHT = Decimal("8")


def _money(value: Decimal) -> Decimal:
    """Round money to 2 decimals (half up)."""
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _hours(value: Decimal) -> Decimal:
    """Round hours to 1 decimal (half up)."""
    return value.quantize(ONEPLACE, rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class PricingInput:
    """Aggregated inputs. Catalog lookups (sums, distances, kits) happen in service."""

    work_hours: Decimal
    bk_hours: Decimal = Decimal("0")
    report_hours: Decimal = Decimal("0")
    trip_hours_base: Decimal = Decimal("0")
    km: Decimal = Decimal("0")
    km_rate: Decimal = Decimal("0")
    tech_rate: Decimal = Decimal("0")
    diet_full_rate: Decimal = Decimal("0")
    diet_half_rate: Decimal = Decimal("0")
    hotel_rate: Decimal = Decimal("0")
    discount_rate: Decimal = Decimal("0.15")
    currency: str = "EUR"


@dataclass(frozen=True)
class PricingOutput:
    """Full breakdown. total = gross, total_end = net after discount."""

    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    num_days: int
    trip_cost: Decimal
    trip_hours: Decimal
    diets: Decimal
    hotel_nights_cost: Decimal
    expenses: Decimal
    hours_import: Decimal
    discount: Decimal
    bk_price: Decimal
    total: Decimal
    total_end: Decimal
    currency: str = "EUR"


def calculate(inp: PricingInput, bk_price: Decimal = Decimal("0")) -> PricingOutput:
    """Run the pricing rules. Raises ValueError on negative inputs."""
    for name in (
        "work_hours",
        "bk_hours",
        "report_hours",
        "trip_hours_base",
        "km",
        "km_rate",
        "tech_rate",
        "diet_full_rate",
        "diet_half_rate",
        "hotel_rate",
        "discount_rate",
    ):
        if getattr(inp, name) < 0:
            raise ValueError(f"{name} must be >= 0")
    if bk_price < 0:
        raise ValueError("bk_price must be >= 0")

    raw = inp.trip_hours_base + inp.work_hours + inp.bk_hours + inp.report_hours
    total_hours = (raw / EIGHT).to_integral_value(rounding=ROUND_CEILING) * EIGHT
    if total_hours < EIGHT:
        total_hours = EIGHT
    adjustment = total_hours - raw

    adjusted_work = inp.work_hours + adjustment
    adjusted_bk = inp.bk_hours
    if inp.bk_hours > 0 and adjustment > 0:
        half_adj = (adjustment / 2).to_integral_value(rounding=ROUND_FLOOR)
        adjusted_bk = inp.bk_hours + half_adj
        adjusted_work = inp.work_hours + adjustment - half_adj
    if adjusted_work < 1:
        adjusted_bk = max(Decimal("0"), adjusted_bk - (Decimal("1") - adjusted_work))
        adjusted_work = Decimal("1")

    num_days = max(1, int(total_hours // EIGHT))

    if inp.km < 200:
        trip_cost = inp.km * inp.km_rate * num_days
        trip_hours = inp.trip_hours_base * num_days
        diets = Decimal(num_days) * inp.diet_half_rate
        hotel = Decimal("0")
    else:
        trip_cost = inp.km * inp.km_rate + inp.trip_hours_base * inp.tech_rate
        trip_hours = inp.trip_hours_base
        hotel = Decimal(num_days - 1) * inp.hotel_rate
        diets = Decimal(num_days - 1) * inp.diet_full_rate + inp.diet_half_rate

    expenses = trip_cost + diets + hotel
    # hours_import is charged on the ROUNDED total_hours (whole 8h days), so it
    # can exceed the sum of the raw workload lines by the rounding adjustment
    # (legacy "HorasRedondeadas"). The stored line amounts are the
    # pre-distribution workload × rate: the legacy RepartirCostes pass that made
    # the lines sum to the total is not implemented yet.
    hours_import = total_hours * inp.tech_rate
    discount = hours_import * inp.discount_rate
    total = hours_import + expenses + bk_price
    total_end = total - discount

    return PricingOutput(
        work_hours=_hours(adjusted_work),
        bk_hours=_hours(adjusted_bk),
        report_hours=_hours(inp.report_hours),
        total_hours=_hours(total_hours),
        num_days=num_days,
        trip_cost=_money(trip_cost),
        trip_hours=_hours(trip_hours),
        diets=_money(diets),
        hotel_nights_cost=_money(hotel),
        expenses=_money(expenses),
        hours_import=_money(hours_import),
        discount=_money(discount),
        bk_price=_money(bk_price),
        total=_money(total),
        total_end=_money(total_end),
        currency=inp.currency,
    )
