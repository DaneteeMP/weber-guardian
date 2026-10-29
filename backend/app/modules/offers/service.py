"""Offer logic. Receives a Session, returns models. No HTTP here."""
import uuid
from datetime import date, datetime
from decimal import Decimal, ROUND_DOWN, ROUND_FLOOR

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.modules.customers.models import Customer
from app.modules.equipment.models import CustomerSite, Equipment
from app.modules.offers.document import BandRate, CustomAnnex, OfferDocument, OfferLine
from app.modules.offers.models import Offer, OfferItem
from app.modules.offers.pricing_engine import PricingInput, calculate
from app.modules.offers.schemas import (
    OfferCalculateIn,
    OfferCalculateOut,
    OfferCreate,
    OfferDocumentSettingsIn,
    OfferUpdate,
    document_guardian_selections,
)
from app.modules.prices.service import get_prices


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


def distribute_costs(gross: Decimal, items: list) -> list[Decimal]:
    """Spread the gross amount over the module lines (legacy "RepartirCostes").

    The legacy did not price every module on its own: it spread the total
    of the offer over the lines, proportionally to their hours, so the annex
    adds up with the header. Each line gets a share of the gross; the shares
    are rounded to cents and the leftover cents go to the lines with the
    largest remaining fraction, so the sum is exactly the gross.

    The key is the workload of the line. Lines without hours get no share:
    they are rows nobody has priced yet, and the legacy flagged them for
    review instead of giving them a made up amount.
    """
    if not items:
        return []
    weights = [Decimal(str(item.workload or 0)) for item in items]
    total_weight = sum(weights)
    if total_weight <= 0:
        # Nothing has hours: the whole gross goes to the first line, the
        # rest stay at zero.
        shares = [Decimal("0.00") for _ in items]
        shares[0] = gross.quantize(Decimal("0.01"))
        return shares

    exact = [gross * weight / total_weight for weight in weights]
    shares = [share.quantize(Decimal("0.01"), rounding=ROUND_DOWN) for share in exact]
    leftover = gross - sum(shares)
    # Largest remainder first: the lines that lost the most to the rounding
    # get the leftover cents back.
    order = sorted(
        range(len(items)),
        key=lambda index: (exact[index] - shares[index], -index),
        reverse=True,
    )
    cents = int((leftover * 100).to_integral_value(rounding=ROUND_FLOOR))
    for step in range(cents):
        shares[order[step % len(order)]] += Decimal("0.01")
    return shares


def calculate_price(data: OfferCalculateIn) -> OfferCalculateOut:
    """Dry-run: run the engine without touching the DB."""
    # audit excludes the basic kit, off_guardian excludes the branch discount.
    basic_kit = data.basic_kit and data.offer_type != "audit"
    apply_discount = data.offer_type != "off_guardian"
    # Legacy rule: 2 report hours per inspected machine (Actualizar-
    # ListadoMaquinas). Never taken from the client payload.
    report_hours = Decimal(data.equipment_count * 2)
    out = calculate(
        PricingInput(
            work_hours=data.work_hours,
            bk_hours=data.bk_hours,
            report_hours=report_hours,
            trip_hours_base=data.trip_hours_base,
            km=data.km,
            km_rate=data.km_rate,
            tech_rate=data.tech_rate,
            diet_full_rate=data.diet_full_rate,
            diet_half_rate=data.diet_half_rate,
            hotel_rate=data.hotel_rate,
            discount_rate=data.discount_rate,
            basic_kit=basic_kit,
            apply_discount=apply_discount,
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
        line_amounts=distribute_costs(out.total, data.items),
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


def _price_with_items(pricing: OfferCalculateIn, items: list) -> OfferCalculateOut:
    """Price a stored offer: the saved items are the truth for machine count.

    The request's equipment_count only feeds the dry-run preview; persistence
    never trusts it, so the derived report hours always match the lines.
    """
    count = len({item.equipment for item in items if item.equipment})
    return calculate_price(pricing.model_copy(update={"equipment_count": count}))


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

    priced = _price_with_items(data.pricing, data.items)
    number = data.id_guardian_offer or _fallback_number()
    # A missing offer_date means "same day as the row was created": the PDF and
    # the home fall back to created_at, so the business date is never invented.
    offer_date = data.offer_date or date.today()

    offer = Offer(
        id_guardian_offer=number,
        customer_id=data.customer_id,
        status=data.status,
        offer_type=data.pricing.offer_type,
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
        guardian_selections=list(data.guardian_selections),
        custom_annexes=[annex.model_dump() for annex in data.custom_annexes],
        created_by=created_by,
        offer_date=offer_date,
    )
    # The lines carry the gross amount spread over them (legacy
    # "RepartirCostes"), so the annex adds up with the header.
    line_amounts = distribute_costs(priced.total, data.items)
    for pos, item in enumerate(data.items, start=1):
        offer.items.append(
            OfferItem(
                row_no=pos,
                equipment=item.equipment,
                description=item.description,
                import_amount=line_amounts[pos - 1],
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


STATUS_ORDER = (
    "Pending response",
    "Cancelled",
    "Accepted",
    "Pending Service",
    "In progress",
    "Pending invoicing",
    "Finished",
)

# Open offers: everything that still needs a commercial or operational action.
# Finished, Cancelled and Rejected are terminal and excluded from "pending".
PENDING_STATUSES = frozenset(
    {
        "Pending response",
        "Accepted",
        "Pending Service",
        "In progress",
        "Pending invoicing",
    }
)


def offers_summary(db: Session, subsidiary_id: str | None = None) -> dict:
    """Dashboard aggregates, all through the subsidiary scope.

    One query feeds every panel: customer lists, pending/realized splits,
    status boards, monthly bars, area performance and the ranking. The rows
    are aggregated in Python because the dashboard also needs the latest
    customer/status pair, which is awkward to express in a single grouped
    query without losing readability.
    """
    stmt = (
        select(
            Offer.id,
            Offer.customer_id,
            Customer.account_name,
            Customer.country,
            Offer.status,
            Offer.total_end,
            Offer.offer_date,
            Offer.created_at,
        )
        .join(Customer, Offer.customer_id == Customer.customer_id)
        .order_by(Offer.offer_date.desc().nullslast(), Offer.created_at.desc())
    )
    if subsidiary_id is not None:
        stmt = stmt.where(Customer.subsidiary_id == subsidiary_id)
    rows = db.execute(stmt).all()

    def add_customer(
        bucket: dict[str, dict],
        offer_id: uuid.UUID,
        customer_id: str,
        account_name: str | None,
        amount: Decimal,
        day: date | None,
        status: str,
    ) -> None:
        row = bucket.get(customer_id)
        if row is None:
            row = {
                "customer_id": customer_id,
                "account_name": account_name or customer_id,
                "count": 0,
                "total_end": Decimal("0"),
                "last_offer_id": str(offer_id),
                "last_offer_date": day,
                "last_status": status,
            }
            bucket[customer_id] = row
        row["count"] += 1
        row["total_end"] += amount

    def ordered(bucket: dict[str, dict]) -> list[dict]:
        return sorted(
            bucket.values(),
            key=lambda row: (-row["count"], -row["total_end"], row["account_name"].lower()),
        )

    customers: dict[str, dict] = {}
    pending_customers: dict[str, dict] = {}
    realized_customers: dict[str, dict] = {}
    status_customers: dict[str, dict[str, dict]] = {
        status: {} for status in STATUS_ORDER
    }
    area_totals: dict[str, dict] = {}
    monthly_counts: dict[str, int] = {}
    status_counts: dict[str, int] = {}
    status_amounts: dict[str, Decimal] = {}
    total = 0

    for offer_id, customer_id, account_name, country, status, total_end, offer_date, created_at in rows:
        total += 1
        amount = total_end or Decimal("0")
        day = offer_date or (created_at.date() if created_at else None)

        month = day.strftime("%Y-%m") if day else "unknown"
        monthly_counts[month] = monthly_counts.get(month, 0) + 1

        add_customer(customers, offer_id, customer_id, account_name, amount, day, status)
        status_counts[status] = status_counts.get(status, 0) + 1
        status_amounts[status] = status_amounts.get(status, Decimal("0")) + amount
        status_customers.setdefault(status, {})
        add_customer(status_customers[status], offer_id, customer_id, account_name, amount, day, status)

        if status in PENDING_STATUSES:
            add_customer(pending_customers, offer_id, customer_id, account_name, amount, day, status)
        if status == "Finished":
            add_customer(realized_customers, offer_id, customer_id, account_name, amount, day, status)

        area = (country or "").strip() or "Unknown"
        area_row = area_totals.get(area)
        if area_row is None:
            area_row = {"area": area, "count": 0, "total_end": Decimal("0")}
            area_totals[area] = area_row
        area_row["count"] += 1
        area_row["total_end"] += amount

    extra_statuses = [status for status in status_counts if status not in STATUS_ORDER]
    ordered_statuses = [*STATUS_ORDER, *extra_statuses]

    by_status = [
        {"status": status, "count": status_counts[status]}
        for status in ordered_statuses
        if status_counts.get(status, 0) > 0
    ]
    status_details = [
        {
            "status": status,
            "count": status_counts.get(status, 0),
            "total_end": status_amounts.get(status, Decimal("0")),
            "customers": ordered(status_customers.get(status, {}))[:20],
        }
        for status in ordered_statuses
    ]

    ranking = ordered(customers)[:15]
    by_area = sorted(
        area_totals.values(),
        key=lambda row: (-row["total_end"], row["area"].lower()),
    )

    # Customers that exist in the scope but still have no offer. They are the
    # commercial follow-up list, so they are returned alphabetically and
    # without the offer rollup fields.
    customer_stmt = select(Customer.customer_id, Customer.account_name).order_by(
        Customer.account_name
    )
    if subsidiary_id is not None:
        customer_stmt = customer_stmt.where(Customer.subsidiary_id == subsidiary_id)
    all_customers = db.execute(customer_stmt).all()
    customers_with_offers = set(customers)
    customers_without_offers = [
        {
            "customer_id": customer_id,
            "account_name": account_name,
            "count": 0,
            "total_end": Decimal("0"),
            "last_offer_id": None,
            "last_offer_date": None,
            "last_status": None,
        }
        for customer_id, account_name in all_customers
        if customer_id not in customers_with_offers
    ]

    return {
        "total": total,
        "by_status": by_status,
        "status_details": status_details,
        "monthly": [
            {"month": month, "count": monthly_counts[month]}
            for month in sorted(monthly_counts)
        ],
        "ranking": ranking,
        "customers_total": len(all_customers),
        "customers": ordered(customers)[:20],
        "customers_with_offers_total": len(customers),
        "customers_without_offers_total": len(customers_without_offers),
        "customers_without_offers": customers_without_offers,
        "pending_total": sum(status_counts.get(status, 0) for status in PENDING_STATUSES),
        "pending_customers": ordered(pending_customers)[:20],
        "realized_total": status_counts.get("Finished", 0),
        "realized_customers": ordered(realized_customers)[:20],
        "by_area": by_area,
    }


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
    priced = _price_with_items(data.pricing, data.items)
    offer.status = data.status
    offer.offer_type = data.pricing.offer_type
    offer.responsible_person = data.responsible_person
    if data.language is not None:
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
    offer.guardian_selections = list(data.guardian_selections)
    # custom_annexes=None on a full edit means "not sent by this form": the
    # annexes belong to the print modal and must survive unrelated edits.
    if data.custom_annexes is not None:
        offer.custom_annexes = [annex.model_dump() for annex in data.custom_annexes]
    # offer_date=None means "keep the day the row was created", so an edit that
    # does not touch the date can never wipe it.
    offer.offer_date = data.offer_date or offer.offer_date or (
        offer.created_at.date() if offer.created_at else None
    )
    offer.items.clear()
    # Same rule as on create: the lines carry the gross amount spread over
    # them (legacy "RepartirCostes").
    line_amounts = distribute_costs(priced.total, data.items)
    for pos, item in enumerate(data.items, start=1):
        offer.items.append(
            OfferItem(
                row_no=pos,
                equipment=item.equipment,
                description=item.description,
                import_amount=line_amounts[pos - 1],
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


ALLOWED_STATUSES = (
    "Pending response",
    "Accepted",
    "In progress",
    "Pending invoicing",
    "Finished",
    "Rejected",
    "Cancelled",
    "Pending Service",
)


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


def patch_document_settings(
    db: Session, offer_id: uuid.UUID, data: OfferDocumentSettingsIn, subsidiary_id: str | None = None
) -> Offer | None:
    """Partial update of the print settings (Print PDF modal auto-save).

    Only the provided fields change (scope, contract language, custom
    annexes), in one transaction. None when missing/out of scope.
    """
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return None
    if data.guardian_selections is not None:
        offer.guardian_selections = list(data.guardian_selections)
    if data.language is not None:
        offer.language = data.language
    if data.custom_annexes is not None:
        offer.custom_annexes = [annex.model_dump() for annex in data.custom_annexes]
    db.commit()
    db.refresh(offer)
    return offer


class TooManyAnnexes(Exception):
    """The annex list already holds the maximum number of entries."""


def append_custom_annex(
    db: Session,
    offer_id: uuid.UUID,
    title: str,
    body_html: str,
    subsidiary_id: str | None = None,
) -> Offer | None:
    """Append one parsed .docx annex to the offer's custom annexes.

    Single transaction: the offer is updated only if the annex count is
    within the same limit the PATCH endpoint enforces (10). The annex is
    stored with an empty plain-text body: the renderer prefers body_html
    when both are present.
    """
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return None
    annexes = list(offer.custom_annexes or [])
    if len(annexes) >= 10:
        raise TooManyAnnexes("An offer can hold at most 10 custom annexes.")
    annexes.append({"title": title, "body": "", "body_html": body_html})
    offer.custom_annexes = annexes
    db.commit()
    db.refresh(offer)
    return offer


def _band_rates_for(db: Session, subsidiary_id: str | None) -> tuple[BandRate, ...]:
    """Customer-facing band rates for the subsidiary, or () when unconfigured.

    The PDF omits the whole rates block unless all three bands are set.
    """
    if subsidiary_id is None:
        return ()
    row = get_prices(db, subsidiary_id)
    if row is None:
        return ()
    bands = (
        (1, row.band1_rate_without, row.band1_rate_with),
        (2, row.band2_rate_without, row.band2_rate_with),
        (3, row.band3_rate_without, row.band3_rate_with),
    )
    if any(without is None or with_ is None for _, without, with_ in bands):
        return ()
    return tuple(
        BandRate(band=band, rate_without_contract=without, rate_with_contract=with_)
        for band, without, with_ in bands
    )


def get_offer_document(db: Session, offer_id: uuid.UUID, subsidiary_id: str | None = None) -> OfferDocument | None:
    """Load the official document data (offer + customer + lines), or None."""
    offer = get_offer(db, offer_id, subsidiary_id=subsidiary_id)
    if offer is None:
        return None
    customer = db.scalar(select(Customer).where(Customer.customer_id == offer.customer_id))
    if customer is None:
        return None
    items = sorted(offer.items, key=lambda item: item.row_no)
    equipment_names = {item.equipment for item in items if item.equipment}
    sites = []
    if equipment_names:
        sites = list(
            db.scalars(
                select(CustomerSite)
                .join(Equipment, Equipment.site_id == CustomerSite.id)
                .where(
                    Equipment.customer_id == offer.customer_id,
                    Equipment.equipment_name.in_(equipment_names),
                )
                .order_by(CustomerSite.physical_city, CustomerSite.physical_street)
            ).unique()
        )
    site_addresses = []
    for site in sites:
        address = ", ".join(
            value
            for value in (
                site.physical_street,
                " ".join(
                    value for value in (site.physical_postal_code, site.physical_city) if value
                ),
                site.physical_province,
                site.physical_country,
            )
            if value
        )
        if address and address not in site_addresses:
            site_addresses.append(address)
    return OfferDocument(
        offer_id=offer.id,
        number=offer.id_guardian_offer,
        offer_date=offer.offer_date or (offer.created_at.date() if offer.created_at else None),
        status=offer.status,
        offer_type=offer.offer_type,
        band_rates=_band_rates_for(db, customer.subsidiary_id),
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
        guardian_selections=tuple(
            document_guardian_selections(offer.guardian_selections or [], offer.offer_type)
        ),
        custom_annexes=tuple(
            CustomAnnex(
                title=annex["title"],
                body=annex.get("body", ""),
                body_html=annex.get("body_html"),
            )
            for annex in (offer.custom_annexes or [])
        ),
        customer_number=customer.customer_id,
        customer_site="; ".join(site_addresses) or None,
        lines=tuple(
            OfferLine(
                pos=item.row_no,
                equipment=item.equipment,
                description=item.description,
                import_amount=item.import_amount,
            )
            for item in items
        ),
    )
