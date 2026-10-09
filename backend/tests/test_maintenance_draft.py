"""Maintenance draft tests: amounts are workload × the customer's branch rate.

Every rule here protects one business invariant: the server computes the money
with Decimal from verified hours, and anything it cannot verify arrives flagged
for a human instead of silently priced at zero.

Module hours come from the global workload rule a material is linked to. A
rule change applies to the next draft of every customer that uses it.
"""
from itertools import count
from decimal import Decimal

import pytest

from app.modules.basic_kit.models import BasicKit
from app.modules.component_names.models import ComponentName
from app.modules.customers.models import Customer
from app.modules.customers.service import CustomerNotFound
from app.modules.equipment.models import Equipment
from app.modules.equipment_catalog.schemas import EquipmentCatalogEntryIn
from app.modules.equipment_catalog.service import create_entry
from app.modules.offers.maintenance import RateNotConfigured, maintenance_draft
from app.modules.prices.models import PriceList
from app.modules.workload_rules.models import WorkloadRule, WorkloadRuleMaterial


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


def _rule_for(db, material_no: str, workload: str | None, *, needs_review: bool = False) -> WorkloadRule:
    """Create a global rule and link one dictionary material to it."""
    rule = WorkloadRule(
        name=f"rule for {material_no}",
        workload=Decimal(workload) if workload is not None else None,
        category="legacy",
        needs_review=needs_review or workload is None,
    )
    db.add(rule)
    db.commit()
    db.add(WorkloadRuleMaterial(workload_rule_id=rule.id, material_no=material_no))
    db.commit()
    return rule


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
    _rule_for(db, "CCW05001", "1.5")
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


def test_dictionary_material_without_a_rule_is_flagged_not_priced(db, italy_customer):
    _confirmed_line(db)
    _dictionary(db, "CCW05001", "CCW")  # known material, not linked to any rule
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCW05001")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    module = draft.rows[1]
    assert module.type_code == "CCW"
    assert module.workload is None
    assert module.workload_id is None
    assert module.needs_review is True
    assert module.amount == Decimal("0.00")


def test_slicer_component_is_the_line_and_is_not_repeated_as_a_module(db, italy_customer):
    """The slicer is the machine line (priced by family), never a module.

    A compact UB slicer has only its slicer component, so the draft must show
    the line row alone and not a second, model-priced slicer row (nor the
    bogus "-Z" accessory variant).
    """
    _confirmed_line(db, label="30x", machine_type="CCS302", workload="2.0")
    _dictionary(db, "CCS 302-376", "CCS", name="computerslicer 302", component_type="Slicer")
    _dictionary(db, "CCS 302-376-Z", "CCS", name="accessories", component_type="Slicer")
    _equipment(
        db, italy_customer.customer_id, "302-376 UB",
        machine_type="CCS302", material_no="CCS 302-376", component_type="Slicer",
    )
    _equipment(
        db, italy_customer.customer_id, "302-376 UB",
        machine_type="CCS302", material_no="CCS 302-376-Z", component_type="Slicer",
    )

    draft = maintenance_draft(db, italy_customer.customer_id, ["302-376 UB"])

    assert [row.kind for row in draft.rows] == ["line"]
    line = draft.rows[0]
    assert line.description == "30x"
    assert line.workload == Decimal("2.0")
    assert draft.total_workload == Decimal("2.0")
    assert draft.total_amount == Decimal("116.00")


def test_line_parts_are_priced_by_the_family_line_not_as_modules(db, italy_customer):
    """Accessories and slicing-line rows belong to the machine line.

    Unlinked they never show up as flagged modules: the family line row prices
    the whole line. An explicit rule with hours keeps a material as a priced
    module, and a linked rule without hours stays visible as pending.
    """
    _confirmed_line(db, workload="3.0")
    _dictionary(
        db, "WLZ03051", "WLZ",
        name="Weber Linien-Zubehör Einzelmodul", component_type="Line Accessories",
    )
    _dictionary(db, "CCL 404", "CCL", name="accessories slicing line", component_type=None)
    _dictionary(
        db, "CFV06002", "CFV",
        name="folding device weSLICE 9500", component_type="Folding Bar",
    )
    _rule_for(db, "CCL 404", "5.00")
    _rule_for(db, "CFV06002", None)
    for material in ("WLZ03051", "CCL 404", "CFV06002"):
        _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no=material)

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    by_type = {row.type_code: row for row in draft.rows if row.kind == "module"}
    assert "WLZ" not in by_type
    assert by_type["CCL"].workload == Decimal("5.00")
    assert by_type["CCL"].amount == Decimal("290.00")
    assert by_type["CCL"].needs_review is False
    assert by_type["CFV"].workload is None
    assert by_type["CFV"].needs_review is True


def test_line_row_exposes_the_line_edit_target(db, italy_customer):
    """A resolved line tells the UI to edit the equipment_catalog entry."""
    _confirmed_line(db, label="602", machine_type="CCS602", workload="3.0")
    _equipment(db, italy_customer.customer_id, "602-750 MCS")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    line = draft.rows[0]
    assert line.workload_kind == "line"
    assert line.line_code == "CCS602"
    assert line.workload_id is not None


def test_unresolved_line_row_is_still_editable(db, italy_customer):
    """A line the catalog does not know can still be configured from the offer."""
    _equipment(db, italy_customer.customer_id, "Mystery machine", machine_type="XXX999")

    draft = maintenance_draft(db, italy_customer.customer_id, ["Mystery machine"])

    line = draft.rows[0]
    assert line.workload_kind == "line"
    assert line.line_code == "XXX999"
    assert line.workload_id is None
    assert line.needs_review is True


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
    _rule_for(db, "CCW05001", "1.5")
    _dictionary(db, "ZZZUNKNOWN", None)
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCW05001")
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="ZZZ-UNKNOWN")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    assert draft.total_workload == Decimal("4.5")
    assert draft.total_amount == Decimal("261.00")
    assert draft.currency == "EUR"
    assert draft.tech_rate == Decimal("58.00")


def test_changing_the_global_rule_changes_the_next_draft(db, italy_customer):
    """Hours live in the global rule: editing it reprices every future draft."""
    _confirmed_line(db)
    _dictionary(db, "CCW05001", "CCW")
    rule = _rule_for(db, "CCW05001", "1.5")
    _equipment(db, italy_customer.customer_id, "602-750 MCS", material_no="CCW05001")

    before = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])
    module_before = next(row for row in before.rows if row.kind == "module")
    assert module_before.amount == Decimal("87.00")

    rule.workload = Decimal("2.00")
    db.commit()

    after = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])
    module_after = next(row for row in after.rows if row.kind == "module")
    assert module_after.workload == Decimal("2.00")
    assert module_after.amount == Decimal("116.00")


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


def test_gigi_machine_resolves_its_real_modules_and_never_a_slicer(db, italy_customer):
    """Gigi WLN04051-23050 (customer 0001017849), with the data reconstructed by rule.

    * CCS04051 is the slicer = the machine line, so it is never a module;
    * KSG01001 sharpener, CCE03001, CCU04051, CCW01001 resolve to their rules;
    * CMB01001 is linked but flagged (legacy conflict), so it is still priced at
      its stored value and marked for review;
    * WLZ04051 is a line accessory: priced by the family line row of the
      machine, so it never appears as an unpriced module.
    """
    _confirmed_line(db, label="40x", machine_type="WLN04051", workload="2.0")
    _dictionary(db, "KSG01001", "KSG", name="Sharpener", component_type="Sharpener")
    _rule_for(db, "KSG01001", "1.00")
    _dictionary(db, "CCE03001", "CCE", name="transport conveyor LC", component_type="Transport Conveyor")
    _rule_for(db, "CCE03001", "1.50")
    _dictionary(db, "CMB01001", "CMB", name="Marking Conveyor", component_type="Transport Conveyor")
    _rule_for(db, "CMB01001", "1.50", needs_review=True)
    _dictionary(db, "CCW01001", "CCW", name="Checkweigher CCW 100", component_type="Checkweigher")
    _rule_for(db, "CCW01001", "1.00")
    _dictionary(db, "CCU04051", "CCU", name="portioning unit 405-Extended", component_type="Portioning Conveyor")
    _rule_for(db, "CCU04051", "0.50")
    _dictionary(db, "CCS04051", "CCS", name="Slicer 405-Extended", component_type="Slicer")
    _dictionary(db, "WLZ04051", "WLZ", name="Accessories Slicer 405-1", component_type="Line Accessories")
    for material in ("KSG01001", "CCE03001", "CMB01001", "CCW01001", "CCU04051", "CCS04051", "WLZ04051"):
        _equipment(
            db, italy_customer.customer_id, "WLN04051-23050",
            machine_type="WLN04051", material_no=material,
        )

    draft = maintenance_draft(db, italy_customer.customer_id, ["WLN04051-23050"])

    modules = {row.material_no: row for row in draft.rows if row.kind == "module"}
    assert "CCS04051" not in modules
    assert modules["KSG01001"].workload == Decimal("1.00")
    assert modules["CCE03001"].workload == Decimal("1.50")
    assert modules["CMB01001"].workload == Decimal("1.50")
    assert modules["CMB01001"].needs_review is True
    assert modules["CCW01001"].workload == Decimal("1.00")
    assert modules["CCW01001"].description == "Checkweigher CCW 100"
    assert modules["CCU04051"].workload == Decimal("0.50")
    assert "WLZ04051" not in modules
    # 2.0 line + 1.0 KSG + 1.5 CCE + 1.5 CMB + 1.0 CCW + 0.5 CCU = 7.5 h.
    assert draft.total_workload == Decimal("7.5")
    assert draft.total_amount == Decimal("435.00")


def test_basic_kit_aggregates_by_machine_type(db, italy_customer):
    _confirmed_line(db)
    kit = BasicKit(model="CCS602", workload_basic_kit=Decimal("4"), spare_parts=Decimal("500"))
    db.add(kit)
    db.commit()
    _equipment(db, italy_customer.customer_id, "602-750 MCS")
    # A second machine without a kit row must not pollute the aggregates.
    _equipment(db, italy_customer.customer_id, "Mystery machine", machine_type="XXX999")

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS", "Mystery machine"])

    assert draft.basic_kit_hours == Decimal("4")
    assert draft.basic_kit_price == Decimal("500")
    # The kit is not a priced maintenance row: totals stay workload-only.
    assert draft.total_workload == Decimal("3.0")


def test_draft_row_exposes_the_module_edit_target(db, italy_customer):
    """A module row points at its global rule, so the offer edits that rule."""
    _confirmed_line(db)
    _dictionary(db, "CCU04051", "CCU", name="portioning unit", component_type="Portioning Conveyor")
    rule = _rule_for(db, "CCU04051", None)
    _equipment(
        db, italy_customer.customer_id, "602-750 MCS",
        material_no="CCU04051", component_type="Portioning Conveyor",
    )

    draft = maintenance_draft(db, italy_customer.customer_id, ["602-750 MCS"])

    module = next(row for row in draft.rows if row.kind == "module")
    assert module.workload_kind == "module"
    assert module.type_code == "CCU"
    assert module.workload_id == rule.id
    assert module.component_type == "Portioning Conveyor"
