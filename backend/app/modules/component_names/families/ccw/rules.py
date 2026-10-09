"""Checkweigher (CCW): decide mono vs multi-track from the row's text.

Business rule (client): any hint that the machine handles several lanes wins;
with no hint at all the checkweigher is mono. The hours differ (mono 1.50,
multi 2.00), so the split matters.

The hint may sit in the English name or in the German description, so both are
searched. A hint is one of:

* a track count of 2 or more written next to its unit: "3-Spur", "2-times",
  "2-fach". A count of exactly 1 ("1-times", "1-fach") is mono, and a bare
  number is never a count: model numbers and belt widths ("CCW 200",
  "BB=375mm", "Hygieneausf. 530") must not be read as a track count.
* words that always mean several lanes: "tandem", "kombi".
* explicit multi words or spelled-out numbers: "mehrfach"/"mehrspur"/
  "mehrbahn"/"multi", "doppel"/"double"/"duo"/"twin"/"triple",
  "zwei"/"drei"/"vier".

Anything else is mono.
"""
import re

MONO = "mono"
MULTI = "multi"

# A count of two or more glued to the word that says what is counted.
_MULTI_UNIT_RE = re.compile(
    r"\b[2-9]\d*\s*-?\s*(?:times?|fach|fold|spur(?:en)?|bahn(?:en)?|track(?:s)?|way|ways|pleats?)\b",
    re.IGNORECASE,
)

# Words that by themselves mean several lanes or a doubled machine. Each stem
# is followed by \w* because German glues the suffix on ("Tandemwaage",
# "Kombiausführung", "Mehrfachausführung").
_MULTI_WORD_RE = re.compile(
    r"\b(?:tandem\w*|kombi\w*|mehrfach\w*|mehrspur\w*|mehrbahn\w*|multi\w*"
    r"|doppel\w*|double\w*|duo\w*|twin\w*|triple\w*|zwei\w*|drei\w*|vier\w*)",
    re.IGNORECASE,
)


def _is_multi(*texts: str | None) -> bool:
    return any(
        _MULTI_UNIT_RE.search(text) or _MULTI_WORD_RE.search(text)
        for text in texts
        if text
    )


def classify(name_en: str | None, description: str | None) -> str:
    """Return MULTI when any hint says several lanes, otherwise MONO."""
    return MULTI if _is_multi(name_en, description) else MONO
