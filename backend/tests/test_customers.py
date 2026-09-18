"""F0 tests: prove that service creates and lists. No API nor Postgres."""
import pytest

from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import CustomerAlreadyExists, create_customer, list_customers


def test_create_and_list(db):
    create_customer(db, CustomerCreate(customer_id="EXT-001", account_name="Fricafort, S.L.", country="Spain"))
    rows = list_customers(db)
    assert len(rows) == 1
    assert rows[0].customer_id == "EXT-001"
    # Internal PK exists and differs from the external ID
    assert rows[0].id is not None
    assert str(rows[0].id) != "EXT-001"


def test_duplicate_customer_id_raises_domain_error(db):
    """Duplicate customer_id must raise a domain error, not a raw DB error."""
    create_customer(db, CustomerCreate(customer_id="EXT-001", account_name="First"))
    with pytest.raises(CustomerAlreadyExists):
        create_customer(db, CustomerCreate(customer_id="EXT-001", account_name="Second"))
    # Session stays usable after rollback, only the first row exists.
    rows = list_customers(db)
    assert len(rows) == 1
    assert rows[0].account_name == "First"
