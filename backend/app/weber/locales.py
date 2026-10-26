"""Contract language handling for the offer PDF.

Normalizes every language representation the system can hold (UI codes,
BCP 47 tags, legacy WeberAssistant names like "Spanish") to a canonical
short tag, and formats money/dates/numbers per locale with Babel.

Who uses it:
- the offer PDF renderer, to pick translations and number formats;
- the annex translation lookup, to fall back to a base language.

Rules:
- missing value (None/blank) falls back to "en" (documented default);
- an unrecognized non-empty value raises ValueError: garbage must never
  silently render a contract in the wrong language.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from babel.dates import format_date as babel_format_date
from babel.numbers import format_currency, format_decimal

DEFAULT_LOCALE = "en"

# Canonical contract locales with their UI display names (also used by the
# frontend selector). BCP 47 short codes: language subtag only, because every
# supported language renders with its own region-neutral rules here.
SUPPORTED_LOCALES: dict[str, str] = {
    "es": "Español",
    "en": "English",
    "de": "Deutsch",
    "pt": "Português",
    "it": "Italiano",
}

# Aliases seen in real data: legacy offer.language values (WeberAssistant UI
# names), full language names and region-tagged BCP 47 variants. Each key is
# lowercased and stripped before lookup.
_ALIASES: dict[str, str] = {
    "es": "es",
    "es-es": "es",
    "es-mx": "es",
    "spanish": "es",
    "español": "es",
    "espanol": "es",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "english": "en",
    "de": "de",
    "de-de": "de",
    "german": "de",
    "deutsch": "de",
    "pt": "pt",
    "pt-pt": "pt",
    "pt-br": "pt",
    "portuguese": "pt",
    "português": "pt",
    "portugues": "pt",
    "it": "it",
    "it-it": "it",
    "italian": "it",
    "italiano": "it",
}


def normalize_locale(value: Optional[str]) -> str:
    """Return the canonical short tag; None/blank -> DEFAULT_LOCALE."""
    if value is None or not str(value).strip():
        return DEFAULT_LOCALE
    key = str(value).strip().lower().replace("_", "-")
    resolved = _ALIASES.get(key)
    if resolved is None:
        raise ValueError(f"unsupported contract language: {value!r}")
    return resolved


def format_money(value: Decimal, locale: str, currency: str = "EUR") -> str:
    """Locale-aware amount, e.g. es: '1.234,50 €', en: '€1,234.50'."""
    normalized = normalize_locale(locale)
    return format_currency(value, currency, locale=normalized)


def format_number(value: Decimal, locale: str) -> str:
    """Locale-aware plain number (no currency symbol)."""
    normalized = normalize_locale(locale)
    return format_decimal(value, locale=normalized)


def format_date(value: Optional[date], locale: str) -> str:
    """Locale-aware long date for the contract body, e.g.
    es: '21 de septiembre de 2026', en: 'September 21, 2026'."""
    if value is None:
        return ""
    normalized = normalize_locale(locale)
    return babel_format_date(value, format="long", locale=normalized)
