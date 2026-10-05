"""Tests for the dictionary grid: filtering, manual edits and the export."""
import pytest

from app.modules.component_names.models import ComponentName
from app.modules.component_names.schemas import ComponentNameUpdateIn
from app.modules.component_names.service import (
    ComponentNameNotFound,
    count_component_names,
    export_component_names,
    import_dictionary,
    list_component_names,
    update_component_name,
)

HEADER = "Component Name EN;Type;Material No.;Component Type;Description"


def build_file(*rows: str) -> bytes:
    return (HEADER + "\r\n" + "\r\n".join(rows) + "\r\n").encode("cp1252")


def seed(db):
    import_dictionary(
        db,
        build_file(
            "Rocker CCR 100;CCR;CCR01001;Rocker;Wippe CCR 100",
            "Checkweigher CCW-500;CCW;CCW05001;Checkweigher;Kontrollwaage CCW 500",
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        ),
    )


def test_list_is_ordered_by_material_number(db):
    seed(db)
    rows = list_component_names(db)
    assert [row.material_no for row in rows] == ["CCA06001", "CCR01001", "CCW05001"]


def test_search_matches_material_name_or_description(db):
    seed(db)
    assert [r.material_no for r in list_component_names(db, search="CCW-500")] == ["CCW05001"]
    assert [r.material_no for r in list_component_names(db, search="Wippe")] == ["CCR01001"]
    assert list_component_names(db, search="nothing here") == []


def test_filter_by_component_type(db):
    seed(db)
    assert [r.material_no for r in list_component_names(db, component_type="Rocker")] == ["CCR01001"]
    assert len(list_component_names(db, component_type="Infeeder")) == 1


def test_only_conflicts_filter_surfaces_undecided_entries(db):
    seed(db)
    conflicted = list_component_names(db, only_conflicts=True)
    assert [row.material_no for row in conflicted] == ["CCA06001"]
    assert conflicted[0].has_conflict is True


def test_count_agrees_with_the_filtered_list(db):
    seed(db)
    assert count_component_names(db) == 3
    assert count_component_names(db, component_type="Infeeder") == 1
    assert count_component_names(db, only_conflicts=True) == 1
    assert count_component_names(db, search="Wippe") == 1


def test_grid_pages_do_not_change_the_total(db):
    seed(db)
    first = list_component_names(db, limit=2, offset=0)
    second = list_component_names(db, limit=2, offset=2)
    assert [r.material_no for r in first] == ["CCA06001", "CCR01001"]
    assert [r.material_no for r in second] == ["CCW05001"]
    assert count_component_names(db) == 3


def test_update_changes_only_the_fields_sent(db):
    seed(db)
    update_component_name(db, "CCR01001", ComponentNameUpdateIn(name_en="Rocker CCR 100 new").model_dump(exclude_none=True))
    row = list_component_names(db, search="CCR01001")[0]
    assert row.name_en == "Rocker CCR 100 new"
    # Untouched columns keep their values instead of being blanked.
    assert row.type_code == "CCR"
    assert row.component_type == "Rocker"
    assert row.description == "Wippe CCR 100"


def test_update_can_settle_a_conflict(db):
    seed(db)
    update_component_name(db, "CCA06001", {"has_conflict": False})
    assert list_component_names(db, only_conflicts=True) == []
    assert count_component_names(db) == 3


def test_update_unknown_material_number_raises_domain_error(db):
    seed(db)
    with pytest.raises(ComponentNameNotFound):
        update_component_name(db, "NOPE", {"name_en": "x"})


def test_update_rejects_a_field_that_is_not_editable(db):
    """A wrong key must fail loudly instead of writing a stray attribute."""
    seed(db)
    with pytest.raises(ValueError, match="cannot edit fields"):
        update_component_name(db, "CCR01001", {"material_no": "HACKED"})
    assert list_component_names(db, search="CCR01001")[0].material_no == "CCR01001"


def test_export_reproduces_the_legacy_five_columns(db):
    seed(db)
    text = export_component_names(db)
    lines = text.strip().splitlines()
    assert lines[0] == HEADER
    assert len(lines) == 4
    assert "CCR01001" in text
    # The export must be a valid input file again, or the clean/download loop
    # would break on the second pass.
    assert import_dictionary(db, text.encode("cp1252")).entries_total_after == 3


def test_export_writes_blank_cells_for_missing_optional_columns(db):
    import_dictionary(db, build_file("Rocker CCR;CCR;CCR01001;;"))
    text = export_component_names(db)
    assert text.strip().splitlines()[1] == "Rocker CCR;CCR;CCR01001;;"
    assert ComponentName.__table__.c.description.nullable is True
