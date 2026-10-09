"""Per-family classifiers: turn one dictionary row into a workload variant.

Every family lives in its own folder next to this file (one folder per family)
so the rules stay small and reviewable instead of growing into one big file. A
family exposes ``classify(name_en, description) -> str``.

``classify_family`` dispatches by the row's ``type_code`` (the legacy short
code) and returns ``None`` when the family has no classifier yet. ``None``
means "undecided", never "mono": the caller must not read it as a decision.
"""
from app.modules.component_names.families import ccw, sca

_CLASSIFIERS = {
    "CCW": ccw.classify,
    "SCA": sca.classify,
}


def classify_family(
    type_code: str | None,
    name_en: str | None,
    description: str | None,
) -> str | None:
    """Return the family variant for one row, or None when there is no classifier."""
    classify = _CLASSIFIERS.get((type_code or "").strip().upper())
    if classify is None:
        return None
    return classify(name_en, description)


def registered_families() -> tuple[str, ...]:
    """Type codes that already have a classifier."""
    return tuple(sorted(_CLASSIFIERS))


__all__ = ["classify_family", "registered_families", "ccw", "sca"]
