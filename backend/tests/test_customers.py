"""F0 tests: prove that service creates and lists. No API nor Postgres."""
import pytest

from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import (
    CustomerAlreadyExists,
    CustomerNotFound,
    EquipmentWithoutMachine,
    count_customers,
    create_customer,
    get_customer_detail,
    list_customers,
)
from app.modules.equipment.models import CustomerSite, Equipment, row_hash_of, site_hash_of


def test_create_and_list(db):
    create_customer(db, CustomerCreate(customer_id="EXT-001", account_name="Fricafort, S.L.", country="Spain"))
    rows = list_customers(db)
    assert len(rows) == 1
    assert rows[0].customer_id == "EXT-001"
    # Internal PK exists and differs from the external ID
    assert rows[0].id is not None
    assert str(rows[0].id) != "EXT-001"


def test_customer_id_is_zero_padded_to_sap_form(db):
    """Numeric SAP Debitors are stored zero-padded to 10 digits, so "1052152"
    and "0001052152" can never become two customers for the same company."""
    row = create_customer(db, CustomerCreate(customer_id="1052152", account_name="Rosso S.p.A."))
    assert row.customer_id == "0001052152"
    with pytest.raises(CustomerAlreadyExists):
        create_customer(db, CustomerCreate(customer_id="0001052152", account_name="Rosso S.p.A."))
    assert count_customers(db) == 1


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

def _seed_customer_with_fleet(db, customer_id="EXT-001", account_name="Fricafort, S.L.", subsidiary_id=None):
    """One customer, one address, and machines made of several component rows."""
    create_customer(
        db,
        CustomerCreate(customer_id=customer_id, account_name=account_name, country="Italy", subsidiary_id=subsidiary_id),
    )
    site_hash = site_hash_of(customer_id, "Via Emilia, 129", "Fontanellato", "43012", "Parma", "Italy")
    site = CustomerSite(
        customer_id=customer_id,
        site_hash=site_hash,
        physical_street="Via Emilia, 129",
        physical_city="Fontanellato",
        physical_postal_code="43012",
        physical_province="Parma",
        physical_country="Italy",
    )
    db.add(site)
    db.flush()
    rows = [
        ("302-435 MLC", "CCS302", "Slicer", "CCS 302-435"),
        ("302-435 MLC", "CCS302", "Checkweigher", "CCW-3435"),
        ("602-837 MLC", "CCS602", "Slicer", "CCS 602-837"),
    ]
    for name, machine_type, component_type, material_no in rows:
        db.add(
            Equipment(
                customer_id=customer_id,
                equipment_name=name,
                machine_type=machine_type,
                component_type=component_type,
                material_no=material_no,
                purchase_date="",
                site_id=site.id,
                row_hash=row_hash_of(customer_id, name, machine_type, component_type, material_no, "", site_hash),
            )
        )
    db.commit()
    return site


def test_customer_detail_returns_address_and_machines_grouped(db):
    """The Clientes tab needs the address plus one entry per machine, not per component row."""
    _seed_customer_with_fleet(db)

    detail = get_customer_detail(db, "EXT-001")

    assert detail.customer.account_name == "Fricafort, S.L."
    assert len(detail.sites) == 1
    assert detail.sites[0].physical_province == "Parma"
    assert detail.sites[0].physical_postal_code == "43012"
    # Two machines, not the three component rows.
    assert [m.equipment_name for m in detail.machines] == ["302-435 MLC", "602-837 MLC"]
    # The machine's own row sits beside its modules under the same heading.
    first = detail.machines[0]
    assert first.machine_type == "CCS302"
    assert [(c.component_type, c.material_no) for c in first.components] == [
        ("Checkweigher", "CCW-3435"),
        ("Slicer", "CCS 302-435"),
    ]


def test_customer_detail_is_not_truncated(db):
    """Regression: GET /equipment capped at 50 rows, hiding 104 of 154 machines.

    The customer view must return the whole fleet, because it feeds the choice
    of what to maintain. A real customer (Agricola Tre Valli) owns 262 rows.
    """
    create_customer(db, CustomerCreate(customer_id="BIG-1", account_name="Agricola Tre Valli"))
    for i in range(154):
        db.add(
            Equipment(
                customer_id="BIG-1",
                equipment_name=f"M-{i:03d}",
                machine_type="CCS302",
                component_type="Slicer",
                material_no=f"CCS 302-{i:03d}",
                row_hash=row_hash_of("BIG-1", f"M-{i:03d}", "CCS302", "Slicer", f"CCS 302-{i:03d}", ""),
            )
        )
    db.commit()

    detail = get_customer_detail(db, "BIG-1")

    assert len(detail.machines) == 154


def test_customer_detail_without_equipment_or_address(db):
    """Half the Italian customers have an address but no imported machine, and the reverse exists too."""
    create_customer(db, CustomerCreate(customer_id="EMPTY-1", account_name="No Fleet Yet", country="Italy"))

    detail = get_customer_detail(db, "EMPTY-1")

    assert detail.machines == []
    assert detail.sites == []


def test_customer_detail_unknown_customer_raises_domain_error(db):
    with pytest.raises(CustomerNotFound):
        get_customer_detail(db, "NOPE")


def test_customer_detail_refuses_equipment_row_without_machine(db):
    """A row with no equipment_name would silently shrink the fleet count, so it must not."""
    create_customer(db, CustomerCreate(customer_id="ORPHAN-1", account_name="Broken Row"))
    db.add(
        Equipment(
            customer_id="ORPHAN-1",
            equipment_name=None,
            machine_type=None,
            component_type="Checkweigher",
            material_no="CCW-3435",
            row_hash=row_hash_of("ORPHAN-1", None, None, "Checkweigher", "CCW-3435", ""),
        )
    )
    db.commit()

    with pytest.raises(EquipmentWithoutMachine) as exc:
        get_customer_detail(db, "ORPHAN-1")
    assert exc.value.material_no == "CCW-3435"


def test_customer_detail_respects_subsidiary_scope(db):
    """customer_sites and equipment carry no subsidiary, so the customer check is the only gate."""
    _seed_customer_with_fleet(db, customer_id="ES-1", account_name="Fricafort, S.L.", subsidiary_id="Weber Iberica")
    _seed_customer_with_fleet(db, customer_id="IT-1", account_name="Erre Italia S.r.l.", subsidiary_id="Weber Italy")

    # The Italy caller cannot read the Iberica customer's fleet.
    with pytest.raises(CustomerNotFound):
        get_customer_detail(db, "ES-1", subsidiary_id="Weber Italy")

    # A global caller (subsidiary_id None) sees both.
    assert get_customer_detail(db, "ES-1").customer.customer_id == "ES-1"
    assert get_customer_detail(db, "IT-1", subsidiary_id="Weber Italy").customer.customer_id == "IT-1"
