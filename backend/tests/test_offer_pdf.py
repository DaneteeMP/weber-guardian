"""Offer PDF tests: renderer output and the HTTP endpoint with scope."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
import pypdfium2 as pdfium
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core import security
from app.core.db import Base, get_db
from app.main import app as api_app
import app.modules.customers.models  # noqa: F401
import app.modules.equipment.models  # noqa: F401
import app.modules.offers.models  # noqa: F401
import app.modules.users.models  # noqa: F401
from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import create_customer
from app.modules.offers.document import OfferDocument, OfferLine
from app.modules.offers.schemas import OfferCalculateIn, OfferCreate
from app.modules.offers.service import create_offer
from app.modules.users.models import User
from app.weber.pdf import build_offer_pdf
from app.weber.pdf.values import (
    document_locale,
    executor_block,
    executor_is_provisional,
    token_values,
)


def _doc(**overrides):
    params = {
        "offer_id": uuid4(),
        "number": "W-02-2026-0001",
        "offer_date": date(2026, 9, 21),
        "status": "Pending response",
        "language": "Spanish",
        "inspection_frequency": "Annual",
        "responsible_person": None,
        "subsidiary_id": "Weber Iberica",
        "account_name": "UAB Riela servisas",
        "account_city": None,
        "account_province": None,
        "account_country": "Lithuania",
        "currency": "EUR",
        "trip_cost": Decimal("50"),
        "diets": Decimal("40"),
        "hotel_cost": Decimal("0"),
        "trip_hours": Decimal("6"),
        "work_hours": Decimal("11"),
        "bk_hours": Decimal("0"),
        "report_hours": Decimal("2"),
        "total_hours": Decimal("16"),
        "hours_import": Decimal("960"),
        "expenses": Decimal("90"),
        "discount": Decimal("144"),
        "bk_price": Decimal("0"),
        "total": Decimal("1050"),
        "total_end": Decimal("906"),
        "general_comments": None,
        "lines": (OfferLine(pos=1, equipment="304-565", description="Slicer", import_amount=Decimal("100")),),
    }
    params.update(overrides)
    return OfferDocument(**params)


def _full_text(rendered) -> str:
    """All visible text of an open PDF document; the caller closes it."""
    return " ".join(
        rendered[index].get_textpage().get_text_range(
            0, rendered[index].get_textpage().count_chars()
        )
        for index in range(len(rendered))
    )


def _sample_docx_bytes() -> bytes:
    """A small Word file exercising paragraphs, bold runs and tables."""
    import io

    from docx import Document as DocxDocument

    document = DocxDocument()
    document.add_paragraph("Confidential service terms")
    paragraph = document.add_paragraph()
    paragraph.add_run("Response time: ")
    paragraph.add_run("4 hours").bold = True
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Module"
    table.cell(0, 1).text = "Hours"
    table.cell(1, 0).text = "Inspection"
    table.cell(1, 1).text = "8"
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_renderer_returns_real_pdf():
    pdf = build_offer_pdf(_doc())
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 5000


def test_commercial_summary_hides_the_internal_costs_and_adds_up():
    """The client sees the modules, the discount and the final amount.

    The travel, the diets and the hotels are already spread over the module
    prices (legacy "RepartirCostes"), so the travel line is zero and the
    summary adds up: inspection + kit - discount = total contract value.
    """
    doc = _doc(
        trip_cost=Decimal("50"),
        expenses=Decimal("90"),
        discount=Decimal("252"),
        bk_price=Decimal("0"),
        total=Decimal("1318"),
        total_end=Decimal("1066"),
    )
    values = token_values(doc, document_locale(doc))

    def plain(text: str) -> str:
        return text.replace("\u00a0", " ")

    assert plain(values["Travel_Amount"]) == "0,00 €"
    assert plain(values["Inspection_Amount"]) == "100,00 €"
    assert plain(values["Guardian_Discount"]) == "252,00 €"
    assert plain(values["Total_Contract_Value"]) == "1.066,00 €"


def test_renderer_rejects_unknown_language():
    with pytest.raises(ValueError, match="language"):
        build_offer_pdf(_doc(language="Klingon"))


def test_renderer_supports_all_executor_subsidiaries():
    for subsidiary_id in (
        "Weber Iberica",
        "Weber Benelux",
        "Weber Germany",
        "Weber Argentina",
        "Weber Italy",
        "España",
        "Deutschland",
    ):
        pdf = build_offer_pdf(_doc(subsidiary_id=subsidiary_id))
        assert pdf[:5] == b"%PDF-"


def test_renderer_uses_only_selected_annex_pages():
    # English fixture so the annex titles are the untranslated source text.
    base = pdfium.PdfDocument(build_offer_pdf(_doc(language="English")))
    try:
        selected = pdfium.PdfDocument(
            build_offer_pdf(
                _doc(language="English", guardian_selections=("customer_service", "remote_support"))
            )
        )
        try:
            assert len(selected) > len(base)
            assert "ANNEX 3" not in _full_text(base)
            assert "ANNEX 3 - SERVICE SUPPORT" in _full_text(selected)
        finally:
            selected.close()
    finally:
        base.close()


def test_renderer_renders_every_machine_of_the_offer():
    lines = tuple(
        OfferLine(
            pos=position,
            equipment=f"M{position}",
            description=f"Module for M{position}",
            import_amount=Decimal("10.00"),
        )
        for position in range(1, 4)
    )
    rendered = pdfium.PdfDocument(build_offer_pdf(_doc(lines=lines)))
    try:
        text = _full_text(rendered)
        for position in (1, 2, 3):
            assert f"M{position}" in text
    finally:
        rendered.close()


def test_guardian_options_carry_their_module_and_unknown_keys_are_rejected():
    pricing = OfferCalculateIn(work_hours=Decimal("0"), equipment_count=0)
    # A service never needs its module typed by hand: it is derived.
    offer = OfferCreate(
        customer_id="C-1",
        guardian_selections=["remote_support"],
        pricing=pricing,
    )
    assert offer.guardian_selections == ["remote_support", "customer_service"]

    with pytest.raises(ValueError, match="unknown Guardian selections"):
        OfferCreate(
            customer_id="C-1",
            guardian_selections=["made_up_service"],
            pricing=pricing,
        )


def test_renderer_falls_back_to_provisional_block_without_invented_data():
    provisional_doc = _doc(subsidiary_id="Weber Partners")
    block = executor_block(provisional_doc)
    assert executor_is_provisional(provisional_doc) is True
    # Placeholder carries only the canonical name: no street, city, country
    # or signature place that would look like real legal data.
    assert block["name"] == "Weber Partners"
    assert not block["street"] and not block["city"] and not block["country"] and not block["place_date"]
    # The cover is flagged instead of showing another filial's address.
    rendered = pdfium.PdfDocument(build_offer_pdf(provisional_doc))
    try:
        assert "DRAFT - SUBSIDIARY LEGAL DETAILS REQUIRED" in _full_text(rendered)
    finally:
        rendered.close()
    # Subsidiaries with a real legal block are never provisional.
    for subsidiary_id in ("Weber Iberica", "Weber Benelux", "Weber Germany", "Weber Argentina"):
        assert executor_is_provisional(_doc(subsidiary_id=subsidiary_id)) is False

    assert executor_is_provisional(_doc(subsidiary_id="Weber Italy")) is False
    italy = executor_block(_doc(subsidiary_id="Weber Italy"))
    assert italy["name"] == "WEBER FOOD TECHNOLOGY ITALIA SrL"
    assert italy["street"] == "Via Josef Maria Pernter, 14"
    assert italy["city"] == "39044 Egna BZ"
    assert italy["country"] == "Italia"


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(security.settings, "dev_auth_enabled", True)
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_db():
        session = Session()
        try:
            yield session
        finally:
            session.close()

    api_app.dependency_overrides[get_db] = override_db
    seed = Session()
    seed.add(User(external_id="oid-es", role="sales", subsidiary_id="Weber Iberica"))
    seed.add(User(external_id="oid-de", role="sales", subsidiary_id="Weber Germany"))
    seed.commit()
    create_customer(seed, CustomerCreate(customer_id="C-ES", account_name="ES Client", subsidiary_id="Weber Iberica"))
    create_customer(seed, CustomerCreate(customer_id="C-DE", account_name="DE Client", subsidiary_id="Weber Germany"))
    pricing = OfferCalculateIn(work_hours=Decimal("8"), tech_rate=Decimal("60"), equipment_count=0)
    es_id = create_offer(
        seed,
        OfferCreate(
            customer_id="C-ES",
            pricing=pricing,
            items=[],
            guardian_selections=["customer_service", "remote_support"],
        ),
        created_by=None,
    ).id
    de_id = create_offer(
        seed,
        OfferCreate(customer_id="C-DE", pricing=pricing, items=[]),
        created_by=None,
    ).id
    seed.close()
    with TestClient(api_app) as test_client:
        yield test_client, {"es": str(es_id), "de": str(de_id)}
    api_app.dependency_overrides.clear()


def test_pdf_endpoint_serves_bytes_with_scope(client):
    test_client, ids = client
    offer = test_client.get(f"/api/v1/offers/{ids['es']}", headers={"X-Dev-User": "oid-es"})
    assert offer.status_code == 200
    assert offer.json()["guardian_selections"] == ["customer_service", "remote_support"]

    res = test_client.get(f"/api/v1/offers/{ids['es']}/pdf", headers={"X-Dev-User": "oid-es"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:5] == b"%PDF-"
    rendered = pdfium.PdfDocument(res.content)
    visible_text = _full_text(rendered)
    rendered.close()
    assert "[x]" in visible_text
    assert "Remote Support" in visible_text
    assert "INTERNAL GENERATION RULE" not in visible_text
    assert "DOCUMENT STRUCTURE" not in visible_text
    # Out-of-scope reads as missing; anonymous as unauthenticated.
    assert test_client.get(f"/api/v1/offers/{ids['de']}/pdf", headers={"X-Dev-User": "oid-es"}).status_code == 404
    assert test_client.get(f"/api/v1/offers/{ids['es']}/pdf").status_code == 401


def test_document_settings_endpoint_saves_and_renders_the_print_modal_state(client):
    """The print modal auto-save: partial PATCH, then the PDF reads it back."""
    test_client, ids = client
    headers = {"X-Dev-User": "oid-es"}

    saved = test_client.patch(
        f"/api/v1/offers/{ids['es']}/document",
        json={
            "language": "es",
            "guardian_selections": ["customer_service", "hotline"],
            "custom_annexes": [
                {"title": "ANNEX X - CUSTOM TERMS", "body": "Extra clause line."}
            ],
        },
        headers=headers,
    )
    assert saved.status_code == 200
    body = saved.json()
    assert body["language"] == "es"
    assert body["guardian_selections"] == ["customer_service", "hotline"]
    assert body["custom_annexes"] == [
        {"title": "ANNEX X - CUSTOM TERMS", "body": "Extra clause line.", "body_html": None}
    ]

    # The PDF is rendered from those saved settings: Spanish locale, the
    # module selected in the modal and the custom annex before the signatures.
    pdf = test_client.get(f"/api/v1/offers/{ids['es']}/pdf", headers=headers)
    assert pdf.status_code == 200
    rendered = pdfium.PdfDocument(pdf.content)
    text = _full_text(rendered)
    rendered.close()
    assert "ANEXO 1" in text
    assert "ANNEX X - CUSTOM TERMS" in text
    assert "Extra clause line." in text
    assert text.index("ANNEX X - CUSTOM TERMS") < text.index("FIRMAS")

    # A service carries its own module: the patch is accepted and stored
    # with the derived parent.
    service_only = test_client.patch(
        f"/api/v1/offers/{ids['es']}/document",
        json={"guardian_selections": ["remote_support"]},
        headers=headers,
    )
    assert service_only.status_code == 200
    assert service_only.json()["guardian_selections"] == [
        "remote_support",
        "customer_service",
    ]

    # A headingless annex is a defect: blank titles never persist.
    blank_title = test_client.patch(
        f"/api/v1/offers/{ids['es']}/document",
        json={"custom_annexes": [{"title": "   ", "body": "orphan"}]},
        headers=headers,
    )
    assert blank_title.status_code == 422

    # Out-of-scope writes read as missing.
    cross_scope = test_client.patch(
        f"/api/v1/offers/{ids['de']}/document",
        json={"language": "es"},
        headers=headers,
    )
    assert cross_scope.status_code == 404


def test_upload_annex_endpoint_parses_docx_into_the_pdf(client):
    """The modal's Word attachment: parsed on upload, printed before the summary."""
    test_client, ids = client
    headers = {"X-Dev-User": "oid-es"}

    res = test_client.post(
        f"/api/v1/offers/{ids['es']}/document/annexes",
        files={
            "file": (
                "Custom Terms.docx",
                _sample_docx_bytes(),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        headers=headers,
    )
    assert res.status_code == 200
    annexes = res.json()["custom_annexes"]
    assert len(annexes) == 1
    assert annexes[0]["title"] == "Custom Terms"
    assert "Confidential service terms" in annexes[0]["body_html"]
    assert "<strong>4 hours</strong>" in annexes[0]["body_html"]
    assert "<table>" in annexes[0]["body_html"]

    pdf = test_client.get(f"/api/v1/offers/{ids['es']}/pdf", headers=headers)
    assert pdf.status_code == 200
    rendered = pdfium.PdfDocument(pdf.content)
    text = _full_text(rendered)
    rendered.close()
    assert "Confidential service terms" in text
    assert "4 hours" in text
    assert "Inspection" in text
    assert text.index("Custom Terms") < text.index("FIRMAS")


def test_upload_annex_endpoint_rejects_bad_files_and_scope(client):
    test_client, ids = client
    headers = {"X-Dev-User": "oid-es"}
    docx_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    wrong_extension = test_client.post(
        f"/api/v1/offers/{ids['es']}/document/annexes",
        files={"file": ("annex.txt", b"plain text", "text/plain")},
        headers=headers,
    )
    assert wrong_extension.status_code == 422

    not_a_zip = test_client.post(
        f"/api/v1/offers/{ids['es']}/document/annexes",
        files={"file": ("annex.docx", b"not a zip archive", docx_type)},
        headers=headers,
    )
    assert not_a_zip.status_code == 422

    cross_scope = test_client.post(
        f"/api/v1/offers/{ids['de']}/document/annexes",
        files={"file": ("annex.docx", _sample_docx_bytes(), docx_type)},
        headers=headers,
    )
    assert cross_scope.status_code == 404

    anonymous = test_client.post(
        f"/api/v1/offers/{ids['es']}/document/annexes",
        files={"file": ("annex.docx", _sample_docx_bytes(), docx_type)},
    )
    assert anonymous.status_code == 401


def test_renderer_prints_uploaded_annex_html_before_the_signatures():
    from app.modules.offers.document import CustomAnnex

    doc = _doc(
        custom_annexes=(
            CustomAnnex(
                title="ANNEX Y - WORD",
                body="",
                body_html=(
                    "<p>Word <strong>annex</strong> text</p>"
                    "<table><tbody><tr><th>Module</th></tr><tr><td>Inspection</td></tr></tbody></table>"
                ),
            ),
        )
    )
    rendered = pdfium.PdfDocument(build_offer_pdf(doc))
    try:
        text = _full_text(rendered)
        assert "Word annex text" in text
        assert "Inspection" in text
        assert text.index("ANNEX Y - WORD") < text.index("FIRMAS")
    finally:
        rendered.close()
