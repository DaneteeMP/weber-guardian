"""Contract locale normalization and Babel formatting tests."""
from datetime import date
from decimal import Decimal

import pytest

from app.weber.locales import (
    DEFAULT_LOCALE,
    format_date,
    format_money,
    format_number,
    normalize_locale,
)


@pytest.mark.parametrize("raw", ["es", "ES", "es-ES", "Spanish", "spanish", "Español", " Español "])
def test_spanish_inputs_normalize_to_es(raw):
    assert normalize_locale(raw) == "es"


@pytest.mark.parametrize(
    "raw,expected",
    [("en", "en"), ("EN-US", "en"), ("English", "en"), ("de-DE", "de"),
     ("German", "de"), ("pt-BR", "pt"), ("Português", "pt"), ("it", "it")],
)
def test_other_inputs_normalize(raw, expected):
    assert normalize_locale(raw) == expected


def test_missing_value_falls_back_to_english():
    """Documented default: a contract without language renders in English."""
    assert normalize_locale(None) == "en"
    assert normalize_locale("") == "en"
    assert normalize_locale("   ") == "en"
    assert DEFAULT_LOCALE == "en"


def test_garbage_raises_instead_of_silently_rendering_the_wrong_language():
    with pytest.raises(ValueError, match="language"):
        normalize_locale("Klingon")
    with pytest.raises(ValueError, match="language"):
        normalize_locale("fr")


def test_money_formats_per_locale():
    # Babel CLDR puts a non-breaking space before the symbol (keeps the amount
    # and its symbol on the same line in the PDF).
    nbsp = "\u00a0"
    amount = Decimal("1234.50")
    assert format_money(amount, "es") == f"1.234,50{nbsp}€"
    assert format_money(amount, "en") == "€1,234.50"
    assert format_money(amount, "de") == f"1.234,50{nbsp}€"
    assert format_money(amount, "es", currency="USD") == f"1.234,50{nbsp}US$"


def test_number_and_date_format_per_locale():
    assert format_number(Decimal("1234.5"), "es") == "1.234,5"
    assert format_date(date(2026, 9, 21), "es") == "21 de septiembre de 2026"
    assert format_date(date(2026, 9, 21), "en") == "September 21, 2026"
    assert format_date(None, "es") == ""
