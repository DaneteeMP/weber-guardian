"""Document assembly and translation for the Guardian agreement PDF.

Responsibility
--------------
Define the ordered sections of the customer contract, the gates that decide
whether a section or subsection appears, and how per-node translations are
applied on top of the English source text.

Data flow
---------
  content/<section>.BLOCKS --(document_sections(selections))--> ordered
      (section_name, blocks) pairs; document_blocks() flattens them
  node id + locale         --(get_text(...))--> localized string
  The renderer (app.weber.pdf) consumes both to build the HTML.

Conventions
-----------
- English source text lives inline in the section modules (cover.py,
  master.py, annex1..7.py, summary.py); every translatable node carries a
  stable ``id``.
- Other locales (content/es.py, ...) provide partial ``MESSAGES`` dicts
  keyed by that node id. Missing ids fall back to the English source text.
- A SECTIONS entry with a ``module`` key is included only when that Guardian
  module is present in ``OfferDocument.guardian_selections``.
- A ``{"type": "sub", "option": ...}`` wrapper is included only when that
  Guardian option is present in the selection.
"""

from __future__ import annotations

from typing import Any, TypeVar

from app.weber.content import (
    annex1,
    annex2,
    annex3,
    annex4,
    annex5,
    annex6,
    annex7,
    breakdown,
    cover,
    de,
    es,
    it,
    labels,
    master,
    pt,
    signatures,
    summary,
)

Block = dict[str, Any]
_T = TypeVar("_T")

# Ordered customer-facing assembly. "module": None means always included.
SECTIONS: tuple[dict[str, Any], ...] = (
    {"name": "cover", "section": cover, "module": None},
    {"name": "master", "section": master, "module": None},
    {"name": "annex1", "section": annex1, "module": None},
    {"name": "annex2", "section": annex2, "module": "maintenance_inspection"},
    {"name": "annex3", "section": annex3, "module": "service_support"},
    {"name": "annex4", "section": annex4, "module": "parts_availability"},
    {"name": "annex5", "section": annex5, "module": "blade_solutions"},
    {"name": "annex6", "section": annex6, "module": "training_optimization"},
    {"name": "annex7", "section": annex7, "module": "digital_services"},
    {"name": "summary", "section": summary, "module": None},
    {"name": "breakdown", "section": breakdown, "module": None},
    {"name": "signatures", "section": signatures, "module": None},
)

# Partial translation catalogs. Locales without an entry simply fall back to
# the English source text for every node. Overrides are strings for text
# nodes and lists of strings for list nodes (ul, ol, dl, lines).
_CATALOGS: dict[str, dict[str, Any]] = {
    "es": es.MESSAGES,
    "de": de.MESSAGES,
    "pt": pt.MESSAGES,
    "it": it.MESSAGES,
}


def document_sections(selections: set[str]) -> list[tuple[str, list[Block]]]:
    """Return ``(section_name, blocks)`` for the given selection, in order.

    ``selections`` holds both module keys and option keys exactly as stored
    in ``OfferDocument.guardian_selections``. Sections gated by an unselected
    module are dropped and ``sub`` wrappers gated by an unselected option are
    removed inside the section, so the customer never receives a "not
    applicable" description. Returned nodes are the shared content nodes:
    callers must treat them as read-only.
    """
    sections: list[tuple[str, list[Block]]] = []
    for entry in SECTIONS:
        gate = entry["module"]
        if gate is not None and gate not in selections:
            continue
        blocks = [
            block
            for block in entry["section"].BLOCKS
            if block.get("type") != "sub" or block["option"] in selections
        ]
        sections.append((entry["name"], blocks))
    return sections


def document_blocks(selections: set[str]) -> list[Block]:
    """Flattened view of :func:`document_sections` for tests and tooling."""
    return [block for _, blocks in document_sections(selections) for block in blocks]


def get_text(locale: str, node_id: str, default: _T) -> _T:
    """Return the override for ``node_id`` in ``locale`` or the EN default."""
    override = _CATALOGS.get(locale, {}).get(node_id)
    return default if override is None else override


def node_text(locale: str, block: Block) -> str:
    """Translated text of an ``id``/``text`` node (h1, h2, p, ...)."""
    return get_text(locale, block["id"], block["text"])


__all__ = [
    "Block",
    "SECTIONS",
    "document_blocks",
    "document_sections",
    "get_text",
    "labels",
    "node_text",
]
