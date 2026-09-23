"""Price logic. Read-only lookup by subsidiary."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.prices.models import PriceList
from app.modules.prices.schemas import PriceUpdate


def get_prices(db: Session, subsidiary_id: str) -> PriceList | None:
    """Fetch the rate row for a subsidiary, or None when not configured."""
    return db.scalar(select(PriceList).where(PriceList.subsidiary_id == subsidiary_id))


def update_prices(db: Session, subsidiary_id: str, data: PriceUpdate) -> PriceList | None:
    """Replace the whole rate row (admin config UI). None when missing: rows are seeded, never auto-created."""
    row = get_prices(db, subsidiary_id)
    if row is None:
        return None
    row.currency = data.currency
    row.km_rate = data.km_rate
    row.tech_rate = data.tech_rate
    row.diet_full_rate = data.diet_full_rate
    row.diet_half_rate = data.diet_half_rate
    row.hotel_rate = data.hotel_rate
    db.commit()
    db.refresh(row)
    return row
