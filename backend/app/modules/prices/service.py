"""Price logic. Read-only lookup by subsidiary."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.prices.models import PriceList


def get_prices(db: Session, subsidiary_id: str) -> PriceList | None:
    """Fetch the rate row for a subsidiary, or None when not configured."""
    return db.scalar(select(PriceList).where(PriceList.subsidiary_id == subsidiary_id))
