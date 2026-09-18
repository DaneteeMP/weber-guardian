"""Customer logic. Receives a Session, returns models. No HTTP here."""
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.customers.schemas import CustomerCreate


class CustomerAlreadyExists(Exception):
    """Domain error: customer_id already taken. Router maps it to HTTP 409."""

    def __init__(self, customer_id: str):
        super().__init__(f"Customer already exists: {customer_id}")
        self.customer_id = customer_id


def list_customers(db: Session, limit: int = 50, offset: int = 0) -> list[Customer]:
    """Simple list with minimal pagination (limit/offset). Nothing more in F0."""
    return list(db.scalars(select(Customer).order_by(Customer.created_at.desc()).limit(limit).offset(offset)))


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
