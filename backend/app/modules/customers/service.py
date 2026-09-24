"""Customer logic. Receives a Session, returns models. No HTTP here."""
from sqlalchemy import func, or_, select
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
    db: Session, limit: int = 50, offset: int = 0, subsidiary_id: str | None = None, search: str | None = None
) -> list[Customer]:
    """List with pagination, subsidiary scope and server-side search.

    None subsidiary = global, sees everything. Scoped callers see their
    subsidiary plus legacy rows without one (NULL). Search matches SAP id,
    account name or country (case-insensitive); None/blank disables it.
    """
    stmt = select(Customer).order_by(Customer.created_at.desc())
    stmt = _apply_filters(stmt, subsidiary_id=subsidiary_id, search=search)
    return list(db.scalars(stmt.limit(limit).offset(offset)))


def count_customers(db: Session, subsidiary_id: str | None = None, search: str | None = None) -> int:
    """Total rows matching the same filters (drives the UI pager)."""
    stmt = select(func.count()).select_from(Customer)
    stmt = _apply_filters(stmt, subsidiary_id=subsidiary_id, search=search)
    return db.scalar(stmt) or 0


def _apply_filters(stmt, subsidiary_id: str | None, search: str | None):
    if subsidiary_id is not None:
        stmt = stmt.where(or_(Customer.subsidiary_id == subsidiary_id, Customer.subsidiary_id.is_(None)))
    if search:
        like = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Customer.customer_id.ilike(like),
                Customer.account_name.ilike(like),
                Customer.country.ilike(like),
            )
        )
    return stmt


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
