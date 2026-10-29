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
    band1_rate_without: Decimal | None
    band1_rate_with: Decimal | None
    band2_rate_without: Decimal | None
    band2_rate_with: Decimal | None
    band3_rate_without: Decimal | None
    band3_rate_with: Decimal | None


class PriceUpdate(BaseModel):
    """Full rate replacement. Every filial edits its own numbers here."""

    currency: str = Field(min_length=1, max_length=8)
    km_rate: Decimal = Field(ge=Decimal("0"))
    tech_rate: Decimal = Field(ge=Decimal("0"))
    diet_full_rate: Decimal = Field(ge=Decimal("0"))
    diet_half_rate: Decimal = Field(ge=Decimal("0"))
    hotel_rate: Decimal = Field(ge=Decimal("0"))
    discount_rate: Decimal = Field(ge=Decimal("0"), le=Decimal("1"))
    # Optional: NULL means "not configured", so the PDF omits the rates block.
    band1_rate_without: Decimal | None = Field(default=None, ge=Decimal("0"))
    band1_rate_with: Decimal | None = Field(default=None, ge=Decimal("0"))
    band2_rate_without: Decimal | None = Field(default=None, ge=Decimal("0"))
    band2_rate_with: Decimal | None = Field(default=None, ge=Decimal("0"))
    band3_rate_without: Decimal | None = Field(default=None, ge=Decimal("0"))
    band3_rate_with: Decimal | None = Field(default=None, ge=Decimal("0"))
