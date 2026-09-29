"""Guardian offer PDF renderer (Weber adapter).

Consumes OfferDocument (core data) and returns PDF bytes. Pure rendering:
all numbers arrive computed, all text arrives from contract_es. Only
Spanish ("Spanish"/"es") is supported so far; anything else fails
explicitly instead of printing the wrong legal text.
"""
import io
from datetime import date

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.subsidiaries import EXECUTOR_CODES, normalize_subsidiary
from app.modules.offers.document import OfferDocument
from app.weber import contract_es

_MONTHS = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _language(doc: OfferDocument) -> str:
    normalized = (doc.language or "").strip().lower()
    if normalized in ("spanish", "es", "es-es"):
        return "es"
    raise ValueError(f"unsupported PDF language: {doc.language!r}")


# Single-filial default while there is no subsidiary admin table (F4/F5):
# legacy rows without subsidiary print under the headquarters executor.
# Revisit the day a second filial prints its own address.
DEFAULT_SUBSIDIARY = "ES"

# Free-text variants resolve through the shared alias table
# (app.core.subsidiaries, single source of truth). Subsidiaries without a
# legal block print a clearly-marked provisional block instead of another
# filial's address: the user adds real legal data in contract_es later.
def _executor(doc: OfferDocument) -> tuple[dict[str, str], bool]:
    canonical = normalize_subsidiary(doc.subsidiary_id) or DEFAULT_SUBSIDIARY
    code = EXECUTOR_CODES.get(canonical, canonical)
    block = contract_es.EXECUTORS.get(code)
    if block is None:
        return _PROVISIONAL_BLOCK(canonical), True
    return block, False


def _PROVISIONAL_BLOCK(canonical: str) -> dict[str, str]:
    """Placeholder block. Deliberately no address, tax id or place of
    signature: none of that exists for this subsidiary yet, so the document
    must not pretend to. It prints a visible DRAFT marker instead."""
    return {
        "name": canonical,
        "street": "",
        "city": "",
        "country": "",
        "place_date": "",
    }


def _money(value, currency: str) -> str:
    return f"{value:,.2f} {currency}"


def _long_date(day: date) -> str:
    return f"{day.day} de {_MONTHS[day.month - 1]} de {day.year}"


def _header(canvas, _doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillGray(0.4)
    canvas.drawCentredString(105 * mm, 287 * mm, "WEBER FOOD TECHNOLOGY IBÉRICA, S.L.")
    canvas.drawCentredString(105 * mm, 283 * mm, "c/ La Coma, 29")
    canvas.drawCentredString(105 * mm, 279 * mm, "(08272) Sant Fruitós de Bages (Barcelona)")
    canvas.setStrokeGray(0.8)
    canvas.line(10 * mm, 275 * mm, 200 * mm, 275 * mm)
    canvas.restoreState()


def build_offer_pdf(doc: OfferDocument) -> bytes:
    """Render the official maintenance-contract PDF. Raises ValueError on gaps."""
    _language(doc)
    executor, provisional = _executor(doc)

    buf = io.BytesIO()
    pdf = SimpleDocTemplate(buf, pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle("Title2", parent=styles["Title"], textColor="#1E3C78", fontSize=22)
    draft = ParagraphStyle("Draft", parent=styles["Title"], textColor="#B00020", fontSize=16)
    h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=12, spaceBefore=8)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=10, spaceBefore=6)
    body = ParagraphStyle("Body2", parent=styles["Normal"], fontSize=9, leading=13)
    small = ParagraphStyle("Small", parent=styles["Normal"], fontSize=9, leading=13)
    bold = ParagraphStyle("Bold", parent=styles["Normal"], fontSize=9, leading=13, fontName="Helvetica-Bold")

    story = []
    today = date.today()

    # Cover: title, executor, client, preamble.
    story.append(Spacer(1, 50 * mm))
    story.append(Paragraph(contract_es.TITLE, title))
    if provisional:
        story.append(Spacer(1, 8 * mm))
        story.append(Paragraph(contract_es.DRAFT_BANNER, draft))
    story.append(Spacer(1, 15 * mm))
    story.append(Paragraph(contract_es.EXECUTOR_LABEL, body))
    story.append(Paragraph(f"<b>{executor['name']}</b>", body))
    if executor["street"]:
        story.append(Paragraph(executor["street"], body))
    if executor["city"]:
        story.append(Paragraph(executor["city"], body))
    if executor["country"]:
        story.append(Paragraph(executor["country"], body))
    story.append(Paragraph(contract_es.EXECUTOR_ALIAS, body))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(contract_es.CLIENT_LABEL, body))
    story.append(Paragraph(f"<b>{doc.account_name.upper()}</b>", body))
    city_line = " ".join(p for p in (doc.account_city, doc.account_province, doc.account_country) if p)
    if city_line:
        story.append(Paragraph(city_line.upper(), body))
    story.append(Paragraph(contract_es.CLIENT_ALIAS, body))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(contract_es.PREAMBLE, body))

    # Clauses.
    story.append(PageBreak())
    for kind, text, indent in contract_es.CLAUSES:
        if kind == "heading":
            story.append(Paragraph(text, h1))
        elif kind == "subheading":
            story.append(Paragraph(text, h2))
        else:
            story.append(Paragraph(text, ParagraphStyle("I", parent=body, leftIndent=indent)))

    # Signature + date.
    story.append(Spacer(1, 6 * mm))
    if executor["place_date"]:
        story.append(Paragraph(f"{executor['place_date']}, a {_long_date(today)}", body))
    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(f"<b>{doc.account_name.upper()}</b>", body))
    story.append(Paragraph(f"<b>{executor['name']}</b>", body))
    if provisional:
        story.append(Paragraph(contract_es.DRAFT_FOOTER, body))

    # Annex 1: machines and totals from the official document.
    story.append(PageBreak())
    story.append(Paragraph(contract_es.ANNEX_TITLE, h1))
    story.append(Paragraph(f"<b>{doc.account_name.upper()}</b>", body))
    if city_line:
        story.append(Paragraph(city_line.upper(), small))
    story.append(Paragraph(f"Oferta: <b>{doc.number}</b>", body))
    story.append(Paragraph(f"Fecha: {doc.offer_date.isoformat() if doc.offer_date else today.isoformat()}", body))
    story.append(Paragraph(f"Frecuencia: {doc.inspection_frequency or 'Annual'}", body))
    story.append(Spacer(1, 4 * mm))

    rows = [["Nº", "Equipo", "Módulo", "Importe"]]
    for line in doc.lines:
        rows.append([
            str(line.pos),
            line.equipment or "",
            line.description or "",
            _money(line.import_amount, doc.currency),
        ])
    table = Table(rows, colWidths=[12 * mm, 30 * mm, 80 * mm, 35 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), "#C8DCF0"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (3, 0), (3, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(table)
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph(f"Horas: {doc.total_hours} · Viaje: {_money(doc.trip_cost, doc.currency)}", body))
    story.append(Paragraph(f"Dietas: {_money(doc.diets, doc.currency)} · Hoteles: {_money(doc.hotel_cost, doc.currency)}", body))
    story.append(Paragraph(f"Total: <b>{_money(doc.total, doc.currency)}</b>", bold))
    story.append(Paragraph(f"Descuento: {_money(doc.discount, doc.currency)}", body))
    story.append(Paragraph(f"Importe total (sin IVA): <b>{_money(doc.total_end, doc.currency)}</b>", bold))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("NOTAS:", bold))
    for note in contract_es.NOTES + contract_es.DISCOUNT_NOTES:
        story.append(Paragraph(note, small))
    if doc.general_comments:
        story.append(Paragraph(f"Observaciones: {doc.general_comments}", body))

    pdf.build(story, onFirstPage=_header, onLaterPages=_header)
    return buf.getvalue()
