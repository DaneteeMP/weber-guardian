"""Official offer document (pure data, no drawing).

The PDF renderer (Weber adapter) consumes this. The core never imports
the adapter: main.py injects the real renderer where a PdfRenderer is
needed. Amounts stay Decimal until the renderer formats them.
"""
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Protocol
import uuid


@dataclass(frozen=True)
class OfferLine:
    pos: int
    equipment: str | None
    description: str | None
    import_amount: Decimal


@dataclass(frozen=True)
class OfferDocument:
    offer_id: uuid.UUID
    number: str
    offer_date: date | None
    status: str
    language: str
    inspection_frequency: str | None
    responsible_person: str | None
    subsidiary_id: str | None
    account_name: str
    account_city: str | None
    account_province: str | None
    account_country: str | None
    currency: str
    trip_cost: Decimal
    diets: Decimal
    hotel_cost: Decimal
    trip_hours: Decimal
    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    hours_import: Decimal
    expenses: Decimal
    discount: Decimal
    bk_price: Decimal
    total: Decimal
    total_end: Decimal
    general_comments: str | None
    lines: tuple[OfferLine, ...] = field(default_factory=tuple)


class PdfRenderer(Protocol):
    """Port: turns an official document into PDF bytes."""

    def __call__(self, doc: OfferDocument) -> bytes: ...
