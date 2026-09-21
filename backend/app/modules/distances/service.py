"""Distance logic. Read-only lookup by province (exact match)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.distances.models import Distance


def get_distance(db: Session, province: str) -> Distance | None:
    """Fetch travel figures for a province, or None when unknown (caller uses km 0)."""
    return db.scalar(select(Distance).where(Distance.province == province))
