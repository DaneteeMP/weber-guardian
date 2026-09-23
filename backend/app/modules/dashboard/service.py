"""Dashboard logic. Aggregate counts, all through the subsidiary scope.

Unlike the Rust route (which counts the whole database for everyone),
scoped callers only see their subsidiary plus legacy NULL rows.
"""
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.dashboard.schemas import CountryCount, DashboardStats
from app.modules.equipment.models import Equipment
from app.modules.offers.models import Offer, OfferItem


def _in_scope(customer_col, subsidiary_id: str | None):
    if subsidiary_id is None:
        return None
    return or_(customer_col == subsidiary_id, customer_col.is_(None))


def get_stats(db: Session, subsidiary_id: str | None = None) -> DashboardStats:
    scope = _in_scope(Customer.subsidiary_id, subsidiary_id)

    customers = select(func.count()).select_from(Customer)
    equipment = select(func.count()).select_from(Equipment).join(
        Customer, Equipment.customer_id == Customer.customer_id
    )
    offers = select(func.count()).select_from(Offer).join(
        Customer, Offer.customer_id == Customer.customer_id
    )
    lines = (
        select(func.count())
        .select_from(OfferItem)
        .join(Offer, OfferItem.offer_id == Offer.id)
        .join(Customer, Offer.customer_id == Customer.customer_id)
    )
    countries = select(Customer.country, func.count()).group_by(Customer.country)
    if scope is not None:
        customers = customers.where(scope)
        equipment = equipment.where(scope)
        offers = offers.where(scope)
        lines = lines.where(scope)
        countries = countries.where(scope)

    country_rows = [
        CountryCount(country=country or "—", count=count)
        for country, count in db.execute(countries.where(Customer.country.is_not(None))).all()
    ]
    country_rows.sort(key=lambda c: c.count, reverse=True)

    return DashboardStats(
        total_customers=db.scalar(customers) or 0,
        total_equipment=db.scalar(equipment) or 0,
        total_offers=db.scalar(offers) or 0,
        total_offer_lines=db.scalar(lines) or 0,
        countries=country_rows,
    )
