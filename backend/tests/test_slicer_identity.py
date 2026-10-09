"""Slicer identity: slicer codes are recognised and line parts are never modules.

Slicers are priced as the machine line, so these helpers decide which model a
slicer row names (ambiguous or accessory rows must come back as None) and
whether any other material belongs to the machine line at all (is_line_part).
"""
import pytest

from app.modules.component_names.slicers import (
    SLICER_TYPE_CODES,
    is_line_part,
    normalize_slicer_model,
    slicer_model_for,
)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Slicer 405-Basic", "Slicer 405"),
        ("Slicer 405-Extended", "Slicer 405"),
        ("Slicer 604-1", "Slicer 604"),
        ("Slicer 604-2", "Slicer 604"),
        ("Slicer 904-1", "Slicer 904"),
        ("Slicer 904-2", "Slicer 904"),
        ("CCS 7000 E2", "Slicer 7000"),
        ("CCS 7000 M6", "Slicer 7000"),
        ("Slicer CCS 7000", "Slicer 7000"),
        ("Slicer weSLICE 9500", "weSLICE 9500"),
        ("weSLICE 2000/2500", "weSLICE 2000/2500"),
        ("weSLICE 7X00", "weSLICE 7X00"),
        ("Textor TS700 Slicer", "Textor Slicer TS700"),
    ],
)
def test_slicer_model_normalization(source: str, expected: str):
    assert normalize_slicer_model(source) == expected


def test_accessory_wording_is_never_a_slicer_model():
    assert normalize_slicer_model("CCS 302 | accessories") is None


def test_only_the_verified_slicer_codes_are_slicers():
    assert SLICER_TYPE_CODES == frozenset({"CCS", "SLI", "TSX"})


def test_accessory_row_of_a_slicer_code_is_not_guessed_from_its_material():
    # Gigi's CCS 302-376-Z: a slicer-family accessory must stay unresolved, even
    # though its material number contains a model.
    assert slicer_model_for("CCS", "accessories", None, "CCS 302-376-Z") is None


def test_non_slicer_code_has_no_slicer_model():
    assert slicer_model_for("CCW", "Checkweigher CCW 100", None, "CCW01001") is None


def test_line_parts_recognised_by_type_component_or_name():
    # Textor slicer machines: real slicers outside the CCS/SLI/TSX codes.
    assert is_line_part("TS5", None, "Slicer TS500 Vario")
    assert is_line_part("TS7", None, "Textor Slicer TS700")
    # The dictionary labels these as the line itself or as its accessories.
    assert is_line_part("WLN", "Line", None)
    assert is_line_part("WLZ", "Line Accessories", "Weber Linien-Zubehör Einzelmodul")
    assert is_line_part("WAZ", "Multi Line Accessories", None)
    # Numeric accessory rows carry no component type, only English wording.
    assert is_line_part("305", None, "accessories slicing line")
    assert is_line_part("304", None, "accessory")
    # A classic slicer code is always the line, whatever the wording.
    assert is_line_part("CCS", None, "computerslicer 302")


def test_modules_and_unknown_rows_are_never_hidden_as_line_parts():
    # The dictionary calls these modules: they keep their own hours.
    assert not is_line_part("CFV", "Folding Bar", "folding device weSLICE 9500")
    assert not is_line_part("CCA", "Infeeder", "autom. infeeder (Typ-I-C)")
    assert not is_line_part("CCW", "Checkweigher", "Checkweigher CCW 100")
    # Conservative: unknown wording is never hidden from the human.
    assert not is_line_part("810", None, "BG basic set-up Röntgenscanner")
    assert not is_line_part("904", None, "ETP Ersatzteilpaket 904-7131")
    assert not is_line_part(None, None, "some brand new component")
