"""Basic-kit contracts (Pydantic). Read-only."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class BasicKitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model: str
    workload_basic_kit: Decimal
    spare_parts: Decimal
