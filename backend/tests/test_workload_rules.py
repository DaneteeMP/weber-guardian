"""Service tests for global workload rules and material links.

Each test protects one business rule:
* a rule is a real, named rule with global hours;
* a material belongs to at most one rule, and a move is one update;
* a material with no rule is reported, never priced;
* slicer codes and line parts are never module rules.
"""
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from app.modules.component_names.models import ComponentName
from app.modules.equipment.models import Equipment
from app.modules.workload_rules import service
from app.modules.workload_rules.models import (
    CATEGORY_LEGACY,
    CATEGORY_MANUAL,
    WorkloadRule,
    WorkloadRuleMaterial,
)
from app.modules.workload_rules.schemas import WorkloadRuleCreateIn


def _rule(db, name: str, workload: str | None = "1.00", **over) -> WorkloadRule:
    row = WorkloadRule(
        name=name,
        workload=Decimal(workload) if workload is not None else None,
        legacy_type_code=over.get("legacy_type_code"),
        category=over.get("category", CATEGORY_LEGACY),
        needs_review=over.get("needs_review", workload is None),
        note=over.get("note"),
    )
    db.add(row)
    db.commit()
    return row


def _dictionary(db, material_no: str, type_code: str | None, name: str = "Checkweigher CCW 100", **over):
    db.add(
        ComponentName(
            material_no=material_no,
            name_en=name,
            type_code=type_code,
            component_type=over.get("component_type", "Checkweigher"),
            has_conflict=over.get("has_conflict", False),
        )
    )
    db.commit()


def _installed(db, customer_id: str, material_no: str, row_hash: str) -> None:
    db.add(
        Equipment(
            customer_id=customer_id,
            equipment_name=f"machine-{row_hash}",
            material_no=material_no,
            row_hash=row_hash,
        )
    )
    db.commit()


def _customer(db, customer_id: str):
    from app.modules.customers.models import Customer

    db.add(Customer(customer_id=customer_id, account_name="Test", subsidiary_id="Weber Italy"))
    db.commit()


# --- create / edit -----------------------------------------------------------


def test_create_rule_is_manual_and_needs_review_without_hours(db):
    rule = service.create_rule(db, WorkloadRuleCreateIn(name="Checkweigher 300"))

    assert rule.category == CATEGORY_MANUAL
    assert rule.workload is None
    assert rule.needs_review is True
    assert rule.legacy_type_code is None


def test_create_rule_rejects_a_duplicate_name(db):
    service.create_rule(db, WorkloadRuleCreateIn(name="Checkweigher 300", workload=Decimal("1.5")))

    with pytest.raises(service.WorkloadRuleNameTaken):
        service.create_rule(db, WorkloadRuleCreateIn(name="Checkweigher 300", workload=Decimal("2")))


def test_create_rule_rejects_negative_hours_at_the_schema(db):
    with pytest.raises(ValueError):
        WorkloadRuleCreateIn(name="Bad", workload=Decimal("-1"))


def test_rule_without_hours_cannot_be_marked_reviewed_false(db):
    with pytest.raises(ValueError):
        WorkloadRuleCreateIn(name="No hours", workload=None, needs_review=False)


def test_edit_changes_hours_and_name_but_keeps_the_legacy_code(db):
    rule = _rule(db, "Checkweigher 100", "1.00", legacy_type_code="CCW")

    updated = service.update_rule(db, rule.id, {"name": "Checkweigher CCW 100", "workload": Decimal("1.25")})

    assert updated.name == "Checkweigher CCW 100"
    assert updated.workload == Decimal("1.25")
    assert updated.legacy_type_code == "CCW"
    assert updated.needs_review is False


def test_renaming_keeps_a_conflict_flag_that_was_not_resolved(db):
    """A CONFLICT rule must stay flagged when someone only renames it."""
    rule = _rule(db, "Marking conveyor CMB", "1.50", needs_review=True, category=CATEGORY_LEGACY)

    updated = service.update_rule(db, rule.id, {"name": "Marking conveyor (CMB)"})

    assert updated.needs_review is True
    assert updated.workload == Decimal("1.50")


def test_clearing_hours_forces_review(db):
    rule = _rule(db, "Rocker CCR", "0.50")

    updated = service.update_rule(db, rule.id, {"workload": None})

    assert updated.workload is None
    assert updated.needs_review is True


def test_edit_cannot_mark_a_rule_without_hours_as_reviewed(db):
    rule = _rule(db, "Rocker CCR", "0.50")

    with pytest.raises(ValueError):
        service.update_rule(db, rule.id, {"workload": None, "needs_review": False})


def test_edit_to_an_existing_name_is_rejected(db):
    _rule(db, "Rocker CCR", "0.50")
    other = _rule(db, "Rocker CTR", "0.50")

    with pytest.raises(service.WorkloadRuleNameTaken):
        service.update_rule(db, other.id, {"name": "Rocker CCR"})


# --- linking -----------------------------------------------------------------


def test_link_material_creates_one_link(db):
    _dictionary(db, "CCW01001", "CCW")
    rule = _rule(db, "Checkweigher 100")

    result = service.link_material(db, "CCW01001", rule.id)

    assert result.changed is True
    assert result.previous_rule_id is None
    assert service.linked_count(db, rule.id) == 1


def test_material_cannot_belong_to_two_rules_a_move_replaces_the_link(db):
    _dictionary(db, "CCW01001", "CCW")
    first = _rule(db, "Checkweigher 100")
    second = _rule(db, "Checkweigher 200 mono")
    service.link_material(db, "CCW01001", first.id)

    result = service.link_material(db, "CCW01001", second.id)

    assert result.changed is True
    assert result.previous_rule_id == first.id
    assert result.previous_rule_name == "Checkweigher 100"
    assert db.query(WorkloadRuleMaterial).filter_by(material_no="CCW01001").count() == 1
    assert service.linked_count(db, first.id) == 0
    assert service.linked_count(db, second.id) == 1


def test_linking_to_the_same_rule_is_a_no_op(db):
    _dictionary(db, "CCW01001", "CCW")
    rule = _rule(db, "Checkweigher 100")
    service.link_material(db, "CCW01001", rule.id)

    result = service.link_material(db, "CCW01001", rule.id)

    assert result.changed is False


def test_link_rejects_a_material_that_is_not_in_the_dictionary(db):
    rule = _rule(db, "Checkweigher 100")

    with pytest.raises(service.MaterialNotFound):
        service.link_material(db, "NOPE-000", rule.id)


def test_link_rejects_an_unknown_rule(db):
    import uuid

    _dictionary(db, "CCW01001", "CCW")

    with pytest.raises(service.WorkloadRuleNotFound):
        service.link_material(db, "CCW01001", uuid.uuid4())


def test_database_refuses_a_second_rule_for_the_same_material(db):
    _dictionary(db, "CCW01001", "CCW")
    first = _rule(db, "Checkweigher 100")
    second = _rule(db, "Checkweigher 200 mono")
    db.add(WorkloadRuleMaterial(workload_rule_id=first.id, material_no="CCW01001"))
    db.commit()

    db.add(WorkloadRuleMaterial(workload_rule_id=second.id, material_no="CCW01001"))
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()


def test_unlink_removes_the_material_from_its_rule(db):
    _dictionary(db, "CCW01001", "CCW")
    rule = _rule(db, "Checkweigher 100")
    service.link_material(db, "CCW01001", rule.id)

    assert service.unlink_material(db, "CCW01001") is True
    assert service.linked_count(db, rule.id) == 0
    assert service.unlink_material(db, "CCW01001") is False


# --- resolution --------------------------------------------------------------


def test_material_resolves_to_its_rule_and_its_global_hours(db):
    _dictionary(db, "CCW01001", "CCW")
    rule = _rule(db, "Checkweigher 100", "1.00")
    service.link_material(db, "CCW01001", rule.id)

    resolution = service.resolve_material(db, "CCW01001-10901")

    assert resolution.state == "resolved"
    assert resolution.rule is not None
    assert resolution.rule.name == "Checkweigher 100"
    assert resolution.rule.workload == Decimal("1.00")


def test_dictionary_material_without_a_rule_reports_no_rule(db):
    _dictionary(db, "CCW02001", "CCW", name="Checkweigher 200")

    resolution = service.resolve_material(db, "CCW02001")

    assert resolution.state == "no_rule"
    assert resolution.rule is None


def test_unknown_material_reports_not_in_dictionary(db):
    resolution = service.resolve_material(db, "ZZZ-UNKNOWN")

    assert resolution.state == "not_in_dictionary"
    assert resolution.rule is None


def test_slicer_code_is_never_a_module_rule_state(db):
    _dictionary(db, "CCS 302-376", "CCS", name="computerslicer 302", component_type="Slicer")
    rule = _rule(db, "Anything", "1.00")
    db.add(WorkloadRuleMaterial(workload_rule_id=rule.id, material_no="CCS 302-376"))
    db.commit()

    resolution = service.resolve_material(db, "CCS 302-376")

    assert resolution.state == "slicer"
    assert resolution.rule is None


def test_line_part_without_a_rule_is_priced_by_its_machine(db):
    _dictionary(
        db, "WLZ03051", "WLZ",
        name="Weber Linien-Zubehör Einzelmodul", component_type="Line Accessories",
    )

    resolution = service.resolve_material(db, "WLZ03051")

    assert resolution.state == "slicer"
    assert resolution.rule is None


def test_an_explicit_rule_wins_over_the_line_part_classifier(db):
    _dictionary(db, "CCL404", "CCL", name="accessories slicing line", component_type=None)
    rule = _rule(db, "lc-infeed conveyor CCL", "5.00")
    service.link_material(db, "CCL404", rule.id)

    resolution = service.resolve_material(db, "CCL404")

    assert resolution.state == "resolved"
    assert resolution.rule is not None
    assert resolution.rule.workload == Decimal("5.00")


def test_unresolved_lists_no_rule_and_conflicts_but_not_slicers(db):
    _customer(db, "0000000001")
    _dictionary(db, "CCW02001", "CCW", name="Checkweigher 200")
    _dictionary(db, "CMB01001", "CMB", name="Marking Conveyor", has_conflict=True)
    _dictionary(db, "CCS 302-376", "CCS", name="computerslicer 302", component_type="Slicer")
    _installed(db, "0000000001", "CCW02001", "h1")
    _installed(db, "0000000001", "CMB01001", "h2")
    _installed(db, "0000000001", "CCS 302-376", "h3")
    _installed(db, "0000000001", "MYSTERY-1", "h4")

    rows = {row.material_no: row.reason for row in service.unresolved_materials(db)}

    assert rows == {
        "CCW02001": "no_rule",
        "CMB01001": "dictionary_conflict",
        # Shown by its normalized key, the same key the draft resolves with.
        "MYSTERY": "not_in_dictionary",
    }


def test_linked_material_is_not_listed_as_unresolved(db):
    _customer(db, "0000000001")
    _dictionary(db, "CCW01001", "CCW")
    _installed(db, "0000000001", "CCW01001", "h1")
    rule = _rule(db, "Checkweigher 100", "1.00")
    service.link_material(db, "CCW01001", rule.id)

    assert service.unresolved_materials(db) == []


def test_unresolved_hides_line_parts_and_shows_rules_without_hours(db):
    _customer(db, "0000000001")
    _dictionary(
        db, "WLZ03051", "WLZ",
        name="Weber Linien-Zubehör Einzelmodul", component_type="Line Accessories",
    )
    _dictionary(db, "305", "305", name="accessories slicing line", component_type=None)
    _dictionary(
        db, "CFV06002", "CFV",
        name="folding device weSLICE 9500", component_type="Folding Bar",
    )
    _dictionary(db, "CCW01001", "CCW")
    _installed(db, "0000000001", "WLZ03051", "h1")
    _installed(db, "0000000001", "305", "h2")
    _installed(db, "0000000001", "CFV06002", "h3")
    _installed(db, "0000000001", "CCW01001", "h4")
    pending = _rule(db, "Folding Bar CFV", None)
    service.link_material(db, "CFV06002", pending.id)
    priced = _rule(db, "Checkweigher 100", "1.00")
    service.link_material(db, "CCW01001", priced.id)

    rows = {row.material_no: row.reason for row in service.unresolved_materials(db)}

    # The line accessories are priced by the family line row of each machine,
    # so they are not a human decision. The folding device stays visible while
    # its rule has no hours; the priced checkweigher disappears.
    assert rows == {"CFV06002": "no_hours"}


def test_rule_materials_count_customers_that_have_the_material(db):
    _customer(db, "0000000001")
    _customer(db, "0000000002")
    _dictionary(db, "CCW01001", "CCW")
    _installed(db, "0000000001", "CCW01001-10901", "h1")
    _installed(db, "0000000002", "CCW01001", "h2")
    rule = _rule(db, "Checkweigher 100", "1.00")
    service.link_material(db, "CCW01001", rule.id)

    rows = service.rule_materials(db, rule.id)

    assert [(row.material_no, row.customers) for row in rows] == [("CCW01001", 2)]


def test_list_rules_reports_linked_counts_and_filters_by_review(db):
    review = _rule(db, "Marking conveyor CMB", "1.50", needs_review=True)
    done = _rule(db, "Rocker CCR", "0.50", needs_review=False)
    _dictionary(db, "CCR01001", "CCR", name="Rocker CCR 100")
    service.link_material(db, "CCR01001", done.id)

    rows = dict((rule.name, count) for rule, count in service.list_rules(db))
    flagged = [rule.name for rule, _ in service.list_rules(db, needs_review=True)]

    assert rows == {"Marking conveyor CMB": 0, "Rocker CCR": 1}
    assert flagged == [review.name]
