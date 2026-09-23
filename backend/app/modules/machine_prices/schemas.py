"""Machine-price contracts (Pydantic). Read + admin upsert/delete."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class MachinePriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model: str
    annual_price: Decimal
    inspections_per_year: int
    currency: str


class MachinePriceUpsert(BaseModel):
    annual_price: Decimal = Field(ge=Decimal("0"))
    inspections_per_year: int = Field(ge=1, le=52)
    currency: str = Field(default="EUR", min_length=1, max_length=8)
