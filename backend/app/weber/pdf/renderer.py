"""WeasyPrint + Jinja2 renderer for the Guardian agreement PDF.

Responsibility: turn an OfferDocument into the customer contract PDF.

Pipeline (all document rules stay in this backend layer; the template only
lays out the resolved view models):
  1. document_locale + token_values   -> {{Token}} data for this document
  2. content.document_sections        -> gated section/block structure
  3. _resolve_block per node          -> translated text, resolved tokens,
                                         dynamic rows (equipment, checklist,
                                         scope tables) from the document
  4. Jinja2 document.html + BASE_CSS  -> HTML (autoescaped view strings)
  5. WeasyPrint                       -> PDF bytes with selectable text

Who uses it: app.weber.pdf.__init__ (re-exported as build_offer_pdf) and
tests/test_renderer.py.
"""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

from app.modules.offers.document import OfferDocument
from app.weber import content
from app.weber.content import labels
from app.weber.layout import BASE_CSS
from app.weber.locales import format_money
from app.weber.pdf.values import (
    document_locale,
    executor_is_provisional,
    machine_groups,
    resolve_tokens,
    token_values,
)

_WEBER_DIR = Path(__file__).resolve().parent.parent
_ASSETS_DIR = _WEBER_DIR / "assets"
_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

# Legacy cover banner when the subsidiary has no legal executor data.
_DRAFT_BANNER = "DRAFT - SUBSIDIARY LEGAL DETAILS REQUIRED"

_ENV = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(("html",)),
)


def render_document(doc: OfferDocument) -> bytes:
    """Render the customer Guardian agreement for this document as PDF bytes."""
    locale = document_locale(doc)
    values = token_values(doc, locale)
    selections = set(doc.guardian_selections)
    sections = _resolve_sections(doc, locale, values, selections)
    _insert_custom_annexes(sections, doc)
    draft_banner = (
        content.get_text(locale, "cover.draft_banner", _DRAFT_BANNER)
        if executor_is_provisional(doc)
        else None
    )
    html = _ENV.get_template("document.html").render(
        lang=locale,
        title=f"Guardian Agreement {doc.number}",
        base_css=BASE_CSS,
        weber_logo_uri=(_ASSETS_DIR / "weber-logo.png").as_uri(),
        cover_logo_uri=(_ASSETS_DIR / "guardian-logo.png").as_uri(),
        draft_banner=draft_banner,
        sections=sections,
    )
    return HTML(string=html, base_url=str(_WEBER_DIR)).write_pdf()


def _insert_custom_annexes(sections: list[dict], doc: OfferDocument) -> None:
    """Insert customer-authored annexes right before the summary section.

    The summary ends with the signature page, so custom annexes must come
    before it. Each annex is one page: its h1 sits mid-document and therefore
    always carries page_break (the first-block exception belongs to the cover).
    Text is printed verbatim - no translation and no {{Token}} resolution:
    it is user input, and a stray brace must never break the render.
    """
    if not doc.custom_annexes:
        return
    views = []
    for annex in doc.custom_annexes:
        blocks = [{"type": "h1", "text": annex.title, "page_break": True}]
        if annex.body_html:
            # Sanitized HTML from the uploaded .docx (offers.docx_annex):
            # only <p>, <strong>, <em>, <table> and friends are ever stored,
            # so it is inserted as trusted content next to the token blocks.
            blocks.append({"type": "html", "html": annex.body_html})
        else:
            blocks.extend(
                {"type": "p", "text": line.strip()}
                for line in annex.body.splitlines()
                if line.strip()
            )
        views.append({"name": "custom", "blocks": blocks})
    position = next(
        (index for index, section in enumerate(sections) if section["name"] == "summary"),
        len(sections),
    )
    sections[position:position] = views


def _resolve_sections(doc, locale, values, selections) -> list[dict]:
    """Resolve every section of the gated document, in order.

    The very first block of the document must not force a page break; every
    later h1 (section title) starts a new page, like the master template.
    """
    sections: list[dict] = []
    seen_block = False
    for name, blocks in content.document_sections(selections):
        resolved = []
        for block in _flatten(blocks):
            view = _resolve_block(block, doc, locale, values, selections)
            if view["type"] == "h1":
                view["page_break"] = seen_block
            seen_block = True
            resolved.append(view)
        sections.append({"name": name, "blocks": resolved})
    return sections


def _flatten(blocks: list[content.Block]) -> list[content.Block]:
    """Ungate already-selected sub wrappers into a flat block list."""
    flat: list[content.Block] = []
    for block in blocks:
        if block["type"] == "sub":
            flat.extend(block["blocks"])
        else:
            flat.append(block)
    return flat


def _resolve_block(block, doc, locale, values, selections) -> dict:
    """Build the template view model for one content node."""
    kind = block["type"]

    if kind in {"h1", "h2", "p"}:
        text = resolve_tokens(content.node_text(locale, block), values)
        view = {"type": kind, "text": text}
        if "class" in block:
            view["class"] = block["class"]
        return view

    if kind in {"ul", "ol", "lines"}:
        return {"type": kind, "items": _translated_items(locale, block, values)}

    if kind == "dl":
        items = []
        for raw in _translated_items(locale, block, values):
            term, separator, definition = raw.partition(": ")
            if not separator:
                raise ValueError(f"definition without term separator: {raw!r}")
            items.append({"term": term, "definition": resolve_tokens(definition, values)})
        return {"type": "dl", "items": items}

    if kind == "kv":
        label = content.get_text(locale, block["id"], block["label"])
        if "token" in block:
            value = values[block["token"]]
        else:
            raw = content.get_text(locale, f"{block['id']}.value", block["value"])
            value = resolve_tokens(raw, values)
        return {"type": "kv", "label": label, "value": value}

    if kind == "equipment_table":
        headers = [
            content.get_text(locale, header["id"], header["text"])
            for header in block["headers"]
        ]
        return {"type": kind, "headers": headers, "rows": _equipment_rows(doc, values)}

    if kind == "kv_table":
        headers = [
            content.get_text(locale, header["id"], header["text"])
            for header in block["headers"]
        ]
        rows = []
        for row in block["rows"]:
            if "module" in row:
                label = content.get_text(
                    locale, f"module.{row['module']}", labels.MODULE_LABELS[row["module"]]
                )
            else:
                label = content.get_text(locale, row["id"], row["label"])
            rows.append(
                {
                    "label": label,
                    "value": values[row["token"]],
                    "total": row.get("total", False),
                }
            )
        return {"type": kind, "headers": headers, "rows": rows}

    if kind == "module_checklist":
        items = []
        for module in labels.MODULES:
            label = content.get_text(
                locale, f"module.{module}", labels.MODULE_LABELS[module]
            )
            mark = "x" if module in selections else " "
            items.append(f"[{mark}] {label}")
        return {"type": kind, "items": items}

    if kind == "signatures":
        company_label = content.get_text(
            locale, block["company_label"]["id"], block["company_label"]["label"]
        )
        columns = [
            {
                "heading": content.get_text(locale, column["id"], column["heading"]),
                "company": values[column["company_token"]],
            }
            for column in block["columns"]
        ]
        fields = [
            {"label": content.get_text(locale, field["id"], field["label"])}
            for field in block["fields"]
        ]
        return {"type": kind, "company_label": company_label, "columns": columns, "fields": fields}

    if kind == "party":
        label = content.get_text(locale, f"{block['id']}.label", block["label"])
        alias = content.get_text(locale, f"{block['id']}.alias", block["alias"])
        address = [values[token] for token in block["address_tokens"] if values[token]]
        return {
            "type": kind,
            "label": label,
            "name": values[block["name_token"]],
            "address": address,
            "alias": alias,
        }

    if kind == "commercial_breakdown":
        customer = [
            line
            for line in (resolve_tokens(item, values) for item in block["customer"])
            if line.strip()
        ]
        return {
            "type": kind,
            "customer": customer,
            "meta_right": [
                {
                    "label": content.get_text(locale, item["id"], item["label"]),
                    "value": values[item["token"]],
                }
                for item in block["meta_right"]
            ],
            "meta_left": [
                {
                    "label": content.get_text(locale, item["id"], item["label"]),
                    "value": values[item["token"]],
                }
                for item in block["meta_left"]
            ],
            "columns": [
                content.get_text(locale, column["id"], column["text"])
                for column in block["columns"]
            ],
            "rows": _line_item_rows(doc, locale),
            "totals": [
                {
                    "label": content.get_text(locale, total["id"], total["label"]),
                    "value": values[total["token"]],
                    "total": total.get("total", False),
                }
                for total in block["totals"]
            ],
        }

    raise ValueError(f"unknown block type: {kind!r}")


def _translated_items(locale, block, values) -> list[str]:
    """Translate a whole list node (single override per list) and resolve tokens."""
    translated = content.get_text(locale, block["id"], block["items"])
    if isinstance(translated, str):
        raise ValueError(f"list override must be a list of strings: {block['id']!r}")
    return [resolve_tokens(item, values) for item in translated]


def _line_item_rows(doc: OfferDocument, locale: str) -> list[list[str]]:
    """One row per offer line: line number, module, formatted amount."""
    rows: list[list[str]] = []
    for line in doc.lines:
        module = " ".join(part for part in (line.equipment, line.description) if part)
        rows.append([str(line.pos), module, format_money(line.import_amount, locale, doc.currency)])
    return rows


def _equipment_rows(doc: OfferDocument, values: dict[str, str]) -> list[list[str]]:
    """One table row per machine in the offer, in first-seen order.

    The master template has separate Production Line and Machine columns but
    the offer data holds a single equipment name, so both columns show it
    (the legacy renderer did the same with its Line_N/Machine_N tokens).
    Serial and type have no data source yet and stay empty, like legacy.
    """
    rows: list[list[str]] = []
    for name, group in machine_groups(doc.lines):
        modules = ", ".join(
            dict.fromkeys(line.description for line in group if line.description)
        )
        rows.append([name, name, "", "", modules, values["Inspection_Frequency"]])
    return rows
