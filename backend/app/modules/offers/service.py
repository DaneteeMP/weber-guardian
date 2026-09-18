"""Offer logic. Receives a Session, returns models. No HTTP here."""
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.customers.models import Customer
from app.modules.offers.models import Offer, OfferItem
from app.modules.offers.pricing_engine import PricingInput, calculate
from app.modules.offers.schemas import OfferCalculateIn, OfferCalculateOut, OfferCreate


class UnknownCustomer(Exception):
    """Domain error: customer_id has no customers row. Router maps it to 404."""

    def __init__(self, customer_id: str):
        super().__init__(f"Unknown customer: {customer_id}")
        self.customer_id = customer_id


class OfferAlreadyExists(Exception):
    """Domain error: id_guardian_offer taken. Router maps it to 409."""

    def __init__(self, number: str):
        super().__init__(f"Offer already exists: {number}")
        self.number = number


def calculate_price(data: OfferCalculateIn) -> OfferCalculateOut:
    """Dry-run: run the engine without touching the DB."""
    out = calculate(
        PricingInput(
            work_hours=data.work_hours,
            bk_hours=data.bk_hours,
            report_hours=data.report_hours,
            trip_hours_base=data.trip_hours_base,
            km=data.km,
            km_rate=data.km_rate,
            tech_rate=data.tech_rate,
            diet_full_rate=data.diet_full_rate,
            diet_half_rate=data.diet_half_rate,
            hotel_rate=data.hotel_rate,
            discount_rate=data.discount_rate,
            currency=data.currency,
        ),
        bk_price=data.bk_price,
    )
    return OfferCalculateOut(
        work_hours=out.work_hours,
        bk_hours=out.bk_hours,
        report_hours=out.report_hours,
        total_hours=out.total_hours,
        num_days=out.num_days,
        trip_cost=out.trip_cost,
        trip_hours=out.trip_hours,
        diets=out.diets,
        hotel_nights_cost=out.hotel_nights_cost,
        expenses=out.expenses,
        hours_import=out.hours_import,
        discount=out.discount,
        bk_price=out.bk_price,
        total=out.total,
        total_end=out.total_end,
        currency=out.currency,
    )


def _fallback_number() -> str:
    """Generic in-core numbering (core never imports app.weber)."""
    year = datetime.now().year
    return f"G-02-{year}-{uuid.uuid4().hex[:8].upper()}"


def create_offer(db: Session, data: OfferCreate) -> Offer:
    """Create header + items atomically. Server computes all prices."""
    customer = db.scalar(select(Customer).where(Customer.customer_id == data.customer_id))
    if customer is None:
        raise UnknownCustomer(data.customer_id)

    priced = calculate_price(data.pricing)
    number = data.id_guardian_offer or _fallback_number()

    offer = Offer(
        id_guardian_offer=number,
        customer_id=data.customer_id,
        status=data.status,
        responsible_person=data.responsible_person,
        language=data.language,
        inspection_frequency=data.inspection_frequency,
        currency=priced.currency,
        work_hours=priced.work_hours,
        bk_hours=priced.bk_hours,
        report_hours=priced.report_hours,
        total_hours=priced.total_hours,
        trip_hours=priced.trip_hours,
        trip_cost=priced.trip_cost,
        diets=priced.diets,
        hotel_cost=priced.hotel_nights_cost,
        expenses=priced.expenses,
        hours_import=priced.hours_import,
        discount=priced.discount,
        bk_price=priced.bk_price,
        total=priced.total,
        total_end=priced.total_end,
        general_comments=data.general_comments,
    )
    for pos, item in enumerate(data.items, start=1):
        offer.items.append(
            OfferItem(
                row_no=pos,
                equipment=item.equipment,
                description=item.description,
                import_amount=item.import_amount,
                workload=item.workload,
            )
        )
    db.add(offer)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Distinguish a race on customer (404) from a duplicate number (409).
        gone = db.scalar(select(Customer).where(Customer.customer_id == data.customer_id)) is None
        if gone:
            raise UnknownCustomer(data.customer_id) from None
        raise OfferAlreadyExists(number) from None
    db.refresh(offer)
    return offer


def list_offers(db: Session, customer_id: str | None = None, limit: int = 50, offset: int = 0) -> list[Offer]:
    """List offers, optionally filtered by external customer_id."""
    stmt = select(Offer).options(selectinload(Offer.items)).order_by(Offer.created_at.desc())
    if customer_id:
        stmt = stmt.where(Offer.customer_id == customer_id)
    return list(db.scalars(stmt.limit(limit).offset(offset)))


def get_offer(db: Session, offer_id: uuid.UUID) -> Offer | None:
    """Fetch one offer with its items, or None."""
    return db.scalar(select(Offer).options(selectinload(Offer.items)).where(Offer.id == offer_id))
