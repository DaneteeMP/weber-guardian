"""Subsidiary management tests: stats, unassigned, assignment. SQLite only."""
import pytest
from sqlalchemy import select

from app.modules.customers.models import Customer
from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import create_customer
from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry
from app.modules.subsidiaries.schemas import AssignCountriesIn, CountryAssignment
from app.modules.subsidiaries.service import (
    UnknownSubsidiary,
    assign_countries,
    auto_assign_all,
    stats,
    unassigned_countries,
)


def _seed(db):
    db.add_all(
        [
            Subsidiary(name="Weber Iberica", short_label="Iberica"),
            Subsidiary(name="Weber Partners", short_label="Partners"),
            SubsidiaryCountry(country="Spain", subsidiary="Weber Iberica"),
            SubsidiaryCountry(country="Zambia", subsidiary="Weber Iberica"),
        ]
    )
    create_customer(db, CustomerCreate(customer_id="A", account_name="A", country="Spain", subsidiary_id="Weber Iberica"))
    create_customer(db, CustomerCreate(customer_id="B", account_name="B", country="Zambia"))
    create_customer(db, CustomerCreate(customer_id="C", account_name="C", country="India"))
    db.commit()


def test_stats_counts(db):
    _seed(db)
    rows = {s.name: s for s in stats(db)}
    assert rows["Weber Iberica"].customers == 1
    assert rows["Weber Iberica"].countries == 2
    assert rows["Weber Partners"].customers == 0


def test_unassigned_lists_null_countries_by_volume(db):
    _seed(db)
    rows = unassigned_countries(db)
    assert {r.country for r in rows} == {"Zambia", "India"}
    assert all(r.count == 1 for r in rows)


def test_assign_moves_only_untagged(db):
    _seed(db)
    updated = assign_countries(
        db, AssignCountriesIn(assignments=[CountryAssignment(country="Zambia", subsidiary="Weber Iberica")])
    )
    assert updated == 1
    assert db.scalar(select(Customer).where(Customer.customer_id == "B")).subsidiary_id == "Weber Iberica"
    assert unassigned_countries(db) == [r for r in unassigned_countries(db) if r.country == "India"]


def test_assign_unknown_subsidiary_fails(db):
    _seed(db)
    with pytest.raises(UnknownSubsidiary):
        assign_countries(
            db, AssignCountriesIn(assignments=[CountryAssignment(country="India", subsidiary="Weber Mars")])
        )
    # Nothing moved on failure.
    assert db.scalar(select(Customer).where(Customer.customer_id == "C")).subsidiary_id is None


def test_auto_assign_all_redistributes_by_country(db):
    from app.modules.subsidiaries.models import Subsidiary, SubsidiaryCountry

    db.add(Subsidiary(name="Weber Iberica", short_label="Iberica"))
    db.add(Subsidiary(name="Weber Partners", short_label="Partners"))
    db.add(SubsidiaryCountry(country="Spain", subsidiary="Weber Iberica"))
    create_customer(db, CustomerCreate(customer_id="A", account_name="A", country="Spain", subsidiary_id="Weber Partners"))
    create_customer(db, CustomerCreate(customer_id="B", account_name="B", country="India"))
    db.commit()
    updated, warnings = auto_assign_all(db)
    assert updated == 1
    assert db.scalar(select(Customer).where(Customer.customer_id == "A")).subsidiary_id == "Weber Iberica"
    assert any("India" in w for w in warnings)
