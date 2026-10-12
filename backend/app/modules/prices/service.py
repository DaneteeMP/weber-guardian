"""Price logic. Read-only lookup by subsidiary."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.prices.models import PriceList
from app.modules.prices.schemas import PriceUpdate
from app.modules.subsidiaries.models import Subsidiary


class PriceUpdateConflict(Exception):
    """Raised when a concurrent request creates the same subsidiary rate row."""


def get_prices(db: Session, subsidiary_id: str) -> PriceList | None:
    """Fetch the rate row for a subsidiary, or None when not configured."""
    return db.scalar(select(PriceList).where(PriceList.subsidiary_id == subsidiary_id))


def update_prices(db: Session, subsidiary_id: str, data: PriceUpdate) -> PriceList | None:
    """Create or replace one subsidiary's explicitly supplied rate row."""
    row = get_prices(db, subsidiary_id)
    if row is None:
        if db.get(Subsidiary, subsidiary_id) is None:
            return None
        row = PriceList(subsidiary_id=subsidiary_id, **data.model_dump())
        db.add(row)
    else:
        row.currency = data.currency
        row.km_rate = data.km_rate
        row.tech_rate = data.tech_rate
        row.diet_full_rate = data.diet_full_rate
        row.diet_half_rate = data.diet_half_rate
        row.hotel_rate = data.hotel_rate
        row.discount_rate = data.discount_rate
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise PriceUpdateConflict("Rates for this subsidiary were changed concurrently") from None
    db.refresh(row)
    return row
