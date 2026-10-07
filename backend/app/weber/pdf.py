"""Render the Guardian contract from Weber's supplied PDF master.

The source pages are rasterized before customer-specific content is applied.
This keeps the original page design intact and ensures removed service text
cannot remain hidden in the delivered PDF.
"""
import io
import re
from dataclasses import dataclass
from pathlib import Path

import pypdfium2 as pdfium
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen.canvas import Canvas

from app.core.subsidiaries import EXECUTOR_CODES, normalize_subsidiary
from app.modules.offers.document import OfferDocument, OfferLine
from app.modules.offers.schemas import GUARDIAN_OPTIONS_BY_MODULE
from app.weber import contract_es

_ROOT = Path(__file__).resolve().parent
_TEMPLATE = _ROOT / "templates" / "guardian_master_template.pdf"
_GUARDIAN_LOGO = _ROOT / "assets" / "guardian-logo.png"
_WEBER_LOGO = _ROOT / "assets" / "weber-logo.png"
_RENDER_SCALE = 2.0
_RULE_PATTERN = re.compile(
    r"INTERNAL GENERATION RULE\s*-\s*REMOVE FROM CUSTOMER COPY:.*?"
    r"(?:selected|configuration)\.",
    re.IGNORECASE | re.DOTALL,
)
_PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Za-z0-9_]+\}\}")
_PAGE_NUMBER_PATTERN = re.compile(r"Page\s+\d+", re.IGNORECASE)
_TEMPLATE_NOTE_PATTERN = re.compile(
    r"Internal template note:.*?rollout\.", re.IGNORECASE | re.DOTALL
)

# The supplied master is 27 pages: page 2 is an internal assembly instruction;
# Annex 1, the master agreement, summary and signatures are always retained.
_BASE_PAGES = set(range(3, 12)) | {26, 27}
_ANNEX_PAGES = {
    "maintenance_inspection": range(12, 15),
    "service_support": range(15, 17),
    "parts_availability": range(17, 19),
    "blade_solutions": range(19, 21),
    "training_optimization": range(21, 24),
    "digital_services": range(24, 26),
}
_OPTION_ONLY_PAGES = {
    16: ("priority_response",),
    20: ("sharpening_assessment", "blade_application_review"),
    25: ("mro_review", "dedicated_account_team"),
}
_MODULE_LABELS = {
    "Maintenance & Inspection": "maintenance_inspection",
    "Service Support": "service_support",
    "Parts & Availability": "parts_availability",
    "Blade Solutions": "blade_solutions",
    "Training & Optimization": "training_optimization",
    "Digital Services": "digital_services",
}

_OPTION_LABELS = {
    "inspection": "Inspection / Annual Inspection",
    "machine_checklist": "Machine Checklist",
    "inspection_report": "Inspection Report",
    "preventive_maintenance": "Preventive Maintenance",
    "maintenance_kit": "Spare Parts / Maintenance Kit",
    "standard_hotline": "Standard Hotline",
    "remote_support": "Remote Support",
    "priority_response": "Priority Response",
    "parts_discount": "Parts Discount",
    "priority_handling": "Priority Handling",
    "recommended_parts_list": "Recommended Parts List",
    "blade_discount": "Blade Discount",
    "stock_agreement": "Stock Agreement",
    "sharpening_assessment": "Sharpening Assessment",
    "blade_application_review": "Blade Application Review",
    "operator_training": "Operator Training",
    "maintenance_training": "Maintenance Training",
    "line_optimization": "Line Optimization",
    "epip_audit": "EPIP Audit",
    "factory_cockpit": "Factory Cockpit",
    "performance_review": "Performance Review",
    "mro_review": "MRO Review",
    "dedicated_account_team": "Dedicated Account Team",
}

_OPTION_RULE_TEXT = {
    "inspection": "Inspection / Annual Inspection",
    "machine_checklist": "Machine Checklist",
    "inspection_report": "Inspection Report",
    "preventive_maintenance": "Preventive Maintenance",
    "maintenance_kit": "Spare Parts or Maintenance Kit",
    "standard_hotline": "Standard Hotline",
    "remote_support": "Remote Support",
    "priority_response": "Priority Response",
    "parts_discount": "Parts Discount",
    "priority_handling": "Priority Handling",
    "recommended_parts_list": "Recommended Parts List",
    "blade_discount": "Blade Discount",
    "stock_agreement": "Stock Agreement",
    "sharpening_assessment": "Sharpening Assessment",
    "blade_application_review": "Blade Application Review",
    "operator_training": "Operator Training",
    "maintenance_training": "Maintenance Training",
    "line_optimization": "Line Optimization",
    "epip_audit": "EPIP Audit",
    "factory_cockpit": "Factory Cockpit",
    "performance_review": "Performance Review",
    "mro_review": "MRO Review",
    "dedicated_account_team": "Dedicated Account Team",
}

_OPTION_HEADINGS = {
    "inspection": "2. Inspection",
    "machine_checklist": "3. Machine Checklist",
    "inspection_report": "4. Inspection Report",
    "preventive_maintenance": "5. Preventive Maintenance",
    "maintenance_kit": "6. Spare Parts / Maintenance Kit",
    "standard_hotline": "2. Standard Hotline",
    "remote_support": "3. Remote Support",
    "priority_response": "4. Priority Response",
    "parts_discount": "2. Parts Discount",
    "priority_handling": "3. Priority Handling",
    "recommended_parts_list": "4. Recommended Parts List",
    "blade_discount": "1. Blade Discount",
    "stock_agreement": "2. Stock Agreement",
    "sharpening_assessment": "3. Sharpening Assessment",
    "blade_application_review": "4. Blade Application Review",
    "operator_training": "1. Operator Training",
    "maintenance_training": "2. Maintenance Training",
    "line_optimization": "3. Line Optimization",
    "epip_audit": "4. EPIP Audit",
    "factory_cockpit": "1. Factory Cockpit",
    "performance_review": "2. Performance Review",
    "mro_review": "3. MRO Review",
    "dedicated_account_team": "4. Dedicated Account Team",
}

_ALWAYS_INCLUDED_SECTION_HEADINGS = (
    "1. Purpose",
    "7. Additional Maintenance and Repairs",
    "8. Inspection Frequency",
    "9. Service Hours",
    "5. Delivery Conditions",
    "5. Follow-Up",
)
_ALL_SECTION_HEADINGS = tuple(_OPTION_HEADINGS.values()) + _ALWAYS_INCLUDED_SECTION_HEADINGS
_OPTION_MODULE = {
    option: module
    for module, options in GUARDIAN_OPTIONS_BY_MODULE.items()
    for option in options
}


@dataclass(frozen=True)
class _TextLine:
    """One line of source PDF text and its PDF-point bounding box."""

    page_number: int
    text: str
    start: int
    end: int
    box: tuple[float, float, float, float]


def _language(doc: OfferDocument) -> str:
    """Reject unknown UI language values; the supplied agreement body is English."""
    normalized = (doc.language or "").strip().lower()
    if normalized in {"english", "en", "spanish", "es", "portuguese", "pt"}:
        return normalized[:2]
    raise ValueError(f"unsupported PDF language: {doc.language!r}")


DEFAULT_SUBSIDIARY = "ES"


def _PROVISIONAL_BLOCK(canonical: str) -> dict[str, str]:
    """Return a visible draft block without inventing subsidiary legal details."""
    return {
        "name": canonical,
        "street": "",
        "city": "",
        "country": "",
        "place_date": "",
    }


def _executor(doc: OfferDocument) -> tuple[dict[str, str], bool]:
    """Resolve the Weber legal entity from the customer's owning subsidiary."""
    canonical = normalize_subsidiary(doc.subsidiary_id) or DEFAULT_SUBSIDIARY
    code = EXECUTOR_CODES.get(canonical, canonical)
    block = contract_es.EXECUTORS.get(code)
    if block is None:
        return _PROVISIONAL_BLOCK(canonical), True
    return block, False


def _selected_pages(selections: set[str]) -> list[int]:
    """Return 1-based source pages for the customer copy in original order."""
    pages = set(_BASE_PAGES)
    for module, annex_pages in _ANNEX_PAGES.items():
        if module in selections:
            pages.update(annex_pages)
    for page_number, options in _OPTION_ONLY_PAGES.items():
        if not any(option in selections for option in options):
            pages.discard(page_number)
    return sorted(pages)


def _box_for_range(text_page, start: int, end: int):
    boxes = []
    for index in range(start, end):
        box = text_page.get_charbox(index)
        if box and box[2] > box[0] and box[3] > box[1]:
            boxes.append(box)
    if not boxes:
        return None
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def _extract_lines(page, page_number: int) -> list[_TextLine]:
    text_page = page.get_textpage()
    text = text_page.get_text_range(0, text_page.count_chars())
    lines = []
    for match in re.finditer(r"[^\r\n]+", text):
        if not match.group().strip():
            continue
        box = _box_for_range(text_page, match.start(), match.end())
        if box:
            lines.append(
                _TextLine(page_number, match.group().strip(), match.start(), match.end(), box)
            )
    text_page.close()
    return sorted(lines, key=lambda line: (-line.box[3], line.box[0]))


def _rule_option(rule_text: str) -> str | None:
    lowered = rule_text.casefold()
    for option, fragment in _OPTION_RULE_TEXT.items():
        if fragment.casefold() in lowered:
            return option
    return None


def _section_redactions(
    lines: list[_TextLine],
    start_index: int,
    end_index: int | None,
    page_sizes: dict[int, tuple[float, float]],
    module: str,
) -> list[tuple[int, tuple[float, float, float, float]]]:
    start = lines[start_index]
    module_last = max(_ANNEX_PAGES[module])
    end = lines[end_index] if end_index is not None else None
    last_page = end.page_number if end else module_last
    last_page = min(last_page, module_last)
    redactions = []

    for page_number in range(start.page_number, last_page + 1):
        width, height = page_sizes[page_number]
        if page_number == start.page_number and end and end.page_number == start.page_number:
            bottom = end.box[3] + 3
            top = start.box[3] + 3
        elif page_number == start.page_number:
            bottom = 38
            top = start.box[3] + 3
        elif end and page_number == end.page_number:
            bottom = end.box[3] + 3
            top = height - 38
        else:
            bottom = 38
            top = height - 38
        if top > bottom:
            redactions.append((page_number, (14, bottom, width - 14, top)))
    return redactions


def _template_redactions(
    source: pdfium.PdfDocument,
    lines: list[_TextLine],
    selections: set[str],
) -> dict[int, list[tuple[float, float, float, float]]]:
    """Remove internal rules and all unselected subsection text from the master."""
    page_sizes = {
        page_number: tuple(source[page_number - 1].get_size())
        for page_number in range(1, len(source) + 1)
    }
    redactions: dict[int, list[tuple[float, float, float, float]]] = {}

    for page_number in range(1, len(source) + 1):
        page = source[page_number - 1]
        text_page = page.get_textpage()
        text = text_page.get_text_range(0, text_page.count_chars())
        width, _ = page_sizes[page_number]
        for match in _RULE_PATTERN.finditer(text):
            box = _box_for_range(text_page, match.start(), match.end())
            if box:
                redactions.setdefault(page_number, []).append(
                    (0, max(0, box[1] - 5), width, box[3] + 5)
                )

            option = _rule_option(match.group())
            if not option or option in selections:
                continue
            module = _OPTION_MODULE[option]
            heading = _OPTION_HEADINGS[option]
            start_index = next(
                (
                    index
                    for index, line in enumerate(lines)
                    if line.page_number in _ANNEX_PAGES[module]
                    and line.text.casefold().startswith(heading.casefold())
                ),
                None,
            )
            if start_index is None:
                raise ValueError(f"could not locate contract subsection: {heading}")
            end_index = next(
                (
                    index
                    for index in range(start_index + 1, len(lines))
                    if any(
                        lines[index].text.casefold().startswith(label.casefold())
                        for label in _ALL_SECTION_HEADINGS
                    )
                ),
                None,
            )
            for target_page, rect in _section_redactions(
                lines, start_index, end_index, page_sizes, module
            ):
                redactions.setdefault(target_page, []).append(rect)
        text_page.close()

    note_page_number = 27
    note_page = source[note_page_number - 1]
    note_text_page = note_page.get_textpage()
    note_text = note_text_page.get_text_range(0, note_text_page.count_chars())
    note_match = _TEMPLATE_NOTE_PATTERN.search(note_text)
    if note_match:
        box = _box_for_range(note_text_page, note_match.start(), note_match.end())
        if box:
            redactions.setdefault(note_page_number, []).append(
                (max(0, box[0] - 5), max(0, box[1] - 4), box[2] + 5, box[3] + 4)
            )
    note_text_page.close()
    return redactions


def _money(value, currency: str) -> str:
    return f"{value:,.2f} {currency}"


def _machine_groups(lines: tuple[OfferLine, ...]) -> list[tuple[str, list[OfferLine]]]:
    groups: dict[str, list[OfferLine]] = {}
    for line in lines:
        if line.equipment:
            groups.setdefault(line.equipment, []).append(line)
    return list(groups.items())


def _needs_equipment_continuation(groups: list[tuple[str, list[OfferLine]]]) -> bool:
    """Keep the fixed master table readable when equipment details do not fit."""
    if len(groups) > 2:
        return True
    return any(
        len(
            ", ".join(
                dict.fromkeys(line.description for line in machine_lines if line.description)
            )
        )
        > 65
        for _, machine_lines in groups
    )


def _selected_scope_text(selections: set[str], module: str) -> str:
    return ", ".join(
        _OPTION_LABELS[option]
        for option in GUARDIAN_OPTIONS_BY_MODULE[module]
        if option in selections
    )


def _token_values(doc: OfferDocument, executor: dict[str, str]) -> dict[str, str]:
    selections = set(doc.guardian_selections)
    groups = _machine_groups(doc.lines)
    needs_continuation = _needs_equipment_continuation(groups)
    machine_names = [name for name, _ in groups]
    line_total = sum((line.import_amount for line in doc.lines), start=doc.total * 0)
    customer_city = " ".join(
        value for value in (doc.account_city, doc.account_province) if value
    )
    site = doc.customer_site or ", ".join(
        value for value in (doc.account_city, doc.account_province, doc.account_country) if value
    )
    offer_date = doc.offer_date.strftime("%d %B %Y") if doc.offer_date else ""

    values = {
        "Agreement_Number": "",
        "Offer_Number": doc.number,
        "Offer_Date": offer_date,
        "Contract_Start_Date": "",
        "Contract_Duration": "",
        "Initial_Term": "",
        "Renewal_Term": "",
        "Termination_Notice_Period": "",
        "Billing_Frequency": "",
        "Weber_Legal_Entity": executor["name"],
        "Weber_Address": executor["street"],
        "Weber_Postcode_City": executor["city"],
        "Weber_Country": executor["country"],
        "Customer_Legal_Name": doc.account_name,
        "Customer_Number": doc.customer_number or "",
        "Customer_Site": site,
        "Customer_Address": "",
        "Customer_Postcode_City": customer_city,
        "Customer_Country": doc.account_country or "",
        "Currency": doc.currency,
        "Line_1": machine_names[0] if machine_names else "",
        "Line_2": machine_names[1] if len(machine_names) > 1 else "",
        "Machine_1": machine_names[0] if machine_names else "",
        "Machine_2": machine_names[1] if len(machine_names) > 1 else "",
        "Serial_1": "",
        "Serial_2": "",
        "Type_1": "",
        "Type_2": "",
        "Modules_1": "See Annex 1 continuation" if needs_continuation else ", ".join(
            dict.fromkeys(line.description or "" for line in groups[0][1] if line.description)
        ) if groups else "",
        "Modules_2": "See Annex 1 continuation" if needs_continuation else ", ".join(
            dict.fromkeys(line.description or "" for line in groups[1][1] if line.description)
        ) if len(groups) > 1 else "",
        "Frequency_1": doc.inspection_frequency or "",
        "Frequency_2": doc.inspection_frequency if len(groups) > 1 else "",
        "Number_Of_Machines": str(len(machine_names)),
        "Number_Of_Lines": str(len(machine_names)),
        "Inspection_Amount": _money(line_total, doc.currency),
        "Travel_Amount": _money(doc.expenses, doc.currency),
        "Parts_Kit_Amount": _money(doc.bk_price, doc.currency),
        "Service_Support_Amount": "",
        "Parts_Module_Amount": "",
        "Blade_Module_Amount": "",
        "Training_Module_Amount": "",
        "Digital_Module_Amount": "",
        "Guardian_Discount": _money(doc.discount, doc.currency),
        "Total_Contract_Value": _money(doc.total_end, doc.currency),
        "Payment_Terms": "",
        "Price_Adjustment_Rule": "",
        "Travel_Conditions": "",
        "Freight_Conditions": "",
        "Special_Commercial_Conditions": doc.general_comments or "",
        "Inspection_Frequency": doc.inspection_frequency or "",
        "Number_Of_Inspections": "",
        "Standard_Service_Hours": "",
        "Hotline_Service_Hours": "",
        "Hotline_Number": "",
        "Service_Email": "",
        "Priority_Response_Target": "",
        "Parts_Discount": "",
        "Parts_Delivery_Condition": "",
        "Freight_Free_Threshold": "",
        "Blade_Discount": "",
        "Operator_Training_Quantity": "",
        "Maintenance_Training_Quantity": "",
        "Line_Optimization_Quantity": "",
        "EPIP_Audit_Quantity": "",
        "EPIP_Lines": "",
        "Factory_Cockpit_Lines": ", ".join(machine_names),
        "Performance_Review_Frequency": "",
        "MRO_Review_Frequency": "",
        "MRO_Target": "",
        "Account_Review_Frequency": "",
    }
    scope_tokens = {
        "maintenance_inspection": "Selected_Maintenance_Options",
        "service_support": "Selected_Service_Support_Options",
        "parts_availability": "Selected_Parts_Options",
        "blade_solutions": "Selected_Blade_Options",
        "training_optimization": "Selected_Training_Options",
        "digital_services": "Selected_Digital_Options",
    }
    for module, token in scope_tokens.items():
        values[token] = _selected_scope_text(selections, module)
    return values


def _fit_font(text: str, font_name: str, start_size: float, max_width: float) -> float:
    size = start_size
    while size > 5.5 and stringWidth(text, font_name, size) > max_width:
        size -= 0.25
    return max(size, 5.5)


def _mask_rect(canvas: Canvas, box, pad: float = 2) -> None:
    x0, y0, x1, y1 = box
    canvas.setFillColor(white)
    canvas.rect(
        max(0, x0 - pad),
        max(0, y0 - pad),
        max(0, x1 - x0 + 2 * pad),
        max(0, y1 - y0 + 2 * pad),
        stroke=0,
        fill=1,
    )


def _draw_token_replacements(
    canvas: Canvas,
    text_page,
    text: str,
    values: dict[str, str],
    page_width: float,
) -> None:
    for match in _PLACEHOLDER_PATTERN.finditer(text):
        box = _box_for_range(text_page, match.start(), match.end())
        if not box:
            continue
        _mask_rect(canvas, box, 2)
        key = match.group()[2:-2]
        value = values.get(key, "")
        if not value:
            continue

        line_end = text.find("\n", match.end())
        if line_end < 0:
            line_end = len(text)
        next_x = None
        for index in range(match.end(), line_end):
            if text[index].isspace():
                continue
            next_box = text_page.get_charbox(index)
            if next_box and next_box[0] > box[2] + 1:
                next_x = next_box[0]
                break
        available_width = (
            next_x - box[2] - 3 if next_x else page_width - box[0] - 22
        )
        available_width = max(12, min(available_width, page_width - box[0] - 18))
        font_name = "Helvetica"
        font_size = _fit_font(value, font_name, max(7, (box[3] - box[1]) * 1.12), available_width)
        canvas.setFillColor(HexColor("#333333"))
        canvas.setFont(font_name, font_size)
        canvas.drawString(box[0], box[1] - 1, value)


def _draw_module_checkmarks(canvas: Canvas, text_page, text: str, selections: set[str]) -> None:
    pattern = re.compile(
        r"\[ \]\s*(Maintenance & Inspection|Service Support|Parts & Availability|"
        r"Blade Solutions|Training & Optimization|Digital Services)"
    )
    for match in pattern.finditer(text):
        module = _MODULE_LABELS[match.group(1)]
        box = _box_for_range(text_page, match.start(), match.start() + 3)
        if not box or module not in selections:
            continue
        _mask_rect(canvas, box, 1.5)
        canvas.setFillColor(HexColor("#111111"))
        canvas.setFont("Helvetica", max(7, (box[3] - box[1]) * 1.05))
        canvas.drawString(box[0], box[1] - 1, "[x]")


def _draw_source_page(
    canvas: Canvas,
    source: pdfium.PdfDocument,
    page_number: int,
    output_page_number: int,
    redactions: list[tuple[float, float, float, float]],
    values: dict[str, str],
    selections: set[str],
) -> None:
    page = source[page_number - 1]
    width, height = page.get_size()
    canvas.setPageSize((width, height))
    bitmap = page.render(scale=_RENDER_SCALE)
    image = bitmap.to_pil().convert("RGB")
    canvas.drawImage(ImageReader(image), 0, 0, width=width, height=height)
    bitmap.close()

    for rect in redactions:
        canvas.setFillColor(white)
        canvas.rect(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1], stroke=0, fill=1)

    text_page = page.get_textpage()
    text = text_page.get_text_range(0, text_page.count_chars())
    if page_number == 10:
        for match in re.finditer(r"\.{3}", text):
            box = _box_for_range(text_page, match.start(), match.end())
            if box:
                _mask_rect(canvas, box, 2)
    if page_number == 27:
        note = _TEMPLATE_NOTE_PATTERN.search(text)
        if note:
            box = _box_for_range(text_page, note.start(), note.end())
            if box:
                _mask_rect(canvas, box, 4)

    page_number_matches = list(_PAGE_NUMBER_PATTERN.finditer(text))
    if page_number_matches:
        box = _box_for_range(
            text_page, page_number_matches[-1].start(), page_number_matches[-1].end()
        )
        if box:
            _mask_rect(canvas, box, 3)

    _draw_token_replacements(canvas, text_page, text, values, width)
    if page_number == 10:
        _draw_module_checkmarks(canvas, text_page, text, selections)
    if page_number_matches and box:
        canvas.setFillColor(HexColor("#7C8188"))
        canvas.setFont("Helvetica", max(7, (box[3] - box[1]) * 1.2))
        canvas.drawRightString(width - 18, box[1] - 1, f"Page {output_page_number}")
    text_page.close()
    canvas.showPage()
    page.close()


def _wrapped_lines(text: str, font_name: str, font_size: float, max_width: float) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and stringWidth(candidate, font_name, font_size) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def _draw_cover(canvas: Canvas, doc: OfferDocument, executor: dict[str, str], provisional: bool) -> None:
    width, height = A4
    canvas.setPageSize(A4)
    canvas.setFillColor(white)
    canvas.rect(0, 0, width, height, stroke=0, fill=1)

    canvas.drawImage(
        ImageReader(str(_WEBER_LOGO)),
        width - 115,
        height - 34,
        width=82,
        height=24,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    canvas.drawImage(
        ImageReader(str(_GUARDIAN_LOGO)),
        (width - 150) / 2,
        480,
        width=150,
        height=147,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    blue = HexColor("#315FA1")
    canvas.setFillColor(blue)
    canvas.setFont("Helvetica-Bold", 15)
    canvas.drawCentredString(width / 2, 440, "MAINTENANCE CONTRACT")
    if provisional:
        canvas.setFont("Helvetica-Bold", 9)
        canvas.setFillColor(HexColor("#B00020"))
        canvas.drawCentredString(width / 2, 421, "DRAFT - SUBSIDIARY LEGAL DETAILS REQUIRED")

    left = 124
    max_width = width - left - 48
    canvas.setFillColor(HexColor("#111111"))
    canvas.setFont("Helvetica", 6.5)
    y = 307
    canvas.drawString(left - 28, y, "Between the company:")
    y -= 13
    canvas.setFillColor(blue)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(left, y, executor["name"])
    y -= 11
    canvas.setFillColor(HexColor("#111111"))
    canvas.setFont("Helvetica", 7)
    for line in (executor["street"], executor["city"], executor["country"]):
        if line:
            canvas.drawString(left, y, line)
            y -= 10
    y -= 5
    canvas.drawRightString(width - 55, y, 'hereinafter referred to as "Weber"')

    y = 205
    canvas.setFont("Helvetica", 6.5)
    canvas.drawString(left - 28, y, "And the company:")
    y -= 13
    canvas.setFillColor(blue)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(left, y, doc.account_name.upper())
    y -= 11
    customer_address = doc.customer_site or ", ".join(
        value
        for value in (doc.account_city, doc.account_province, doc.account_country)
        if value
    )
    canvas.setFillColor(HexColor("#111111"))
    canvas.setFont("Helvetica", 7)
    for line in _wrapped_lines(customer_address, "Helvetica", 7, max_width):
        canvas.drawString(left, y, line)
        y -= 9
    y -= 4
    canvas.drawRightString(width - 55, y, 'hereinafter referred to as the "Customer"')

    canvas.setFont("Helvetica", 6.5)
    y = 75
    preamble = (
        "the following maintenance and inspection contract is entered into "
        '(hereinafter, the "Agreement"):'
    )
    for line in _wrapped_lines(preamble, "Helvetica", 6.5, width - 90):
        canvas.drawString(45, y, line)
        y -= 9
    canvas.showPage()


def _draw_equipment_continuation_pages(
    canvas: Canvas,
    groups: list[tuple[str, list[OfferLine]]],
    frequency: str | None,
    first_page_number: int,
) -> int:
    """Add matching Annex 1 table pages for machines beyond the two master rows."""
    pending = list(groups)
    page_number = first_page_number
    columns = (
        ("Production Line", 76),
        ("Machine", 78),
        ("Serial No.", 72),
        ("Type", 62),
        ("Included Modules / Components", 158),
        ("Service Frequency", 74),
    )
    page_width, page_height = A4
    table_x = 38
    header_height = 38
    font_size = 7.2
    leading = 8.4

    while pending:
        canvas.setPageSize(A4)
        canvas.setFillColor(HexColor("#245A93"))
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawRightString(page_width - 22, page_height - 28, "WEBER GUARDIAN AGREEMENT")
        canvas.setFont("Helvetica-Bold", 15)
        canvas.drawString(45, page_height - 82, "ANNEX 1 - EQUIPMENT & COMMERCIAL SCHEDULE")
        canvas.setFont("Helvetica", 10)
        canvas.drawString(45, page_height - 101, "Equipment Covered (continued)")

        table_top = page_height - 126
        x = table_x
        canvas.setStrokeColor(HexColor("#111111"))
        canvas.setLineWidth(0.5)
        for label, column_width in columns:
            canvas.setFillColor(HexColor("#064477"))
            canvas.rect(x, table_top - header_height, column_width, header_height, fill=1, stroke=1)
            canvas.setFillColor(white)
            canvas.setFont("Helvetica-Bold", 7.5)
            for line_no, text_line in enumerate(
                _wrapped_lines(label, "Helvetica-Bold", 7.5, column_width - 8)
            ):
                canvas.drawCentredString(
                    x + column_width / 2,
                    table_top - 13 - line_no * 9,
                    text_line,
                )
            x += column_width

        y = table_top - header_height
        while pending:
            equipment, machine_lines = pending[0]
            modules = ", ".join(
                dict.fromkeys(
                    line.description for line in machine_lines if line.description
                )
            )
            row_values = (
                equipment,
                equipment,
                "",
                "",
                modules,
                frequency or "",
            )
            wrapped = [
                _wrapped_lines(value, "Helvetica", font_size, width - 8) if value else [""]
                for value, (_, width) in zip(row_values, columns, strict=True)
            ]
            row_height = max(22, max(len(cell) for cell in wrapped) * leading + 8)
            if y - row_height < 58:
                break

            x = table_x
            for cell_lines, (_, column_width) in zip(wrapped, columns, strict=True):
                canvas.setFillColor(white)
                canvas.rect(x, y - row_height, column_width, row_height, fill=1, stroke=1)
                canvas.setFillColor(HexColor("#222222"))
                canvas.setFont("Helvetica", font_size)
                for line_no, text_line in enumerate(cell_lines):
                    canvas.drawString(
                        x + 4,
                        y - 8 - font_size - line_no * leading,
                        text_line,
                    )
                x += column_width
            y -= row_height
            pending.pop(0)

        canvas.setFillColor(HexColor("#7C8188"))
        canvas.setFont("Helvetica", 8)
        canvas.drawString(14, 17, "Weber Guardian | Modular Master Agreement & Service Annexes")
        canvas.drawRightString(page_width - 18, 17, f"Page {page_number}")
        canvas.showPage()
        page_number += 1

    return page_number


def build_offer_pdf(doc: OfferDocument) -> bytes:
    """Render the modular customer agreement using the supplied PDF master."""
    _language(doc)
    executor, provisional = _executor(doc)
    if not _TEMPLATE.is_file():
        raise ValueError(f"Guardian PDF master template is missing: {_TEMPLATE.name}")
    if not _GUARDIAN_LOGO.is_file() or not _WEBER_LOGO.is_file():
        raise ValueError("Guardian and Weber logo PNG files must be present in the Weber assets folder")

    source = pdfium.PdfDocument(str(_TEMPLATE))
    if len(source) != 27:
        source.close()
        raise ValueError("Guardian PDF master template must contain exactly 27 pages")

    lines: list[_TextLine] = []
    for page_number in range(1, len(source) + 1):
        lines.extend(_extract_lines(source[page_number - 1], page_number))

    selections = set(doc.guardian_selections)
    redactions = _template_redactions(source, lines, selections)
    values = _token_values(doc, executor)
    machine_groups = _machine_groups(doc.lines)
    output = io.BytesIO()
    canvas = Canvas(output, pagesize=A4, pageCompression=1)
    _draw_cover(canvas, doc, executor, provisional)

    output_page_number = 2
    for page_number in _selected_pages(selections):
        _draw_source_page(
            canvas,
            source,
            page_number,
            output_page_number,
            redactions.get(page_number, []),
            values,
            selections,
        )
        output_page_number += 1
        if page_number == 10 and _needs_equipment_continuation(machine_groups):
            output_page_number = _draw_equipment_continuation_pages(
                canvas,
                machine_groups,
                doc.inspection_frequency,
                output_page_number,
            )
    canvas.save()
    source.close()
    return output.getvalue()
