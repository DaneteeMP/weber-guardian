"""Offer service tests (F1). SQLite in-memory, no API."""
from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy import func, select

from app.modules.customers.schemas import CustomerCreate
from app.modules.customers.service import create_customer
from app.modules.offers.models import Offer, OfferItem
from app.modules.offers.schemas import OfferCalculateIn, OfferCreate, OfferItemCreate
from app.modules.offers.service import (
    OfferAlreadyExists,
    UnknownCustomer,
    calculate_price,
    create_offer,
    distribute_costs,
    get_offer_document,
    list_offers,
)


def _customer(db, cid="0001012933"):
    return create_customer(db, CustomerCreate(customer_id=cid, account_name="UAB Riela servisas", country="Lithuania"))


def _pricing(**overrides):
    params = {
        "work_hours": Decimal("10"),
        "trip_hours_base": Decimal("3"),
        "km": Decimal("50"),
        "km_rate": Decimal("0.5"),
        "tech_rate": Decimal("60"),
        "diet_full_rate": Decimal("40"),
        "diet_half_rate": Decimal("20"),
        "hotel_rate": Decimal("80"),
        # One inspected machine -> 2 report hours (legacy rule).
        "equipment_count": 1,
    }
    params.update(overrides)
    return OfferCalculateIn(**params)


def _offer_data(cid="0001012933", number="W-02-2026-0001"):
    return OfferCreate(
        customer_id=cid,
        id_guardian_offer=number,
        pricing=_pricing(),
        items=[
            OfferItemCreate(equipment="304-565", description="Slicer", import_amount=Decimal("100.00"), workload=Decimal("6")),
            OfferItemCreate(equipment="304-565", description="Checkweigher", import_amount=Decimal("50.00"), workload=Decimal("4")),
        ],
    )


def test_calculate_is_dry_run_with_fixed_totals():
    out = calculate_price(_pricing())
    assert out.report_hours == Decimal("2.0")
    # Gross (the module lines sum to it) and net (what the client pays).
    assert out.total == Decimal("1996.00")
    assert out.total_end == Decimal("1780.00")


def test_create_offer_persists_header_and_items_with_server_totals(db):
    _customer(db)
    offer = create_offer(db, _offer_data())
    assert offer.id_guardian_offer == "W-02-2026-0001"
    # Report hours derive from the stored items: both lines share one
    # machine, so 1 x 2h.
    assert offer.report_hours == Decimal("2.0")
    assert offer.total == Decimal("1996.00")
    assert offer.total_end == Decimal("1780.00")
    assert len(offer.items) == 2
    assert [i.row_no for i in offer.items] == [1, 2]
    # The lines carry the gross spread over them (legacy "RepartirCostes"),
    # so the annex adds up with the header.
    assert sum(i.import_amount for i in offer.items) == offer.total


def test_distribute_costs_shares_the_gross_by_hours():
    items = [
        OfferItemCreate(equipment="A", description="a", import_amount=Decimal("600"), workload=Decimal("6")),
        OfferItemCreate(equipment="A", description="b", import_amount=Decimal("400"), workload=Decimal("4")),
    ]
    shares = distribute_costs(Decimal("1000.00"), items)
    assert shares == [Decimal("600.00"), Decimal("400.00")]
    assert sum(shares) == Decimal("1000.00")


def test_distribute_costs_keeps_the_cents_exact():
    # 100.00 over three equal lines: 33.33 + 33.33 + 33.34.
    items = [
        OfferItemCreate(equipment="A", description="a", import_amount=Decimal("0"), workload=Decimal("1")),
        OfferItemCreate(equipment="A", description="b", import_amount=Decimal("0"), workload=Decimal("1")),
        OfferItemCreate(equipment="A", description="c", import_amount=Decimal("0"), workload=Decimal("1")),
    ]
    shares = distribute_costs(Decimal("100.00"), items)
    assert sum(shares) == Decimal("100.00")
    assert sorted(shares) == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]


def test_distribute_costs_leaves_lines_without_hours_at_zero():
    items = [
        OfferItemCreate(equipment="A", description="a", import_amount=Decimal("0"), workload=Decimal("2")),
        OfferItemCreate(equipment="A", description="unpriced", import_amount=Decimal("0"), workload=Decimal("0")),
    ]
    shares = distribute_costs(Decimal("100.00"), items)
    assert shares == [Decimal("100.00"), Decimal("0.00")]
    assert sum(shares) == Decimal("100.00")


def test_create_offer_unknown_customer_raises_404_domain(db):
    with pytest.raises(UnknownCustomer):
        create_offer(db, _offer_data(cid="NOPE"))


def test_duplicate_number_raises_409_and_leaves_no_orphans(db):
    _customer(db)
    create_offer(db, _offer_data(number="W-02-2026-0001"))
    with pytest.raises(OfferAlreadyExists):
        create_offer(db, _offer_data(number="W-02-2026-0001"))
    assert db.scalar(select(func.count()).select_from(Offer)) == 1
    assert db.scalar(select(func.count()).select_from(OfferItem)) == 2


def test_list_offers_filters_by_customer(db):
    _customer(db, "0001012933")
    _customer(db, "0001052941")
    create_offer(db, _offer_data(cid="0001012933", number="W-02-2026-0001"))
    create_offer(db, _offer_data(cid="0001052941", number="W-02-2026-0002"))
    assert len(list_offers(db)) == 2
    only = list_offers(db, customer_id="0001012933")
    assert len(only) == 1
    assert only[0].customer_id == "0001012933"


def test_delete_offer_removes_header_and_lines(db):
    from app.modules.offers.service import delete_offer, get_offer

    _customer(db)
    offer = create_offer(db, _offer_data())
    assert delete_offer(db, offer.id) is True
    assert get_offer(db, offer.id) is None
    assert db.scalar(select(func.count()).select_from(OfferItem)) == 0
    assert delete_offer(db, offer.id) is False


def test_set_offer_status_and_bad_value(db):
    from app.modules.offers.service import BadStatus, set_offer_status

    _customer(db)
    offer = create_offer(db, _offer_data())
    closed = set_offer_status(db, offer.id, "Finished")
    assert closed is not None and closed.status == "Finished"
    with pytest.raises(BadStatus):
        set_offer_status(db, offer.id, "Burnt")


def test_summary_counts_and_ranking(db):
    from app.modules.offers.service import offers_summary

    _customer(db, "0001012933")
    _customer(db, "0001052941")
    create_offer(db, _offer_data(cid="0001012933", number="W-02-2026-0001"))
    create_offer(db, _offer_data(cid="0001012933", number="W-02-2026-0002"))
    create_offer(db, _offer_data(cid="0001052941", number="W-02-2026-0003"))
    summary = offers_summary(db)
    assert summary["total"] == 3
    assert {"status": "Pending response", "count": 3} in summary["by_status"]
    assert sum(m["count"] for m in summary["monthly"]) == 3
    top = summary["ranking"][0]
    assert top["customer_id"] == "0001012933" and top["count"] == 2


def test_summary_dashboard_rollups(db):
    from app.modules.offers.service import offers_summary, set_offer_status

    _customer(db, "0001012933")
    _customer(db, "0001052941")
    _customer(db, "0001000000")  # still has no offer
    create_offer(db, _offer_data(cid="0001012933", number="W-02-2026-0001"))
    second = create_offer(db, _offer_data(cid="0001012933", number="W-02-2026-0002"))
    create_offer(db, _offer_data(cid="0001052941", number="W-02-2026-0003"))
    set_offer_status(db, second.id, "Finished")

    summary = offers_summary(db)

    assert summary["total"] == 3
    assert summary["customers_total"] == 3
    assert summary["customers_with_offers_total"] == 2
    assert summary["customers_without_offers_total"] == 1
    assert summary["customers_without_offers"][0]["customer_id"] == "0001000000"
    assert summary["customers_without_offers"][0]["count"] == 0
    assert summary["pending_total"] == 2
    assert summary["realized_total"] == 1

    pending = {row["customer_id"]: row for row in summary["pending_customers"]}
    assert pending["0001012933"]["count"] == 1
    assert pending["0001052941"]["count"] == 1

    realized = {row["customer_id"]: row for row in summary["realized_customers"]}
    assert realized["0001012933"]["count"] == 1
    assert realized["0001012933"]["total_end"] == Decimal("1780.00")

    finished = next(row for row in summary["status_details"] if row["status"] == "Finished")
    assert finished["count"] == 1
    assert finished["total_end"] == Decimal("1780.00")
    assert finished["customers"][0]["customer_id"] == "0001012933"

    cancelled = next(row for row in summary["status_details"] if row["status"] == "Cancelled")
    assert cancelled["count"] == 0 and cancelled["customers"] == []

    assert summary["by_area"][0]["area"] == "Lithuania"
    assert summary["by_area"][0]["count"] == 3
    assert summary["ranking"][0]["customer_id"] == "0001012933"
    assert summary["ranking"][0]["account_name"] == "UAB Riela servisas"


def test_summary_groups_monthly_by_business_date(db):
    """The monthly chart must follow offer_date, not the creation stamp."""
    from app.modules.offers.service import create_offer, offers_summary

    _customer(db)
    base = _offer_data()
    create_offer(db, base.model_copy(update={"id_guardian_offer": "W-01", "offer_date": date(2026, 1, 5)}))
    create_offer(db, base.model_copy(update={"id_guardian_offer": "W-02", "offer_date": date(2026, 1, 20)}))
    create_offer(db, base.model_copy(update={"id_guardian_offer": "W-03", "offer_date": date(2026, 2, 2)}))

    months = {m["month"]: m["count"] for m in offers_summary(db)["monthly"]}
    assert months == {"2026-01": 2, "2026-02": 1}


def test_update_offer_recomputes_and_replaces_lines(db):
    from decimal import Decimal as _Decimal

    from app.modules.offers.schemas import OfferUpdate
    from app.modules.offers.service import update_offer

    _customer(db)
    # An edit without a language must keep the stored one (the form no longer
    # sends it, so a legacy offer can never lose its historical value).
    offer = create_offer(db, _offer_data().model_copy(update={"language": "Portuguese"}))
    assert len(offer.items) == 2
    updated = update_offer(
        db,
        offer.id,
        OfferUpdate(
            status="Pending response",
            pricing=_pricing(),
            items=[OfferItemCreate(equipment="X", workload=_Decimal("1"))],
        ),
    )
    assert updated is not None
    assert updated.status == "Pending response"
    assert updated.language == "Portuguese"
    # One stored machine -> 2 report hours; totals recompute from items.
    assert updated.report_hours == Decimal("2.0")
    assert updated.total == Decimal("1996.00")
    assert [i.row_no for i in updated.items] == [1]
    assert update_offer(
        db,
        offer.id,
        OfferUpdate(status="Pending response", pricing=_pricing(), items=[]),
        subsidiary_id="NOPE",
    ) is None


def test_offer_date_defaults_to_creation_day(db):
    """A new offer without offer_date lands on today, never on a silent default."""
    from app.modules.offers.service import create_offer

    _customer(db)
    offer = create_offer(db, _offer_data())
    assert offer.offer_date == date.today()


def test_offer_date_is_editable_and_survives_edits(db):
    """The business date is user data: it can be set, changed, and never wiped."""
    from app.modules.offers.schemas import OfferUpdate
    from app.modules.offers.service import create_offer, update_offer

    _customer(db)
    offer = create_offer(db, _offer_data())
    edited_date = date(2026, 2, 17)

    updated = update_offer(
        db,
        offer.id,
        OfferUpdate(status="Pending response", offer_date=edited_date, pricing=_pricing(), items=[]),
    )
    assert updated is not None
    assert updated.offer_date == edited_date

    # An edit that leaves offer_date out must keep the stored date.
    again = update_offer(
        db,
        offer.id,
        OfferUpdate(status="Pending response", pricing=_pricing(), items=[]),
    )
    assert again is not None
    assert again.offer_date == edited_date

    # The offer date is what the PDF prints, not the audit stamp.
    document = get_offer_document(db, offer.id)
    assert document.offer_date == edited_date


def test_custom_annexes_persist_and_survive_full_edits(db):
    """The annexes belong to the print modal: unrelated edits must not wipe them."""
    from app.modules.offers.document import CustomAnnex
    from app.modules.offers.schemas import CustomAnnex as CustomAnnexIn
    from app.modules.offers.schemas import OfferUpdate
    from app.modules.offers.service import create_offer, update_offer

    _customer(db)
    annexes = [CustomAnnexIn(title="SLA Addendum", body="Response in 4h.")]
    offer = create_offer(db, _offer_data().model_copy(update={"custom_annexes": annexes}))
    assert offer.custom_annexes == [
        {"title": "SLA Addendum", "body": "Response in 4h.", "body_html": None}
    ]

    # The official document carries them to the renderer.
    document = get_offer_document(db, offer.id)
    assert document.custom_annexes == (CustomAnnex(title="SLA Addendum", body="Response in 4h."),)

    # A full edit whose form does not send custom_annexes keeps them.
    updated = update_offer(
        db,
        offer.id,
        OfferUpdate(status="Pending response", pricing=_pricing(), items=[]),
    )
    assert updated is not None
    assert updated.custom_annexes == [
        {"title": "SLA Addendum", "body": "Response in 4h.", "body_html": None}
    ]


def test_patch_document_settings_updates_only_provided_fields(db):
    """Print modal auto-save: partial by design, scope-checked like any read."""
    from app.modules.offers.schemas import OfferDocumentSettingsIn
    from app.modules.offers.service import create_offer, patch_document_settings

    _customer(db)
    offer = create_offer(
        db,
        _offer_data().model_copy(
            update={
                "language": "en",
                "guardian_selections": ["maintenance_inspection", "inspection"],
            }
        ),
    )

    language_only = patch_document_settings(
        db, offer.id, OfferDocumentSettingsIn(language="de")
    )
    assert language_only is not None
    assert language_only.language == "de"
    # Untouched fields keep their values (None means "keep" on every field).
    assert language_only.guardian_selections == ["maintenance_inspection", "inspection"]
    assert language_only.custom_annexes == []

    patched = patch_document_settings(
        db,
        offer.id,
        OfferDocumentSettingsIn(
            guardian_selections=["service_support", "remote_support"],
            custom_annexes=[{"title": "Annex Z", "body": "Extra terms."}],
        ),
    )
    assert patched is not None
    assert patched.guardian_selections == ["service_support", "remote_support"]
    assert patched.custom_annexes == [
        {"title": "Annex Z", "body": "Extra terms.", "body_html": None}
    ]
    assert patched.language == "de"

    # Out-of-scope writes read as missing, same as every other mutation.
    assert (
        patch_document_settings(
            db, offer.id, OfferDocumentSettingsIn(language="es"), subsidiary_id="NOPE"
        )
        is None
    )
