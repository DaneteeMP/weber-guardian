"""Weber numbering tests. Pure adapter, no DB."""
import pytest

from app.weber.guardian_numbering import build_number, guardian_type_of


def test_guardian_type_of_known_codes():
    assert guardian_type_of("W-01-2026-0001") == "Basic Kit"
    assert guardian_type_of("W-02-2026-0001") == "Audit"
    assert guardian_type_of("W-03-2026-0001") == "Off-Guardian"
    assert guardian_type_of("W-09-2026-0001") is None


def test_build_number_format():
    assert build_number("W", 2026, 7) == "W-02-2026-0007"
    assert build_number("W", 2026, 7, "01") == "W-01-2026-0007"


def test_build_number_rejects_bad_parts():
    with pytest.raises(ValueError):
        build_number("", 2026, 1)
    with pytest.raises(ValueError):
        build_number("W", 1999, 1)
    with pytest.raises(ValueError):
        build_number("W", 2026, 0)
    with pytest.raises(ValueError):
        build_number("W", 2026, 1, "09")
