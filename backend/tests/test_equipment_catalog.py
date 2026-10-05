"""Equipment catalog tests: exact matching, confirmation, CRUD and conflicts.

Since migration 0019 the catalog holds lines only: modules are priced through
component_workloads and the schema refuses any other kind. resolve_line is the
helper the maintenance draft uses, so its confirmation semantics are tested
here too.
"""
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.modules.equipment_catalog.schemas import EquipmentCatalogEntryIn
from app.modules.equipment_catalog.service import (
    EquipmentCatalogConflict,
    create_entry,
    delete_entry,
    list_entries,
    resolve_line,
    update_entry,
)


def _line_entry(*, confirmed: bool = False, label: str = "30x") -> EquipmentCatalogEntryIn:
    return EquipmentCatalogEntryIn(
        kind="line",
        label=label,
        workload=Decimal("4.5"),
        matches=[
            {"match_field": "machine_type", "match_value": "CCS304", "is_confirmed": confirmed}
        ],
    )


def test_unconfirmed_match_resolves_as_candidate_not_as_line(db):
    entry = create_entry(db, _line_entry())

    resolved = resolve_line(db, "CCS304")

    assert resolved is not None
    assert resolved[0].id == entry.id
    assert resolved[1] is False
    assert entry.matches[0].is_confirmed is False


def test_confirmed_match_resolves_with_its_workload(db):
    entry = create_entry(db, _line_entry(confirmed=True))

    resolved = resolve_line(db, "CCS304")

    assert resolved is not None
    assert resolved[0].id == entry.id
    assert resolved[0].workload == Decimal("4.5")
    assert resolved[1] is True


def test_matching_is_exact_and_empty_codes_resolve_to_nothing(db):
    create_entry(db, _line_entry(confirmed=True))

    assert resolve_line(db, "CCS304-extra") is None
    assert resolve_line(db, "") is None
    assert resolve_line(db, None) is None


def test_schema_accepts_lines_only():
    """Migration 0019 dropped module pricing: the schema refuses other kinds."""
    with pytest.raises(ValidationError):
        EquipmentCatalogEntryIn(
            kind="module",
            label="Checkweigher",
            matches=[{"match_field": "machine_type", "match_value": "CCS304"}],
        )


def test_schema_rejects_material_number_matches():
    with pytest.raises(ValidationError):
        EquipmentCatalogEntryIn(
            kind="line",
            label="Checkweigher",
            matches=[{"match_field": "material_no", "match_value": "CCW05001"}],
        )


def test_duplicate_external_code_is_a_domain_conflict(db):
    create_entry(db, _line_entry(label="30x"))

    with pytest.raises(EquipmentCatalogConflict):
        create_entry(db, _line_entry(label="40x"))

    assert [entry.label for entry in list_entries(db)] == ["30x"]


def test_duplicate_match_value_inside_one_payload_is_rejected(db):
    with pytest.raises(ValidationError, match="Duplicate match value"):
        EquipmentCatalogEntryIn(
            kind="line",
            label="30x",
            matches=[
                {"match_field": "machine_type", "match_value": "CCS304"},
                {"match_field": "machine_type", "match_value": "CCS304"},
            ],
        )


def test_update_replaces_entry_and_associations(db):
    created = create_entry(db, _line_entry())
    updated = update_entry(
        db,
        created.id,
        EquipmentCatalogEntryIn(
            kind="line",
            label="30x revised",
            workload=Decimal("5.0"),
            matches=[
                {"match_field": "machine_type", "match_value": "CCS304", "is_confirmed": True},
                {"match_field": "machine_type", "match_value": "CCS305", "is_confirmed": False},
            ],
        ),
    )

    assert updated is not None
    assert updated.id == created.id
    assert updated.label == "30x revised"
    assert updated.workload == Decimal("5.0")
    assert {match.match_value for match in updated.matches} == {"CCS304", "CCS305"}
    assert resolve_line(db, "CCS304")[0].id == created.id
    assert resolve_line(db, "CCS305")[1] is False


def test_delete_removes_entry_and_matches(db):
    created = create_entry(db, _line_entry())

    assert delete_entry(db, created.id) is True
    assert delete_entry(db, created.id) is False
    assert list_entries(db) == []
