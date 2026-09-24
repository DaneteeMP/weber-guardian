"""Subsidiary codes: single canonical form, free-text input tolerated.

Codes are short ("ES", "DE", "BNL", "AR", ...). Humans type variants
("España", "Deutschland"), so every entry point normalizes instead of
storing the raw text (which silently breaks scope filters).
"""

ALIASES = {
    "es": "ES",
    "españa": "ES",
    "espana": "ES",
    "spain": "ES",
    "ibérica": "ES",
    "iberica": "ES",
    "bnl": "BNL",
    "benelux": "BNL",
    "nederland": "BNL",
    "netherlands": "BNL",
    "holland": "BNL",
    "de": "DE",
    "deutschland": "DE",
    "alemania": "DE",
    "germany": "DE",
    "ar": "AR",
    "argentina": "AR",
}


def normalize_subsidiary(value: str | None) -> str | None:
    """Canonical code, or None for empty input. Unknown values pass through
    upper-cased so new filials work before getting an alias."""
    if value is None:
        return None
    stripped = value.strip()
    if not stripped:
        return None
    return ALIASES.get(stripped.lower(), stripped.upper())
