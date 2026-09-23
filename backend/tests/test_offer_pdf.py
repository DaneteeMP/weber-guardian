"""Offer PDF tests: renderer output and the HTTP endpoint with scope."""
from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
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
        "status": "Draft",
        "language": "Spanish",
        "inspection_frequency": "Annual",
        "responsible_person": None,
        "subsidiary_id": "ES",
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
    with pytest.raises(ValueError, match="subsidiary"):
        build_offer_pdf(_doc(subsidiary_id="NOWHERE"))


def test_renderer_supports_all_executor_subsidiaries():
    for subsidiary_id in ("ES", "BNL", "DE", "AR", "España", "Deutschland"):
        pdf = build_offer_pdf(_doc(subsidiary_id=subsidiary_id))
        assert pdf[:5] == b"%PDF-"


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
    seed.add(User(external_id="oid-es", role="sales", subsidiary_id="ES"))
    seed.add(User(external_id="oid-de", role="sales", subsidiary_id="DE"))
    seed.commit()
    create_customer(seed, CustomerCreate(customer_id="C-ES", account_name="ES Client", subsidiary_id="ES"))
    create_customer(seed, CustomerCreate(customer_id="C-DE", account_name="DE Client", subsidiary_id="DE"))
    pricing = OfferCalculateIn(work_hours=Decimal("8"), tech_rate=Decimal("60"))
    es_id = create_offer(
        seed,
        OfferCreate(customer_id="C-ES", pricing=pricing, items=[]),
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
    res = test_client.get(f"/api/v1/offers/{ids['es']}/pdf", headers={"X-Dev-User": "oid-es"})
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content[:5] == b"%PDF-"
    # Out-of-scope reads as missing; anonymous as unauthenticated.
    assert test_client.get(f"/api/v1/offers/{ids['de']}/pdf", headers={"X-Dev-User": "oid-es"}).status_code == 404
    assert test_client.get(f"/api/v1/offers/{ids['es']}/pdf").status_code == 401
