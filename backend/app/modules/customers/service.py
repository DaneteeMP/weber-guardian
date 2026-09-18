"""Customer logic. Receives a Session, returns models. No HTTP here."""
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.customers.schemas import CustomerCreate


class CustomerAlreadyExists(Exception):
    """Domain error: customer_id already taken. Router maps it to HTTP 409."""

    def __init__(self, customer_id: str):
        super().__init__(f"Customer already exists: {customer_id}")
        self.customer_id = customer_id


def list_customers(
    db: Session, limit: int = 50, offset: int = 0, subsidiary_id: str | None = None
) -> list[Customer]:
    """List with pagination and subsidiary scope. None = global, sees everything.

    Scoped callers see their subsidiary plus legacy rows without one (NULL).
    """
    stmt = select(Customer).order_by(Customer.created_at.desc())
    if subsidiary_id is not None:
        stmt = stmt.where(or_(Customer.subsidiary_id == subsidiary_id, Customer.subsidiary_id.is_(None)))
    return list(db.scalars(stmt.limit(limit).offset(offset)))


def create_customer(db: Session, data: CustomerCreate) -> Customer:
    """Create one customer. Commits explicitly, rolls back on duplicate."""
    row = Customer(**data.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CustomerAlreadyExists(data.customer_id) from None
    db.refresh(row)
    return row
