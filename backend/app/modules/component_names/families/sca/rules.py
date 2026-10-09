"""Product scanner (SCA): mono vs multi-track, read from the row's text.

The dictionary marks the multi-track scanners in words only: "multi-track" in
the English name, "mehrspurig" in the German description. Everything else is a
single-track scanner.
"""
import re

MONO = "mono"
MULTI = "multi"

_MULTI_RE = re.compile(r"multi\s*-?\s*track\w*|mehrspur\w*", re.IGNORECASE)


def classify(name_en: str | None, description: str | None) -> str:
    """Return MULTI when the row says multi-track, otherwise MONO."""
    for text in (name_en, description):
        if text and _MULTI_RE.search(text):
            return MULTI
    return MONO
