"""Guardian offer numbering (Weber legacy format).

Observed in WeberAssistant OfferBuilder: the offer number embeds a kind
code ("-01-" Basic Kit, "-02-" Audit, "-03-" Off-Guardian). Pure helpers,
no DB. The core never imports this module.
"""

KIND_CODES: dict[str, str] = {
    "01": "Basic Kit",
    "02": "Audit",
    "03": "Off-Guardian",
}


def guardian_type_of(number: str) -> str | None:
    """Return the guardian type encoded in a legacy offer number, if any."""
    for code, name in KIND_CODES.items():
        if f"-{code}-" in number:
            return name
    return None


def build_number(prefix: str, year: int, seq: int, kind_code: str = "02") -> str:
    """Build a new legacy-style number. Raises ValueError on bad parts."""
    if not prefix or not prefix.strip():
        raise ValueError("prefix must be non-empty")
    if year < 2000 or year > 2100:
        raise ValueError("year must be between 2000 and 2100")
    if seq < 1:
        raise ValueError("seq must be >= 1")
    if kind_code not in KIND_CODES:
        raise ValueError(f"kind_code must be one of {sorted(KIND_CODES)}")
    return f"{prefix.strip()}-{kind_code}-{year}-{seq:04d}"
