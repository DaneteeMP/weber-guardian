"""Distance logic. Read-only lookup by province (exact match)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.distances.models import Distance
from app.modules.distances.schemas import DistanceUpdate


def get_distance(db: Session, province: str) -> Distance | None:
    """Fetch travel figures for a province, or None when unknown (caller uses km 0)."""
    return db.scalar(select(Distance).where(Distance.province == province))


def list_distances(db: Session, limit: int = 50, offset: int = 0) -> list[Distance]:
    """List all provinces, ordered by name (admin config table)."""
    return list(db.scalars(select(Distance).order_by(Distance.province).limit(limit).offset(offset)))


def upsert_distance(db: Session, province: str, data: DistanceUpdate) -> Distance:
    """Create or replace the province row (admin config UI)."""
    row = get_distance(db, province)
    if row is None:
        row = Distance(province=province, km=data.km, trip_hours=data.trip_hours)
        db.add(row)
    else:
        row.km = data.km
        row.trip_hours = data.trip_hours
    db.commit()
    db.refresh(row)
    return row
