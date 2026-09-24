"""Basic-kit logic. Lookup plus admin create/delete (no updates: delete + recreate)."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.basic_kit.models import BasicKit
from app.modules.basic_kit.schemas import BasicKitCreate, BasicKitUpsert


class KitAlreadyExists(Exception):
    """Domain error: model already registered. Router maps it to 409."""

    def __init__(self, model: str):
        super().__init__(f"Kit already exists: {model}")
        self.model = model


def get_kit(db: Session, model: str) -> BasicKit | None:
    """Fetch kit figures for a model, or None when the model has no kit."""
    return db.scalar(select(BasicKit).where(BasicKit.model == model))


def list_kits(db: Session, limit: int = 50, offset: int = 0) -> list[BasicKit]:
    """List all kits, ordered by model (admin config table)."""
    return list(db.scalars(select(BasicKit).order_by(BasicKit.model).limit(limit).offset(offset)))


def create_kit(db: Session, data: BasicKitCreate) -> BasicKit:
    """Register a new kit. Commits explicitly, rolls back on duplicate."""
    row = BasicKit(**data.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise KitAlreadyExists(data.model) from None
    db.refresh(row)
    return row


def upsert_kit(db: Session, model: str, data: BasicKitUpsert) -> BasicKit:
    """Create or replace the kit row (admin config UI edit button)."""
    row = get_kit(db, model)
    if row is None:
        row = BasicKit(model=model, **data.model_dump())
        db.add(row)
    else:
        row.workload_basic_kit = data.workload_basic_kit
        row.spare_parts = data.spare_parts
    db.commit()
    db.refresh(row)
    return row


def delete_kit(db: Session, model: str) -> bool:
    """Remove a kit. False when missing."""
    row = get_kit(db, model)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True
