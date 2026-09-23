"""Distance contracts (Pydantic). Read + admin upsert."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DistanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    province: str
    km: Decimal
    trip_hours: Decimal


class DistanceUpdate(BaseModel):
    """Full replacement; creates the row when the province is new."""

    km: Decimal = Field(ge=Decimal("0"))
    trip_hours: Decimal = Field(ge=Decimal("0"))
