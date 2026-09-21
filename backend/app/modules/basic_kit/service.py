"""Basic-kit logic. Read-only lookup by machine model (exact match)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.basic_kit.models import BasicKit


def get_kit(db: Session, model: str) -> BasicKit | None:
    """Fetch kit figures for a model, or None when the model has no kit."""
    return db.scalar(select(BasicKit).where(BasicKit.model == model))
