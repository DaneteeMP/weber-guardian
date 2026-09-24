"""Equipment logic. Read-only: writes happen in the CSV import service."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.equipment.models import Equipment


def list_equipment(
    db: Session,
    customer_id: str | None = None,
    limit: int = 50,
    offset: int = 0,
    subsidiary_id: str | None = None,
) -> list[Equipment]:
    """List equipment with optional customer filter and subsidiary scope (None = global, strict)."""
    stmt = select(Equipment).order_by(Equipment.created_at.desc())
    if customer_id:
        stmt = stmt.where(Equipment.customer_id == customer_id)
    if subsidiary_id is not None:
        stmt = stmt.join(Customer, Equipment.customer_id == Customer.customer_id).where(
            Customer.subsidiary_id == subsidiary_id
        )
    return list(db.scalars(stmt.limit(limit).offset(offset)))
