"""Machine-price logic. Lookup plus admin upsert/delete."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.machine_prices.models import MachinePrice
from app.modules.machine_prices.schemas import MachinePriceUpsert


def list_prices(db: Session, limit: int = 50, offset: int = 0) -> list[MachinePrice]:
    """List all machine prices, ordered by model."""
    return list(db.scalars(select(MachinePrice).order_by(MachinePrice.model).limit(limit).offset(offset)))


def get_price(db: Session, model: str) -> MachinePrice | None:
    """Fetch one model price, or None."""
    return db.scalar(select(MachinePrice).where(MachinePrice.model == model))


def upsert_price(db: Session, model: str, data: MachinePriceUpsert) -> MachinePrice:
    """Create or replace the model row (admin config UI)."""
    row = get_price(db, model)
    if row is None:
        row = MachinePrice(model=model, **data.model_dump())
        db.add(row)
    else:
        row.annual_price = data.annual_price
        row.inspections_per_year = data.inspections_per_year
        row.currency = data.currency
    db.commit()
    db.refresh(row)
    return row


def delete_price(db: Session, model: str) -> bool:
    """Remove a model row. False when missing."""
    row = get_price(db, model)
    if row is None:
        return False
    db.delete(row)
    db.commit()
    return True
