"""Customer logic. Receives a Session, returns models. No HTTP here."""
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.modules.customers.models import Customer
from app.modules.customers.schemas import (
    CustomerComponentOut,
    CustomerCreate,
    CustomerDetailOut,
    CustomerMachineOut,
    CustomerOut,
)
from app.modules.equipment.models import CustomerSite, Equipment
from app.modules.equipment.schemas import CustomerSiteOut


class CustomerAlreadyExists(Exception):
    """Domain error: customer_id already taken. Router maps it to HTTP 409."""

    def __init__(self, customer_id: str):
        super().__init__(f"Customer already exists: {customer_id}")
        self.customer_id = customer_id


class OutsideScope(Exception):
    """Domain error: scoped caller creating outside its filial. Router maps it to 403."""

    def __init__(self, subsidiary_id: str | None):
        super().__init__(f"Cannot create outside subsidiary {subsidiary_id}")
        self.subsidiary_id = subsidiary_id


class CustomerNotFound(Exception):
    """Domain error: no customer with that SAP id. Router maps it to HTTP 404."""

    def __init__(self, customer_id: str):
        super().__init__(f"Customer not found: {customer_id}")
        self.customer_id = customer_id


class EquipmentWithoutMachine(Exception):
    """Domain error: an installed row with no equipment_name to group it under.

    equipment_name is nullable in the schema because machine-level SAP rows can
    arrive without a component breakdown. Those rows have no machine to hang
    off in the customer detail view, and dropping them would hide a machine
    nobody can see, so the view refuses instead of lying about the fleet size.
    """

    def __init__(self, customer_id: str, material_no: str | None):
        super().__init__(f"Equipment row without machine for customer {customer_id}: {material_no}")
        self.customer_id = customer_id
        self.material_no = material_no


def list_customers(
    db: Session, limit: int = 50, offset: int = 0, subsidiary_id: str | None = None, search: str | None = None
) -> list[Customer]:
    """List with pagination, subsidiary scope and server-side search.

    None subsidiary = global (admin), sees everything. Scoped callers see
    ONLY their subsidiary: untagged (NULL) rows stay visible to global
    users alone, so filials never leak into each other. Search matches SAP
    id, account name or country (case-insensitive); None/blank disables it.
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
        stmt = stmt.where(Customer.subsidiary_id == subsidiary_id)
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


def get_customer_detail(db: Session, customer_id: str, subsidiary_id: str | None = None) -> CustomerDetailOut:
    """Return one customer with its addresses and every machine it owns.

    Deliberately NOT paginated, unlike list_customers. Browsing the Clientes
    list is a paged concern; this is "everything this one customer has", and a
    single customer's fleet is bounded by the data, not by a UI choice: the
    largest is 262 machines, so a page size would only hide machines from the
    person choosing what to maintain. This is the bug that GET /equipment had
    with its default limit of 50 (202 customers were truncated).

    Machines are grouped by equipment_name because that is the key SAP repeats
    for every component installed on the same machine. Sites are read straight
    from customer_sites, not inferred from the equipment rows, so a customer
    with an address but no imported machine still shows where they are.

    Subsidiary scope is enforced by filtering the customer first: sites and
    equipment have no subsidiary column of their own, so reaching them without
    passing the customer check would leak another filial's fleet.
    """
    stmt = select(Customer).where(Customer.customer_id == customer_id)
    if subsidiary_id is not None:
        stmt = stmt.where(Customer.subsidiary_id == subsidiary_id)
    customer = db.scalar(stmt)
    if customer is None:
        raise CustomerNotFound(customer_id)

    sites = list(
        db.scalars(
            select(CustomerSite).where(CustomerSite.customer_id == customer_id).order_by(CustomerSite.created_at)
        )
    )

    rows = list(
        db.scalars(
            select(Equipment)
            .where(Equipment.customer_id == customer_id)
            .order_by(Equipment.equipment_name, Equipment.component_type, Equipment.material_no)
        )
    )

    machines: list[CustomerMachineOut] = []
    index: dict[str, CustomerMachineOut] = {}
    for row in rows:
        name = row.equipment_name
        if not name:
            # No machine to attach it to. equipment_name is nullable in the
            # schema, so this is possible even though the current Italy import
            # has none. Raising would break the whole detail view over one bad
            # row; skipping loses it silently. Neither is acceptable, so the
            # row is reported and the caller decides.
            raise EquipmentWithoutMachine(customer_id, row.material_no)
        machine = index.get(name)
        if machine is None:
            machine = CustomerMachineOut(
                equipment_name=name,
                machine_type=row.machine_type,
                site_id=row.site_id,
                components=[],
            )
            index[name] = machine
            machines.append(machine)
        machine.components.append(
            CustomerComponentOut(
                component_type=row.component_type,
                material_no=row.material_no,
                purchase_date=row.purchase_date,
            )
        )

    return CustomerDetailOut(
        customer=CustomerOut.model_validate(customer),
        sites=[CustomerSiteOut.model_validate(site) for site in sites],
        machines=machines,
    )


def create_customer(db: Session, data: CustomerCreate, scope_subsidiary: str | None = None) -> Customer:
    """Create one customer. Commits explicitly, rolls back on duplicate.

    Scoped callers land inside their own filial: an empty subsidiary
    defaults to it, a foreign one is rejected (403 at the router).
    """
    if scope_subsidiary is not None:
        if data.subsidiary_id and data.subsidiary_id != scope_subsidiary:
            raise OutsideScope(scope_subsidiary)
        data = data.model_copy(update={"subsidiary_id": scope_subsidiary})
    row = Customer(**data.model_dump())
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise CustomerAlreadyExists(data.customer_id) from None
    db.refresh(row)
    return row
