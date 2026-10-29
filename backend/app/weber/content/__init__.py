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
- A SECTIONS entry with a ``modules`` tuple is included only when at least
  one of those Guardian modules is present in
  ``OfferDocument.guardian_selections``; ``None`` means always included.
- A ``{"type": "sub", "option"/"options": ...}`` wrapper is included only
  when one of its Guardian options is present in the selection.
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

# Ordered customer-facing assembly. ``modules`` lists the Guardian modules
# that publish the section (any of them); None means always included.
SECTIONS: tuple[dict[str, Any], ...] = (
    {"name": "cover", "section": cover, "modules": None},
    {"name": "master", "section": master, "modules": None},
    {"name": "annex1", "section": annex1, "modules": None},
    # Inspection and its report are always part of the agreement.
    {"name": "annex2", "section": annex2, "modules": None},
    {"name": "annex3", "section": annex3, "modules": ("customer_service",)},
    {"name": "annex4", "section": annex4, "modules": ("spare_parts",)},
    {"name": "annex5", "section": annex5, "modules": ("blade_solutions",)},
    # Training lives with optimization in the same annex.
    {"name": "annex6", "section": annex6, "modules": ("academy", "optimization")},
    # Performance reviews are optimization; cockpit and monitoring are digital.
    {"name": "annex7", "section": annex7, "modules": ("optimization", "digital_services")},
    {"name": "summary", "section": summary, "modules": None},
    {"name": "breakdown", "section": breakdown, "modules": None},
    {"name": "signatures", "section": signatures, "modules": None},
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


def _options_of(block: Block) -> frozenset[str]:
    """Gate keys of a ``sub`` block: ``option`` or ``options`` (any of)."""
    if "options" in block:
        return frozenset(block["options"])
    return frozenset((block["option"],))


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
        modules = entry["modules"]
        if modules is not None and not any(module in selections for module in modules):
            continue
        blocks = [
            block
            for block in entry["section"].BLOCKS
            if block.get("type") != "sub" or _options_of(block) & selections
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
