"""Price contracts (Pydantic). Each subsidiary explicitly manages its own rates."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subsidiary_id: str
    currency: str
    km_rate: Decimal
    tech_rate: Decimal
    diet_full_rate: Decimal
    diet_half_rate: Decimal
    hotel_rate: Decimal
    discount_rate: Decimal


class PriceUpdate(BaseModel):
    """Full rate replacement. Every filial edits its own numbers here."""

    currency: str = Field(min_length=1, max_length=8)
    km_rate: Decimal = Field(ge=Decimal("0"))
    tech_rate: Decimal = Field(ge=Decimal("0"))
    diet_full_rate: Decimal = Field(ge=Decimal("0"))
    diet_half_rate: Decimal = Field(ge=Decimal("0"))
    hotel_rate: Decimal = Field(ge=Decimal("0"))
    discount_rate: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
