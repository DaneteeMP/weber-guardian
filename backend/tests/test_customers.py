"""F0 tests: prove that service creates and lists. No API nor Postgres."""
import pytest

from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import CustomerAlreadyExists, count_customers, create_customer, list_customers


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


def test_search_matches_sap_name_and_country(db):
    create_customer(db, CustomerCreate(customer_id="EXT-001", account_name="Fricafort, S.L.", country="Spain"))
    create_customer(db, CustomerCreate(customer_id="EXT-002", account_name="Riela", country="Lithuania"))
    assert len(list_customers(db, search="fricafort")) == 1
    assert len(list_customers(db, search="EXT-002")) == 1
    assert len(list_customers(db, search="lithuania")) == 1
    assert len(list_customers(db, search="nope")) == 0
    assert count_customers(db, search="fricafort") == 1
    assert count_customers(db) == 2


def test_search_combines_with_scope_and_pagination(db):
    create_customer(
        db, CustomerCreate(customer_id="A-1", account_name="Alpha Foods", country="Spain", subsidiary_id="Weber Iberica")
    )
    create_customer(
        db, CustomerCreate(customer_id="A-2", account_name="Alpha Meats", country="Spain", subsidiary_id="Weber Iberica")
    )
    create_customer(
        db, CustomerCreate(customer_id="B-1", account_name="Alpha Berlin", country="Germany", subsidiary_id="Weber Germany")
    )
    assert count_customers(db, subsidiary_id="Weber Iberica", search="alpha") == 2
    page = list_customers(db, subsidiary_id="Weber Iberica", search="alpha", limit=1, offset=1)
    assert len(page) == 1
    assert count_customers(db, subsidiary_id="Weber Germany", search="alpha") == 1
