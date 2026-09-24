"""Basic-kit contracts (Pydantic). Lookup + admin create/delete."""
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class BasicKitOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    model: str
    workload_basic_kit: Decimal
    spare_parts: Decimal


class BasicKitCreate(BaseModel):
    model: str = Field(min_length=1, max_length=64)
    workload_basic_kit: Decimal = Field(ge=Decimal("0"))
    spare_parts: Decimal = Field(ge=Decimal("0"))


class BasicKitUpsert(BaseModel):
    workload_basic_kit: Decimal = Field(ge=Decimal("0"))
    spare_parts: Decimal = Field(ge=Decimal("0"))
