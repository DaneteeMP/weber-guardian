"""Tests for the names_dictionary.csv cleaning rules.

Every case here is a defect that was measured in the real file, not invented:
repeating rows, disagreeing rows, missing names and a cp1252 encoding. The
parsing itself is a pure function, so it is tested without a database.
"""
import pytest
from sqlalchemy import select

from app.modules.component_names.models import ComponentName
from app.modules.component_names.service import (
    DictionaryFileError,
    import_dictionary,
    parse_and_clean,
)

HEADER = "Component Name EN;Type;Material No.;Component Type;Description"


def build_file(*rows: str) -> bytes:
    return (HEADER + "\r\n" + "\r\n".join(rows) + "\r\n").encode("cp1252")


def test_single_row_becomes_one_entry():
    cleaned = parse_and_clean(build_file("Textor TS700 Slicer;TSX;TSX06001;Slicer;Textor Slicer"))
    assert cleaned.rows_read == 1
    assert len(cleaned.entries) == 1
    entry = cleaned.entries[0]
    assert entry.material_no == "TSX06001"
    assert entry.name_en == "Textor TS700 Slicer"
    assert entry.type_code == "TSX"
    assert entry.component_type == "Slicer"
    assert entry.description == "Textor Slicer"
    assert entry.source_rows == 1
    assert entry.has_conflict is False


def test_cp1252_umlauts_force_the_cp1252_decoder():
    """The legacy file is cp1252: its umlauts are not valid utf-8."""
    raw = build_file("Wippe;CCR;CCR01001;Rocker;Wippe CCR 100 mit Rückwärtsförderer")
    cleaned = parse_and_clean(raw)
    assert cleaned.encoding == "cp1252"
    assert cleaned.entries[0].description.endswith("Rückwärtsförderer")


def test_identical_repeats_collapse_and_count_source_rows():
    """The real file repeats the same material number thousands of times."""
    row = "Checkweigher CCW-500;CCW;CCW05001;Checkweigher;Kontrollwaage CCW 500"
    cleaned = parse_and_clean(build_file(*([row] * 7)))
    assert len(cleaned.entries) == 1
    assert cleaned.entries[0].source_rows == 7
    assert cleaned.duplicate_rows_collapsed == 6
    assert cleaned.entries[0].has_conflict is False


def test_blank_rows_are_counted_not_stored():
    cleaned = parse_and_clean(build_file("Slicer;CCS;CCS06001;Slicer;Slicer", "", "   "))
    assert cleaned.rows_read == 3
    assert cleaned.rows_blank == 2
    assert len(cleaned.entries) == 1


def test_rows_without_material_no_are_counted_not_stored():
    """A row with no material number cannot be joined to any equipment."""
    cleaned = parse_and_clean(build_file("Multivac R 535;VPM;;Packaging Machine;"))
    assert cleaned.rows_without_material_no == 1
    assert cleaned.entries == []


def test_whitespace_and_case_are_normalised():
    cleaned = parse_and_clean(build_file("  Rocker   CCR 100 ; CCR ; CCR01001 ;Rocker;  Wippe CCR 100  "))
    entry = cleaned.entries[0]
    assert entry.name_en == "Rocker CCR 100"
    assert entry.type_code == "CCR"
    assert entry.component_type == "Rocker"
    assert entry.description == "Wippe CCR 100"


def test_majority_value_wins_and_conflict_is_flagged():
    """Same material number, different names: keep the most frequent, flag it."""
    cleaned = parse_and_clean(
        build_file(
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        )
    )
    assert len(cleaned.entries) == 1
    entry = cleaned.entries[0]
    assert entry.name_en == "Infeeder CCA"
    assert entry.has_conflict is True


def test_empty_never_beats_a_real_value():
    """A field present in some rows and blank in others keeps the real value."""
    cleaned = parse_and_clean(
        build_file(
            ";CMB;CMB01001;;Markierband",
            "Marking Conveyor;CMB;CMB01001;Marking Conveyor;Markierband",
        )
    )
    entry = cleaned.entries[0]
    assert entry.name_en == "Marking Conveyor"
    assert entry.component_type == "Marking Conveyor"


def test_tie_breaks_alphabetically_so_the_result_is_reproducible():
    first = parse_and_clean(
        build_file("Alpha;CC;CC00001;A;a", "Beta;CC;CC00001;B;b")
    ).entries[0]
    second = parse_and_clean(
        build_file("Beta;CC;CC00001;B;b", "Alpha;CC;CC00001;A;a")
    ).entries[0]
    assert first.name_en == second.name_en == "Alpha"
    assert first.has_conflict is True


def test_material_number_without_any_english_name_is_reported_not_invented():
    """Four material numbers exist with only a German description."""
    cleaned = parse_and_clean(
        build_file(
            "; ;71511969-02;;BGE Universalband 305-UB",
            "Portioning Unit;CCU;CCU04051;Portioning Unit;Portioniereinheit",
        )
    )
    assert cleaned.material_numbers_without_name == 1
    assert cleaned.unmapped_material_numbers == ["71511969"]
    assert [entry.material_no for entry in cleaned.entries] == ["CCU04051"]


def test_missing_english_name_on_some_rows_is_filled_from_the_others():
    cleaned = parse_and_clean(
        build_file(
            ";;CCU04051;;Portioniereinheit",
            "Portioning Unit;CCU;CCU04051;Portioning Unit;Portioniereinheit",
        )
    )
    assert cleaned.material_numbers_without_name == 0
    assert cleaned.entries[0].name_en == "Portioning Unit"


def test_header_must_match_known_columns():
    with pytest.raises(DictionaryFileError, match="unexpected header"):
        parse_and_clean(b"a;b;c;d;e\r\n1;2;3;4;5\r\n")


def test_column_order_does_not_matter():
    raw = "Description;Component Type;Material No.;Type;Component Name EN\r\nWippe;Rocker;CCR01001;CCR;Rocker CCR\r\n"
    entry = parse_and_clean(raw.encode("cp1252")).entries[0]
    assert entry.material_no == "CCR01001"
    assert entry.name_en == "Rocker CCR"
    assert entry.type_code == "CCR"


def test_empty_file_is_rejected():
    with pytest.raises(DictionaryFileError, match="empty"):
        parse_and_clean(b"")


def test_short_row_is_rejected_instead_of_guessed():
    with pytest.raises(DictionaryFileError, match="expected at least 5"):
        parse_and_clean(build_file("Slicer;CCS;CCS06001"))


def test_utf8_file_is_accepted_when_re_exported():
    raw = (HEADER + "\nRocker CCR;CCR;CCR01001;Rocker;Wippe\n").encode("utf-8")
    cleaned = parse_and_clean(raw)
    assert cleaned.encoding == "utf-8"
    assert cleaned.entries[0].name_en == "Rocker CCR"


def test_import_writes_entries_and_reports_collapsed_rows(db):
    row = "Checkweigher CCW-500;CCW;CCW05001;Checkweigher;Kontrollwaage CCW 500"
    report = import_dictionary(db, build_file(*([row] * 3)))

    assert report.entries_written == 1
    assert report.entries_total_after == 1
    assert report.duplicate_rows_collapsed == 2
    assert report.entries_with_conflict == 0

    stored = db.scalar(select(ComponentName))
    assert stored.material_no == "CCW05001"
    assert stored.source_rows == 3


def test_reimport_updates_the_same_row_instead_of_duplicating(db):
    import_dictionary(db, build_file("Rocker CCR;CCR;CCR01001;Rocker;Wippe"))
    report = import_dictionary(db, build_file("Rocker CCR 100;CCR;CCR01001;Rocker;Wippe"))

    rows = list(db.scalars(select(ComponentName)))
    assert len(rows) == 1
    assert rows[0].name_en == "Rocker CCR 100"
    assert report.stale_entries_deleted == 0


def test_reimport_deletes_material_numbers_the_file_dropped(db):
    import_dictionary(
        db, build_file("Rocker CCR;CCR;CCR01001;Rocker;Wippe", "Slicer;CCS;CCS06001;Slicer;Slicer")
    )
    report = import_dictionary(db, build_file("Rocker CCR;CCR;CCR01001;Rocker;Wippe"))

    assert report.stale_entries_deleted == 1
    assert [row.material_no for row in db.scalars(select(ComponentName))] == ["CCR01001"]


def test_conflicting_material_numbers_are_flagged_for_review(db):
    import_dictionary(
        db,
        build_file(
            "Infeeder CCA;CCA;CCA06001;Infeeder;Infeeder CCA",
            "Infeeder CCA 600;CCA;CCA06001;Infeeder;Infeeder CCA 600",
        ),
    )
    stored = db.scalar(select(ComponentName))
    assert stored.has_conflict is True
