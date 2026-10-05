"""Maintenance draft tests: amounts are workload × the customer's branch rate.

Every rule here protects one business invariant: the server computes the money
with Decimal from verified hours, and anything it cannot verify arrives flagged
for a human instead of silently priced at zero.
"""
from itertools import count
from decimal import Decimal

import pytest

from app.modules.component_names.models import ComponentName, ComponentWorkload
from app.modules.customers.models import Customer
from app.modules.customers.service import CustomerNotFound
from app.modules.equipment.models import Equipment
from app.modules.equipment_catalog.schemas import EquipmentCatalogEntryIn
from app.modules.equipment_catalog.service import create_entry
from app.modules.offers.maintenance import RateNotConfigured, maintenance_draft
from app.modules.prices.models import PriceList


@pytest.fixture
def italy_customer(db):
    customer = Customer(
        customer_id="1050258", account_name="Agricola Tre Valli", subsidiary_id="Weber Italy"
    )
    db.add(customer)
    db.add(
        PriceList(
            subsidiary_id="Weber Italy",
            currency="EUR",
            tech_rate=Decimal("58.00"),
        )
    )
    db.commit()
    return customer


def _equipment(db, customer_id: str, name: str, **over) -> Equipment:
    row = Equipment(
        customer_id=customer_id,
        equipment_name=name,
        machine_type=over.get("machine_type", "CCS602"),
        component_type=over.get("component_type"),
        material_no=over.get("material_no"),
        row_hash=over.get("row_hash", f"hash-{next(_equipment.counter)}"),
    )
    db.add(row)
    db.commit()
    return row


_equipment.counter = count()


def _confirmed_line(db, label: str = "602", machine_type: str = "CCS602", workload: str = "3.0"):
    return create_entry(
        db,
        EquipmentCatalogEntryIn(
            kind="line",
            label=label,
            workload=Decimal(workload),
            matches=[{"match_field": "machine_type", "match_value": machine_type, "is_confirmed": True}],
        ),
    )


def _dictionary(
    db,
    material_no: str,
    type_code: str | None,
    name: str = "Checkweigher",
    component_type: str = "Checkweigher",
):
    db.add(
        ComponentName(
            material_no=material_no,
            name_en=name,
            type_code=type_code,
            component_type=component_type,
        )
    )
    db.commit()


def _workload(
    db,
    source_key: str,
    name: str,
    component_type: str,
    workload: str | None,
    *,
    needs_review: bool = False,
):
    db.add(
        ComponentWorkload(
            source_key=source_key,
            name=name,
            component_type=component_type,
            workload=Decimal(workload) if workload else None,
            needs_review=needs_review or workload is None,
        )
    )
    db.commit()


def test_line_amount_is_workload_times_the_subsidiary_rate(db, italy_customer):
    _confirmed_line(db, workload="3.0")
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCS 602-750")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    line = draft.rows[0]
    assert line.kind == "line"
    assert line.description == "602"
    assert line.workload == Decimal("3.0")
    # 3.0 h × 58.00 €/h = 174.00, computed server-side.
    assert line.amount == Decimal("174.00")
    assert line.match_state == "confirmed"
    assert line.needs_review is False


def test_modules_resolve_through_the_dictionary_and_collapse_duplicates(db, italy_customer):
    _confirmed_line(db)
    _dictionary(db, "CCW05001", "CCW")
    _workload(db, "component:checkweigher", "Checkweigher", "Checkweigher", "1.5")
    # The same part installed twice on one machine must not be priced twice.
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCW05001", component_type="Checkweigher")
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCW05001", component_type="Checkweigher")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    modules = [row for row in draft.rows if row.kind == "module"]
    assert len(modules) == 1
    assert modules[0].description == "Checkweigher"
    assert modules[0].type_code == "CCW"
    assert modules[0].workload == Decimal("1.5")
    assert modules[0].amount == Decimal("87.00")


def test_material_the_dictionary_does_not_know_is_flagged_not_priced(db, italy_customer):
    _confirmed_line(db)
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="ZZZ-UNKNOWN", component_type="Mystery")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    module = draft.rows[1]
    assert module.kind == "module"
    assert module.match_state == "unknown"
    assert module.workload is None
    assert module.amount == Decimal("0.00")
    assert module.needs_review is True
    # A flagged row must not hide inside the totals: only the confirmed line
    # (3.0 h × 58 €) contributes, the unknown module adds nothing.
    assert draft.total_amount == Decimal("174.00")
    assert draft.total_workload == Decimal("3.0")


def test_code_without_a_seeded_workload_is_flagged_not_priced(db, italy_customer):
    _confirmed_line(db)
    _dictionary(
        db,
        "SLI06001",
        "SLI",
        name="Slicer 600",
        component_type="Slicer",
    )  # dictionary knows the code, workload missing
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="SLI06001")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    module = draft.rows[1]
    assert module.type_code == "SLI"
    assert module.workload is None
    assert module.needs_review is True
    assert module.amount == Decimal("0.00")


def test_slicer_model_uses_its_canonical_product_workload(db, italy_customer):
    _confirmed_line(db)
    _dictionary(
        db,
        "CCS04051",
        "CCS",
        name="Slicer 405-Extended",
        component_type="Slicer",
    )
    _workload(
        db,
        "slicer:slicer 405",
        "Slicer 405",
        "Slicer",
        "4.0",
    )
    _equipment(
        db,
        italy_customer.customer_id,
        "602-750 MCS",
        material_no="CCS04051-10591",
        component_type="Slicer",
    )

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    slicer = next(row for row in draft.rows if row.kind == "module")
    assert slicer.description == "Slicer 405"
    assert slicer.workload == Decimal("4.0")
    assert slicer.amount == Decimal("232.00")
    assert slicer.needs_review is False


def test_ambiguous_slicer_accessory_is_not_associated_to_a_model(db, italy_customer):
    _confirmed_line(db)
    _dictionary(
        db,
        "CCS03002",
        "CCS",
        name="CCS 302 | accessories",
        component_type="Slicer",
    )
    _equipment(
        db,
        italy_customer.customer_id,
        "602-750 MCS",
        material_no="CCS03002-10001",
        component_type="Slicer",
    )

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    slicer = next(row for row in draft.rows if row.kind == "module")
    assert slicer.description == "CCS 302 | accessories"
    assert slicer.workload is None
    assert slicer.amount == Decimal("0.00")
    assert slicer.needs_review is True


def test_unconfirmed_line_shows_its_hours_but_is_flagged(db, italy_customer):
    # Same entry, match left unconfirmed: an administrator still has to
    # validate the code, but the hours are probably right and are shown.
    create_entry(
        db,
        EquipmentCatalogEntryIn(
            kind="line",
            label="602",
            workload=Decimal("3.0"),
            matches=[{"match_field": "machine_type", "match_value": "CCS602", "is_confirmed": False}],
        ),
    )
    _equipment(db, italy_customer.customer_id, "602-750 MCS")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    line = draft.rows[0]
    assert line.match_state == "unconfirmed"
    assert line.needs_review is True
    assert line.amount == Decimal("174.00")


def test_machine_without_catalog_match_gets_an_unknown_line_row(db, italy_customer):
    _equipment(db, italy_customer.customer_id, "Mystery machine", machine_type="XXX999")

    draft = maintenance_draft(db, italy_customer.customer_id, ["Mystery machine"])

    line = draft.rows[0]
    assert line.match_state == "unknown"
    assert line.workload is None
    assert line.amount == Decimal("0.00")
    assert line.needs_review is True


def test_totals_sum_the_priced_rows_only(db, italy_customer):
    _confirmed_line(db, workload="3.0")
    _dictionary(db, "CCW05001", "CCW")
    _workload(db, "component:checkweigher", "Checkweigher", "Checkweigher", "1.5")
    _dictionary(db, "ZZZUNKNOWN", None)
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCW05001")
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="ZZZ-UNKNOWN")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    assert draft.total_workload == Decimal("4.5")
    assert draft.total_amount == Decimal("261.00")
    assert draft.currency == "EUR"
    assert draft.tech_rate == Decimal("58.00")


def test_scoped_caller_cannot_draft_another_filials_customer(db, italy_customer):
    _confirmed_line(db)
    _equipment(db, italy_customer.customer_id, "602-750 MCS")

    with pytest.raises(CustomerNotFound):
        maintenance_draft(
            db, italy_customer.customer_id, ["602-750 MCS"], scope_subsidiary_id="Weber Iberica"
        )


def test_missing_rate_row_raises_rate_not_configured(db):
    customer = Customer(customer_id="9999999", account_name="No rates yet", subsidiary_id="Weber Nowhere")
    db.add(customer)
    db.commit()
    _equipment(db, customer.customer_id, "602-750 MCS")

    with pytest.raises(RateNotConfigured):
        maintenance_draft(db, customer.customer_id, ["602-750 MCS"])


def test_unknown_customer_raises_customer_not_found(db):
    with pytest.raises(CustomerNotFound):
        maintenance_draft(db, "NO-SUCH-CUSTOMER", ["602-750 MCS"])


def test_selected_machines_come_out_in_the_requested_order(db, italy_customer):
    _confirmed_line(db)
    _equipment(db, italy_customer.customer_id, "602-750 MCS")
    _equipment(db, italy_customer.customer_id, "902-2670 MCS")

    draft = maintenance_draft(db, italy_customer.customer_id, ["902-2670 MCS", "602-750 MCS"])

    line_machines = [row.machine for row in draft.rows if row.kind == "line"]
    assert line_machines == ["902-2670 MCS", "602-750 MCS"]
