"""SCA family classifier: multi-track wording vs the single-track default.

Pure-Python: these tests exercise the text rules only, so they need no database.
"""
from app.modules.component_names.families import classify_family, registered_families
from app.modules.component_names.families.sca import rules


def test_sca_is_registered():
    assert "SCA" in registered_families()


def test_multi_track_wording_is_multi():
    assert rules.classify("product scanner multi-track", None) == rules.MULTI
    assert rules.classify(None, "-> iB: Produktscanner mehrspurig") == rules.MULTI


def test_default_is_mono():
    assert rules.classify("product scanner", "-> IB: Produktscanner") == rules.MONO
    assert rules.classify("weSCAN", "weSCAN") == rules.MONO


def test_classify_family_dispatches_by_type_code():
    assert classify_family("sca", "product scanner multi-track", None) == rules.MULTI
    assert classify_family("SCA", "product scanner", None) == rules.MONO
