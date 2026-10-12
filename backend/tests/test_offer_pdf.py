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


def test_renderer_returns_real_pdf():
    pdf = build_offer_pdf(_doc())
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 5000


def test_renderer_rejects_unknown_language_and_subsidiary():
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
    base_pdf = build_offer_pdf(_doc())
    base = pdfium.PdfDocument(base_pdf)
    assert len(base) == 12
    base.close()

    selected_pdf = build_offer_pdf(
        _doc(guardian_selections=("service_support", "remote_support"))
    )
    selected = pdfium.PdfDocument(selected_pdf)
    assert len(selected) == 13
    selected.close()


def test_renderer_adds_an_equipment_continuation_for_more_than_two_machines():
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
    assert len(rendered) == 13
    continuation = rendered[9].get_textpage()
    text = continuation.get_text_range(0, continuation.count_chars())
    assert "M3" in text
    rendered.close()


def test_guardian_options_require_a_known_selected_parent_module():
    pricing = OfferCalculateIn(work_hours=Decimal("0"))
    with pytest.raises(ValueError, match="require module selection"):
        OfferCreate(
            customer_id="C-1",
            guardian_selections=["remote_support"],
            pricing=pricing,
        )

    with pytest.raises(ValueError, match="unknown Guardian selections"):
        OfferCreate(
            customer_id="C-1",
            guardian_selections=["made_up_service"],
            pricing=pricing,
        )


def test_renderer_falls_back_to_provisional_block_without_invented_data():
    from app.weber.pdf import _executor

    block, provisional = _executor(_doc(subsidiary_id="Weber Partners"))
    assert provisional is True
    # Placeholder carries only the canonical name: no street, city, country
    # or signature place that would look like real legal data.
    assert block["name"] == "Weber Partners"
    assert not block["street"] and not block["city"] and not block["country"] and not block["place_date"]
    # Rendering still works (falls back, never raises).
    assert build_offer_pdf(_doc(subsidiary_id="Weber Partners"))[:5] == b"%PDF-"
    # Subsidiaries with a real legal block are never provisional.
    for subsidiary_id in ("Weber Iberica", "Weber Benelux", "Weber Germany", "Weber Argentina"):
        _, provisional = _executor(_doc(subsidiary_id=subsidiary_id))
        assert provisional is False

    italy, provisional = _executor(_doc(subsidiary_id="Weber Italy"))
    assert provisional is False
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
    pricing = OfferCalculateIn(work_hours=Decimal("8"), tech_rate=Decimal("60"))
    es_id = create_offer(
        seed,
        OfferCreate(
            customer_id="C-ES",
            pricing=pricing,
            items=[],
            guardian_selections=["service_support", "remote_support"],
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
    assert offer.json()["guardian_selections"] == ["service_support", "remote_support"]

    res = test_client.get(f"/api/v1/offers/{ids['es']}/pdf", headers={"X-Dev-User": "oid-es"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:5] == b"%PDF-"
    rendered = pdfium.PdfDocument(res.content)
    assert len(rendered) == 13
    visible_text = " ".join(
        rendered[index].get_textpage().get_text_range(
            0, rendered[index].get_textpage().count_chars()
        )
        for index in range(len(rendered))
    )
    assert "[x]" in visible_text
    assert "Remote Support" in visible_text
    assert "INTERNAL GENERATION RULE" not in visible_text
    assert "DOCUMENT STRUCTURE" not in visible_text
    rendered.close()
    # Out-of-scope reads as missing; anonymous as unauthenticated.
    assert test_client.get(f"/api/v1/offers/{ids['de']}/pdf", headers={"X-Dev-User": "oid-es"}).status_code == 404
    assert test_client.get(f"/api/v1/offers/{ids['es']}/pdf").status_code == 401
