"""Offer HTTP contracts (Pydantic). Backend owns all prices.

Clients never send totals: CalculateOut/OfferOut carry them, Create
schemas do not. All money is Decimal (EUR explicit).
"""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

Money = Decimal
MAX12 = 9999999999.99


class OfferItemCreate(BaseModel):
    equipment: str | None = Field(default=None, max_length=64)
    description: str | None = Field(default=None, max_length=500)
    import_amount: Decimal = Field(default=Decimal("0"), ge=Decimal("0"), le=Decimal(str(MAX12)))
    workload: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))


class OfferItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    row_no: int
    equipment: str | None
    description: str | None
    import_amount: Decimal
    workload: Decimal


class OfferCalculateIn(BaseModel):
    """Dry-run input: aggregated hours + rates. No persistence."""

    work_hours: Decimal = Field(ge=Decimal("0"))
    bk_hours: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    report_hours: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    trip_hours_base: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    km: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    km_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    tech_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    diet_full_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    diet_half_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    hotel_rate: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    discount_rate: Decimal = Field(default=Decimal("0.15"), ge=Decimal("0"), le=Decimal("1"))
    bk_price: Decimal = Field(default=Decimal("0"), ge=Decimal("0"))
    currency: str = Field(default="EUR", min_length=1, max_length=8)


class OfferCalculateOut(BaseModel):
    """Engine breakdown. total = gross, total_end = net."""

    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    num_days: int
    trip_cost: Decimal
    trip_hours: Decimal
    diets: Decimal
    hotel_nights_cost: Decimal
    expenses: Decimal
    hours_import: Decimal
    discount: Decimal
    bk_price: Decimal
    total: Decimal
    total_end: Decimal
    currency: str


class OfferCreate(BaseModel):
    """Create input. Totals are computed server-side, never accepted."""

    customer_id: str = Field(min_length=1, max_length=64)
    id_guardian_offer: str | None = Field(default=None, min_length=1, max_length=64)
    status: str = Field(default="Draft", min_length=1, max_length=32)
    responsible_person: str | None = Field(default=None, max_length=128)
    language: str | None = Field(default=None, max_length=32)
    inspection_frequency: str | None = Field(default=None, max_length=32)
    general_comments: str | None = Field(default=None, max_length=2000)
    pricing: OfferCalculateIn
    items: list[OfferItemCreate] = Field(default_factory=list)


class OfferOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    id_guardian_offer: str
    customer_id: str
    status: str
    responsible_person: str | None
    language: str | None
    inspection_frequency: str | None
    currency: str
    work_hours: Decimal
    bk_hours: Decimal
    report_hours: Decimal
    total_hours: Decimal
    trip_hours: Decimal
    trip_cost: Decimal
    diets: Decimal
    hotel_cost: Decimal
    expenses: Decimal
    hours_import: Decimal
    discount: Decimal
    bk_price: Decimal
    total: Decimal
    total_end: Decimal
    general_comments: str | None
    created_at: datetime
    items: list[OfferItemOut] = Field(default_factory=list)
