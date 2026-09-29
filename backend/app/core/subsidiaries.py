"""Subsidiary identity: canonical full names, tolerated input variants.

Canonical IDs are the business names ("Weber Iberica"). Short codes
("ES") and free text ("España") are legacy/input variants resolved here,
never stored. Unknown values pass through upper-cased (explicit, and the
import reports them as warnings instead of guessing a filial).
"""
import re

CANONICAL = [
    "Weber Benelux", "Weber Brazil", "Weber Colombia", "Weber Croatia",
    "Weber Czech", "Weber Denmark", "Weber Finland", "Weber France",
    "Weber Germany", "Weber Iberica", "Weber Inc", "Weber Italy",
    "Weber Latam", "Weber Latina", "Weber Norway", "Weber Poland",
    "Weber Romania", "Weber Russia", "Weber Singapore", "Weber Sweden",
    "Weber Switzerland", "Weber Partners",
]

SHORT_LABELS = {
    "Weber Benelux": "Benelux", "Weber Brazil": "Brazil", "Weber Colombia": "Colombia",
    "Weber Croatia": "Croatia", "Weber Czech": "Czech", "Weber Denmark": "Denmark",
    "Weber Finland": "Finland", "Weber France": "France", "Weber Germany": "Germany",
    "Weber Iberica": "Iberica", "Weber Inc": "Inc", "Weber Italy": "Italy",
    "Weber Latam": "Latam", "Weber Latina": "Latina", "Weber Norway": "Norway",
    "Weber Poland": "Poland", "Weber Romania": "Romania", "Weber Russia": "Russia",
    "Weber Singapore": "Singapore", "Weber Sweden": "Sweden",
    "Weber Switzerland": "Switzerland", "Weber Partners": "Partners",
}

# Legacy short codes and free-text variants -> canonical full name.
SUBSIDIARY_ALIASES = {
    "es": "Weber Iberica", "españa": "Weber Iberica", "espana": "Weber Iberica",
    "spain": "Weber Iberica", "ibérica": "Weber Iberica", "iberica": "Weber Iberica",
    "bnl": "Weber Benelux", "benelux": "Weber Benelux",
    "nederland": "Weber Benelux", "netherlands": "Weber Benelux", "holland": "Weber Benelux",
    "de": "Weber Germany", "deutschland": "Weber Germany", "alemania": "Weber Germany",
    "germany": "Weber Germany", "breidenbach": "Weber Germany",
    "ar": "Weber Argentina", "argentina": "Weber Argentina",
}

# Executor blocks live under short codes (see app.weber.pdf).
EXECUTOR_CODES = {
    "Weber Iberica": "ES",
    "Weber Benelux": "BNL",
    "Weber Germany": "DE",
    "Weber Argentina": "AR",
}

# CSV spellings that normalization alone cannot reconcile with the catalog.
# Keys AND values are _key() output (lowercase alphanumeric, no punctuation).
COUNTRY_ALIASES = {
    "bosniaandherzegovina": "bosniaherz",
    "palestinianterritoryoccupied": "palestine",
    "dominicanrepublic": "dominicanrep",
    "trinidadandtobago": "trinidadtobago",
    "russianfederation": "russianfed",
    "unitedarabemirates": "utdarabemir",
    "korearepublicof": "southkorea",
    "macedoniatheformeryugoslavrepublicof": "macedonia",
    "boliviaplurinationalstateof": "bolivia",
    "venezuelabolivarianrepublicof": "venezuela",
}


def _key(value: str) -> str:
    """Lowercase alphanumeric key: spaces, punctuation and case vanish."""
    return re.sub(r"[^a-z0-9]", "", value.lower())


def normalize_country(value: str | None) -> str | None:
    """Canonical country key, or None for empty input."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    key = _key(stripped)
    return COUNTRY_ALIASES.get(key, key)


def normalize_subsidiary(value: str | None) -> str | None:
    """Canonical full name, or None for empty input. Unknown values pass
    through upper-cased so new filials work before getting an alias."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    lowered = stripped.lower()
    for name in CANONICAL:
        if lowered == name.lower():
            return name
    short = lowered.removeprefix("weber ").strip()
    if short in SUBSIDIARY_ALIASES:
        return SUBSIDIARY_ALIASES[short]
    return SUBSIDIARY_ALIASES.get(lowered, stripped.upper())


def short_label(subsidiary: str | None) -> str | None:
    """Display label for the UI badge; None stays None."""
    if subsidiary is None:
        return None
    return SHORT_LABELS.get(subsidiary, subsidiary)
