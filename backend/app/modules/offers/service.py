"""Offer logic. Receives a Session, returns models. No HTTP here."""
import uuid
from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.customers.models import Customer
from app.modules.offers.document import OfferDocument, OfferLine
from app.modules.offers.models import Offer, OfferItem
from app.modules.offers.pricing_engine import PricingInput, calculate
from app.modules.offers.schemas import OfferCalculateIn, OfferCalculateOut, OfferCreate, OfferUpdate


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


def create_offer(
    db: Session, data: OfferCreate, created_by: uuid.UUID | None = None, scope_subsidiary: str | None = None
) -> Offer:
    """Create header + items atomically. Server computes all prices."""
    customer = db.scalar(select(Customer).where(Customer.customer_id == data.customer_id))
    if customer is None:
        raise UnknownCustomer(data.customer_id)
    # Scoped callers work on their own filial only (reads as missing otherwise).
    if scope_subsidiary is not None and customer.subsidiary_id != scope_subsidiary:
        raise UnknownCustomer(data.customer_id)

    priced = calculate_price(data.pricing)
    number = data.id_guardian_offer or _fallback_number()
    # A missing offer_date means "same day as the row was created": the PDF and
    # the home fall back to created_at, so the business date is never invented.
    offer_date = data.offer_date or date.today()

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
        created_by=created_by,
        offer_date=offer_date,
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


def list_offers(
    db: Session,
    customer_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    subsidiary_id: str | None = None,
    status: str | None = None,
) -> list[Offer]:
    """List offers with optional customer/status filters and subsidiary scope (None = global).

    Strict: scoped callers see ONLY their subsidiary's customers.
    """
    stmt = select(Offer).options(selectinload(Offer.items)).order_by(Offer.created_at.desc())
    if customer_id:
        stmt = stmt.where(Offer.customer_id == customer_id)
    if status:
        stmt = stmt.where(Offer.status == status)
    if subsidiary_id is not None:
        stmt = stmt.join(Customer, Offer.customer_id == Customer.customer_id).where(
            Customer.subsidiary_id == subsidiary_id
        )
    return list(db.scalars(stmt.limit(limit).offset(offset)))


def offers_summary(db: Session, subsidiary_id: str | None = None) -> dict:
    """Dense home-screen figures, all through the subsidiary scope.

    Returns totals, per-status counts, monthly counts (YYYY-MM) and the
    top customers by offer count with summed net totals.
    """
    base = select(Offer)
    if subsidiary_id is not None:
        base = base.join(Customer, Offer.customer_id == Customer.customer_id).where(
            Customer.subsidiary_id == subsidiary_id
        )
    sub = base.subquery()
    total = db.scalar(select(func.count()).select_from(sub)) or 0
    by_status = [
        {"status": status, "count": count}
        for status, count in db.execute(
            select(sub.c.status, func.count()).group_by(sub.c.status)
        ).all()
    ]
    monthly_counts: dict[str, int] = {}
    # Group by the business date so the chart agrees with the date column and
    # the date printed on the PDF. Rows without offer_date fall back to the day
    # the row was created.
    date_column = select(Offer.offer_date, Offer.created_at)
    if subsidiary_id is not None:
        date_column = date_column.join(Customer, Offer.customer_id == Customer.customer_id).where(
            Customer.subsidiary_id == subsidiary_id
        )
    for offer_date, created_at in db.execute(date_column).all():
        day = offer_date or (created_at.date() if created_at else None)
        month = day.strftime("%Y-%m") if day else "unknown"
        monthly_counts[month] = monthly_counts.get(month, 0) + 1
    monthly = [{"month": month, "count": monthly_counts[month]} for month in sorted(monthly_counts)]
    ranking = [
        {"customer_id": cid, "count": count, "total_end": str(total_end)}
        for cid, count, total_end in db.execute(
            select(sub.c.customer_id, func.count(), func.sum(sub.c.total_end))
            .group_by(sub.c.customer_id)
            .order_by(func.count().desc())
            .limit(15)
        ).all()
    ]
    return {"total": total, "by_status": by_status, "monthly": monthly, "ranking": ranking}


def get_offer(db: Session, offer_id: uuid.UUID, subsidiary_id: str | None = None) -> Offer | None:
    """Fetch one offer with its items, or None (out-of-scope reads as missing)."""
    stmt = select(Offer).options(selectinload(Offer.items)).where(Offer.id == offer_id)
    if subsidiary_id is not None:
        stmt = stmt.join(Customer, Offer.customer_id == Customer.customer_id).where(
            Customer.subsidiary_id == subsidiary_id
        )
    return db.scalar(stmt)


def update_offer(
    db: Session, offer_id: uuid.UUID, data: OfferUpdate, subsidiary_id: str | None = None
) -> Offer | None:
    """Full edit: header fields plus wholesale line replacement with server
    recomputation, in one transaction. None when missing/out of scope."""
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return None
    priced = calculate_price(data.pricing)
    offer.status = data.status
    offer.responsible_person = data.responsible_person
    offer.language = data.language
    offer.inspection_frequency = data.inspection_frequency
    offer.currency = priced.currency
    offer.work_hours = priced.work_hours
    offer.bk_hours = priced.bk_hours
    offer.report_hours = priced.report_hours
    offer.total_hours = priced.total_hours
    offer.trip_hours = priced.trip_hours
    offer.trip_cost = priced.trip_cost
    offer.diets = priced.diets
    offer.hotel_cost = priced.hotel_nights_cost
    offer.expenses = priced.expenses
    offer.hours_import = priced.hours_import
    offer.discount = priced.discount
    offer.bk_price = priced.bk_price
    offer.total = priced.total
    offer.total_end = priced.total_end
    offer.general_comments = data.general_comments
    # offer_date=None means "keep the day the row was created", so an edit that
    # does not touch the date can never wipe it.
    offer.offer_date = data.offer_date or offer.offer_date or (
        offer.created_at.date() if offer.created_at else None
    )
    offer.items.clear()
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
    db.commit()
    db.refresh(offer)
    return offer


def delete_offer(db: Session, offer_id: uuid.UUID, subsidiary_id: str | None = None) -> bool:
    """Delete header and lines (items fall via ON DELETE CASCADE). False when missing/out of scope."""
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return False
    db.delete(offer)
    db.commit()
    return True


class BadStatus(Exception):
    """Domain error: unknown status value. Router maps it to 422."""

    def __init__(self, status: str):
        super().__init__(f"Unknown status: {status}")
        self.status = status


ALLOWED_STATUSES = ("Draft", "Pending response", "Finished", "Cancelled", "Rejected")


def set_offer_status(
    db: Session, offer_id: uuid.UUID, status: str, subsidiary_id: str | None = None
) -> Offer | None:
    """Change status (e.g. CLOSE OFFER -> Finished). None when missing/out of scope."""
    if status not in ALLOWED_STATUSES:
        raise BadStatus(status)
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return None
    offer.status = status
    db.commit()
    db.refresh(offer)
    return offer


def get_offer_document(db: Session, offer_id: uuid.UUID, subsidiary_id: str | None = None) -> OfferDocument | None:
    """Load the official document data (offer + customer + lines), or None."""
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return None
    customer = db.scalar(select(Customer).where(Customer.customer_id == offer.customer_id))
    if customer is None:
        return None
    return OfferDocument(
        offer_id=offer.id,
        number=offer.id_guardian_offer,
        offer_date=offer.offer_date or (offer.created_at.date() if offer.created_at else None),
        status=offer.status,
        language=offer.language or "Spanish",
        inspection_frequency=offer.inspection_frequency,
        responsible_person=offer.responsible_person,
        subsidiary_id=customer.subsidiary_id,
        account_name=customer.account_name,
        account_city=customer.city,
        account_province=customer.province,
        account_country=customer.country,
        currency=offer.currency,
        trip_cost=offer.trip_cost,
        diets=offer.diets,
        hotel_cost=offer.hotel_cost,
        trip_hours=offer.trip_hours,
        work_hours=offer.work_hours,
        bk_hours=offer.bk_hours,
        report_hours=offer.report_hours,
        total_hours=offer.total_hours,
        hours_import=offer.hours_import,
        expenses=offer.expenses,
        discount=offer.discount,
        bk_price=offer.bk_price,
        total=offer.total,
        total_end=offer.total_end,
        general_comments=offer.general_comments,
        lines=tuple(
            OfferLine(
                pos=item.row_no,
                equipment=item.equipment,
                description=item.description,
                import_amount=item.import_amount,
            )
            for item in sorted(offer.items, key=lambda i: i.row_no)
        ),
    )
