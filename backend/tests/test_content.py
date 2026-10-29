"""Structural tests for the Guardian PDF content package.

The content modules are data, so these tests enforce the schema contract the
renderer (B6) will rely on: unique and required node ids, allowed block
types, gates coherent with GUARDIAN_OPTIONS_BY_MODULE, tokens that exist in
the master template, and full translation catalogs (es, de, pt, it) that only
override real ids and cover every translatable node.
"""

from __future__ import annotations

import re
from pathlib import Path

import pypdfium2 as pdfium

from app.modules.offers.schemas import GUARDIAN_OPTIONS_BY_MODULE
from app.weber import content
from app.weber.content import labels

_TEMPLATE = (
    Path(__file__).resolve().parents[1]
    / "app"
    / "weber"
    / "templates"
    / "guardian_master_template.pdf"
)

ALLOWED_TYPES = {
    "h1",
    "h2",
    "p",
    "ul",
    "ol",
    "dl",
    "kv",
    "lines",
    "party",
    "commercial_breakdown",
    "band_rates",
    "equipment_table",
    "kv_table",
    "module_checklist",
    "signatures",
    "sub",
}

ALL_MODULES = set(GUARDIAN_OPTIONS_BY_MODULE)
ALL_OPTIONS = {option for options in GUARDIAN_OPTIONS_BY_MODULE.values() for option in options}
ALL_SELECTIONS = ALL_MODULES | ALL_OPTIONS

# Tokens introduced after the legacy master template PDF: they have no
# {{Token}} occurrence in that reference document, so the template check below
# must exempt them (they are still validated against token_values elsewhere).
POST_LEGACY_TOKENS = {"Guardian_Type"}


def _iter_nodes(blocks):
    for block in blocks:
        yield block
        if block.get("type") == "sub":
            yield from _iter_nodes(block["blocks"])


def _iter_all_nodes(blocks):
    """Yield every node including nested headers, fields, columns and rows."""
    for block in blocks:
        yield block
        if block.get("type") == "sub":
            yield from _iter_all_nodes(block["blocks"])
        for key in (
            "headers",
            "fields",
            "columns",
            "rows",
            "meta_right",
            "meta_left",
            "totals",
            "matrix_headers",
            "rate_headers",
        ):
            for item in block.get(key) or []:
                yield item
        if "company_label" in block:
            yield block["company_label"]


def _all_blocks():
    return content.document_blocks(ALL_SELECTIONS)


def _collect_ids(blocks):
    ids = []
    for block in _iter_nodes(blocks):
        if "id" in block:
            ids.append(block["id"])
        for key in (
            "headers",
            "fields",
            "columns",
            "meta_right",
            "meta_left",
            "totals",
            "matrix_headers",
            "rate_headers",
        ):
            for item in block.get(key) or []:
                ids.append(item["id"])
        if "company_label" in block:
            ids.append(block["company_label"]["id"])
        for row in block.get("rows") or []:
            if "id" in row:
                ids.append(row["id"])
    return ids


def _template_tokens() -> set[str]:
    """Whitespace-insensitive {{Token}} names extracted from the master PDF."""
    document = pdfium.PdfDocument(str(_TEMPLATE))
    tokens: set[str] = set()
    try:
        for index in range(len(document)):
            text = document[index].get_textpage().get_text_bounded()
            compact = re.sub(r"\s+", "", text)
            tokens.update(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", compact))
    finally:
        document.close()
    return tokens


def test_every_section_exports_blocks():
    for entry in content.SECTIONS:
        assert isinstance(entry["section"].BLOCKS, list)
        assert entry["section"].BLOCKS, f"{entry['section']} has no blocks"


def test_node_ids_are_required_and_unique():
    ids = _collect_ids(_all_blocks())
    assert all(ids), "every node must carry a non-empty id"
    duplicates = {value for value in ids if ids.count(value) > 1}
    assert not duplicates, f"duplicate node ids: {sorted(duplicates)}"


def test_block_types_are_known():
    types = {block["type"] for block in _iter_nodes(_all_blocks())}
    unknown = types - ALLOWED_TYPES
    assert not unknown, f"unknown block types: {sorted(unknown)}"


def test_text_shapes():
    for block in _iter_nodes(_all_blocks()):
        kind = block["type"]
        if kind in {"h1", "h2", "p"}:
            assert block["text"], f"{block['id']} has no text"
        elif kind in {"ul", "ol", "dl", "lines"}:
            assert block["items"], f"{block['id']} has no items"
        elif kind == "kv":
            assert block["label"]
            assert ("token" in block) ^ ("value" in block), block["id"]
        elif kind == "party":
            assert block["label"] and block["name_token"] and block["alias"]
            assert block["address_tokens"]
        elif kind == "dl":
            for item in block["items"]:
                assert ": " in item, f"definition without term separator: {item!r}"


def test_sub_gates_belong_to_their_module():
    for entry in content.SECTIONS:
        module = entry["module"]
        blocks = entry["section"].BLOCKS
        if module is None:
            assert not [b for b in blocks if b["type"] == "sub"], (
                f"{entry['section']} must not contain gated subs"
            )
            continue
        options = set(GUARDIAN_OPTIONS_BY_MODULE[module])
        for block in blocks:
            if block["type"] == "sub":
                assert block["option"] in options, (
                    f"{block['option']} is not an option of {module}"
                )


def test_module_gates_are_valid():
    for entry in content.SECTIONS:
        module = entry["module"]
        if module is not None:
            assert module in ALL_MODULES, f"unknown module gate: {module}"


def test_kv_table_rows_have_label_or_module():
    for block in _iter_nodes(_all_blocks()):
        if block["type"] != "kv_table":
            continue
        for row in block["rows"]:
            has_id = "id" in row
            has_module = "module" in row
            assert has_id ^ has_module, f"row needs id or module: {row}"
            assert row.get("token"), f"row without token: {row}"


def test_document_blocks_gating():
    bare = content.document_blocks(set())
    titles = [b["text"] for b in bare if b["type"] == "h1"]
    assert titles == [
        "MAINTENANCE CONTRACT",
        "ANNEX 1 - EQUIPMENT & COMMERCIAL SCHEDULE",
        "GUARDIAN CONFIGURATION SUMMARY",
        "ANNEX 1, List of machines and modules",
        "SIGNATURES",
    ]

    module_only = content.document_blocks({"maintenance_inspection"})
    module_titles = [b["text"] for b in module_only if b["type"] == "h1"]
    assert "ANNEX 2 - MAINTENANCE & INSPECTION" in module_titles
    module_text = " ".join(
        b.get("text", "") for b in _iter_nodes(module_only) if b.get("type") in {"h1", "h2"}
    )
    assert "S301 Scheduled Technical Inspection" not in module_text, "option sub must drop without its option"

    full = content.document_blocks(ALL_SELECTIONS)
    full_text = " ".join(
        b.get("text", "") for b in _iter_nodes(full) if b.get("type") in {"h1", "h2"}
    )
    assert "S301 Scheduled Technical Inspection" in full_text
    assert "S104 On-site Service & Priority Response" in full_text


def test_content_tokens_exist_in_master_template():
    known = _template_tokens()
    used: set[str] = set()
    for block in _iter_nodes(_all_blocks()):
        for field in ("text", "value"):
            value = block.get(field)
            if isinstance(value, str):
                used.update(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", value))
        for item in block.get("items") or []:
            used.update(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", item))
        if "token" in block:
            used.add(block["token"])
        if "name_token" in block:
            used.add(block["name_token"])
        used.update(block.get("address_tokens") or [])
        for key in ("meta_right", "meta_left", "totals"):
            for entry in block.get(key) or []:
                if "token" in entry:
                    used.add(entry["token"])
        for item in block.get("customer") or []:
            used.update(re.findall(r"\{\{([A-Za-z0-9_]+)\}\}", item))
        for row in block.get("rows") or []:
            if "token" in row:
                used.add(row["token"])
        for column in block.get("columns") or []:
            if "company_token" in column:
                used.add(column["company_token"])
    missing = used - known - POST_LEGACY_TOKENS
    assert not missing, f"tokens not present in master template: {sorted(missing)}"


def test_module_and_option_labels_cover_the_domain():
    assert set(labels.MODULE_LABELS) == ALL_MODULES
    assert len(labels.MODULES) == len(ALL_MODULES)
    assert set(labels.OPTION_LABELS) == ALL_OPTIONS


# Nodes that must not appear in the catalogs: container nodes carry no text
# of their own (their nested headers/rows are translated separately), and
# pure-token nodes hold only {{Token}} placeholders that must survive
# verbatim (party addresses, special-conditions slot, module checklist).
NON_TRANSLATABLE_NODES = {
    "cover.executor",
    "cover.customer",
    "breakdown",
    "annex3.rates",
    "annex1.equipment",
    "annex1.modules",
    "annex1.summary",
    "summary.scope",
    "summary.signatures",
    "annex1.special.conditions",
}

FULL_CATALOGS = {
    "es": content.es.MESSAGES,
    "de": content.de.MESSAGES,
    "pt": content.pt.MESSAGES,
    "it": content.it.MESSAGES,
}


def _valid_catalog_ids() -> set[str]:
    node_ids = set(_collect_ids(_all_blocks()))
    valid = set(node_ids)
    valid.update(f"module.{module}" for module in labels.MODULES)
    valid.update(f"guardian_type.{key}" for key in labels.GUARDIAN_TYPE_LABELS)
    for block in _iter_nodes(_all_blocks()):
        if block["type"] == "kv" and "value" in block:
            valid.add(f"{block['id']}.value")
        if block["type"] == "party":
            valid.add(f"{block['id']}.label")
            valid.add(f"{block['id']}.alias")
    return valid


def test_full_catalogs_override_only_existing_ids():
    valid = _valid_catalog_ids()
    for locale, catalog in FULL_CATALOGS.items():
        unknown = set(catalog) - valid
        assert not unknown, f"{locale}.py overrides unknown ids: {sorted(unknown)}"
        assert catalog, f"{locale}.py must not be empty"
        for module in labels.MODULES:
            assert f"module.{module}" in catalog, f"{locale}.py missing module.{module}"
        for key in labels.GUARDIAN_TYPE_LABELS:
            assert f"guardian_type.{key}" in catalog, f"{locale}.py missing guardian_type.{key}"


def test_full_catalogs_shapes_match_nodes():
    node_by_id = {}
    for node in _iter_all_nodes(_all_blocks()):
        if "id" in node:
            node_by_id[node["id"]] = node
    for locale, catalog in FULL_CATALOGS.items():
        for node_id, override in catalog.items():
            if node_id.startswith(("module.", "guardian_type.")) or node_id.endswith(
                (".value", ".label", ".alias")
            ):
                assert isinstance(override, str), f"{locale}:{node_id}"
                continue
            node = node_by_id[node_id]
            if "items" in node:
                assert isinstance(override, list), f"{locale}:{node_id}"
            else:
                assert isinstance(override, str), f"{locale}:{node_id}"


def test_full_catalogs_cover_all_translatable_ids():
    required = _valid_catalog_ids() - NON_TRANSLATABLE_NODES
    for locale, catalog in FULL_CATALOGS.items():
        missing = required - set(catalog)
        assert not missing, f"{locale}.py missing translations: {sorted(missing)}"


def test_get_text_fallback():
    assert content.get_text("en", "cover.title", "MAINTENANCE CONTRACT") == "MAINTENANCE CONTRACT"
    assert content.get_text("de", "cover.title", "MAINTENANCE CONTRACT") == "WARTUNGSVERTRAG"
    assert content.get_text("es", "cover.title", "MAINTENANCE CONTRACT") == "CONTRATO DE MANTENIMIENTO"
    assert content.node_text("es", {"id": "cover.title", "text": "MAINTENANCE CONTRACT"}) == (
        "CONTRATO DE MANTENIMIENTO"
    )
