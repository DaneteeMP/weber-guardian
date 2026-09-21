"""Distance contracts (Pydantic). Read-only."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class DistanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    province: str
    km: Decimal
    trip_hours: Decimal
