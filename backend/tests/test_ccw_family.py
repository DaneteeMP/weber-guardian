"""CCW family classifier: the multi hints, and what must stay mono.

Pure-Python: these tests exercise the text rules only, so they need no database.
"""
from app.modules.component_names.families import classify_family, registered_families
from app.modules.component_names.families.ccw import rules


def test_ccw_is_registered():
    assert "CCW" in registered_families()


def test_default_is_mono():
    assert rules.classify("CCW", None) == rules.MONO


def test_single_track_wording_stays_mono():
    for text in (
        "CCW 1-times BB=375mm round belt",
        "Kontrollwaage 1-fach BB=375mm RR",
        "CCW mono BB=375 RR",
    ):
        assert rules.classify(text, text) == rules.MONO


def test_model_numbers_and_dimensions_are_not_lane_counts():
    # "200" is a model, "530"/"370"/"375" are widths: none is a lane count.
    assert rules.classify("Checkweigher 200", "Kontrollwaage CCW 200") == rules.MONO
    assert rules.classify("CCW hyg. design 530", "Kontrollwaage Hygieneausf. 530") == rules.MONO
    assert rules.classify("CCW 1-times BB=370mm round belt", None) == rules.MONO


def test_tandem_and_kombi_are_multi():
    assert rules.classify("BG Weber Tandemwaage kompl.", None) == rules.MULTI
    assert rules.classify(None, "-> IB: Kontrollwaage Kombiausführung") == rules.MULTI


def test_a_count_of_two_or_more_with_its_unit_is_multi():
    assert rules.classify(None, "Kontrollwaage 3-Spur-Ausführung") == rules.MULTI
    assert rules.classify(None, "-> IB: CCW 2-times BB=225mm RR") == rules.MULTI
    assert rules.classify(None, "Kontrollwaage 2-fach") == rules.MULTI


def test_extra_multi_words_are_multi():
    for text in ("zweispurig", "double", "Mehrfachausführung", "doppel", "multi-track"):
        assert rules.classify(None, text) == rules.MULTI


def test_classify_family_dispatches_by_type_code():
    assert classify_family("ccw", "CCW 1-times", None) == rules.MONO
    assert classify_family("CCW", None, "Kontrollwaage 3-Spur") == rules.MULTI


def test_family_without_a_classifier_is_undecided_not_mono():
    assert classify_family("CCQ", "transport conveyor", None) is None
