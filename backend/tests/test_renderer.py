"""End-to-end tests for the WeasyPrint renderer (no database involved).

Each test builds a minimal OfferDocument, renders the PDF and reads the
extracted text back with pypdfium2, so the assertions cover the real output
a customer would see: gating, token resolution, locale formatting and the
dynamic rows.
"""

from __future__ import annotations

import os
import re
import tempfile
import uuid
from datetime import date
from decimal import Decimal

import pypdfium2 as pdfium

from app.modules.offers.document import CustomAnnex, OfferDocument, OfferLine
from app.modules.offers.schemas import GUARDIAN_OPTIONS_BY_MODULE
from app.weber import content
from app.weber.pdf import renderer, values


def _doc(**overrides) -> OfferDocument:
    base = dict(
        offer_id=uuid.uuid4(),
        number="OFF-2026-001",
        offer_date=date(2026, 9, 21),
        status="draft",
        language="en",
        inspection_frequency="2 visits / year",
        responsible_person=None,
        subsidiary_id="ES",
        account_name="ACME Foods S.L.",
        account_city="Madrid",
        account_province=None,
        account_country="Espana",
        currency="EUR",
        trip_cost=Decimal("0"),
        diets=Decimal("0"),
        hotel_cost=Decimal("0"),
        trip_hours=Decimal("0"),
        work_hours=Decimal("0"),
        bk_hours=Decimal("0"),
        report_hours=Decimal("0"),
        total_hours=Decimal("0"),
        hours_import=Decimal("1000"),
        expenses=Decimal("0"),
        discount=Decimal("100"),
        bk_price=Decimal("500"),
        total=Decimal("1400"),
        total_end=Decimal("1800"),
        general_comments="Special conditions apply.",
        guardian_selections=(
            "maintenance_inspection",
            "inspection",
            "service_support",
            "standard_hotline",
        ),
        customer_number="12345",
        customer_site="Planta Madrid",
        lines=(
            OfferLine(1, "LINEA 1", "Inspection kit", Decimal("1000")),
            OfferLine(2, "LINEA 1", "Spare parts", Decimal("400")),
            OfferLine(3, "LINEA 2", "Blade program", Decimal("600")),
        ),
    )
    base.update(overrides)
    return OfferDocument(**base)


def _pdf_text(pdf: bytes) -> str:
    handle = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    try:
        handle.write(pdf)
        handle.close()
        document = pdfium.PdfDocument(handle.name)
        try:
            pages = [
                document[index].get_textpage().get_text_bounded()
                for index in range(len(document))
            ]
        finally:
            document.close()
        return "\n".join(pages)
    finally:
        os.unlink(handle.name)


def test_render_selectable_text_and_resolved_tokens():
    pdf = renderer.render_document(_doc())
    assert pdf.startswith(b"%PDF")
    text = _pdf_text(pdf)

    # Master agreement body (legacy contract: 0 + I-IX)
    assert "I. PURPOSE OF THE CONTRACT" in text
    assert "IX. PLACE OF JURISDICTION" in text
    # Tokens resolved from the document data
    assert "OFF-2026-001" in text
    assert "ACME Foods S.L." in text
    assert "WEBER FOOD TECHNOLOGY IB" in text
    # Dynamic values
    assert "Special conditions apply." in text
    assert "Inspection kit" in text
    assert "Blade program" in text
    # No unresolved placeholders may reach the customer
    assert "{{" not in text
    # Signatures page
    assert "For the Customer" in text
    assert "For Weber" in text


def test_module_and_option_gating():
    text = _pdf_text(renderer.render_document(_doc()))

    # Module and option both selected: annex and subsection present
    assert "ANNEX 2 - MAINTENANCE & INSPECTION" in text
    assert "S301 Scheduled Technical Inspection" in text
    assert "ANNEX 3 - SERVICE SUPPORT" in text
    assert "S101 Standard Hotline" in text
    # Module selected but option absent inside it: subsection dropped
    assert "3. Remote Support" not in text
    assert "S303 Preventive Maintenance" not in text
    # Module not selected: the whole annex is dropped
    assert "ANNEX 4 - PARTS & AVAILABILITY" not in text
    assert "ANNEX 7 - DIGITAL SERVICES" not in text


def test_empty_billing_section_heading_is_hidden():
    """The billing rows have no data yet, so the whole section (heading and
    rows) is omitted instead of printing an empty title."""
    text = _pdf_text(renderer.render_document(_doc()))
    assert "5. Billing" not in text


def test_special_conditions_heading_hidden_when_empty():
    text = _pdf_text(renderer.render_document(_doc(general_comments="")))
    assert "6. Special Commercial Conditions" not in text


def test_rate_table_heading_hidden_without_band_rates():
    """The rates heading and table disappear together when the subsidiary has
    no band rates configured (the fixture has none)."""
    text = _pdf_text(renderer.render_document(_doc()))
    assert "S101 Standard Hotline" in text
    assert "2. Service Rates" not in text


def test_selected_scope_and_checklist_marks():
    text = _pdf_text(renderer.render_document(_doc()))
    # Checklist marks every module, checked only when selected
    assert "[x] Maintenance & Inspection" in text
    assert "[ ] Digital Services" in text
    # Selected_*_Options scope tokens join the selected option labels
    assert "Inspection / Annual Inspection" in text


def test_spanish_locale_formats_money_and_titles():
    text = _pdf_text(renderer.render_document(_doc(language="Spanish")))
    assert "CONTRATO DE MANTENIMIENTO" in text
    assert "Cliente" in text
    # total_end 1800.00 EUR in es format: thousands point, decimal comma
    assert "1.800,00" in text
    # offer_date 21 September 2026 in es long format
    assert "21 de septiembre de 2026" in text


def test_every_machine_gets_a_row():
    text = _pdf_text(renderer.render_document(_doc()))
    assert text.count("LINEA 1") >= 2  # production line and machine columns
    assert "LINEA 2" in text
    assert "2 visits / year" in text  # frequency column for every machine


def test_resolve_tokens_rejects_unknown_token():
    known = values.token_values(_doc(), "en")
    try:
        values.resolve_tokens("{{Not_A_Token}}", known)
    except ValueError as error:
        assert "Not_A_Token" in str(error)
    else:
        raise AssertionError("unknown token must raise ValueError")


def test_values_cover_every_content_token():
    all_options = {
        option
        for options in GUARDIAN_OPTIONS_BY_MODULE.values()
        for option in options
    }
    selections = set(GUARDIAN_OPTIONS_BY_MODULE) | all_options
    pattern = re.compile(r"\{\{([A-Za-z0-9_]+)\}\}")
    used: set[str] = set()

    def walk(blocks):
        for block in blocks:
            if block.get("type") == "sub":
                walk(block["blocks"])
                continue
            for field in ("text", "value"):
                value = block.get(field)
                if isinstance(value, str):
                    used.update(pattern.findall(value))
            for item in block.get("items") or []:
                used.update(pattern.findall(item))
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
                used.update(pattern.findall(item))
            for row in block.get("rows") or []:
                if "token" in row:
                    used.add(row["token"])
            for column in block.get("columns") or []:
                if "company_token" in column:
                    used.add(column["company_token"])

    walk(content.document_blocks(selections))
    known = set(values.token_values(_doc(), "en"))
    missing = used - known
    assert not missing, f"content tokens missing from token_values: {sorted(missing)}"


def test_custom_annexes_render_before_the_signatures_verbatim():
    pdf = renderer.render_document(
        _doc(
            custom_annexes=(
                CustomAnnex(
                    title="ANNEX X - SERVICE LEVEL ADDENDUM",
                    body="Response within four working hours.\n\n{{Not_A_Token}} stays literal.",
                ),
            )
        )
    )
    text = _pdf_text(pdf)
    # Own heading and paragraphs, before the signature page (last section).
    assert "ANNEX X - SERVICE LEVEL ADDENDUM" in text
    assert "Response within four working hours." in text
    assert "{{Not_A_Token}} stays literal." in text
    assert text.index("ANNEX X - SERVICE LEVEL ADDENDUM") < text.index("SIGNATURES")
