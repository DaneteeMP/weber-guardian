"""Pydantic contracts for the global equipment catalog."""
from datetime import datetime
from decimal import Decimal
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator


CatalogKind = Literal["line"]
MatchField = Literal["machine_type"]


class EquipmentCatalogMatchIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    match_field: MatchField
    match_value: str = Field(min_length=1, max_length=64)
    is_confirmed: bool = False


class EquipmentCatalogMatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    match_field: MatchField
    match_value: str
    is_confirmed: bool


class EquipmentCatalogEntryIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    kind: CatalogKind
    label: str = Field(min_length=1, max_length=128)
    # Hours only. The amount is computed server-side from the branch rate.
    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    matches: list[EquipmentCatalogMatchIn] = Field(default_factory=list)
    _seen_values: set[str] = set()

    @model_validator(mode="after")
    def validate_matches(self) -> "EquipmentCatalogEntryIn":
        for match in self.matches:
            if match.match_field != "machine_type":
                raise ValueError("line entries require machine_type matches")
            if match.match_value in self._seen_values:
                raise ValueError(f"Duplicate match value: {match.match_value}")
            self._seen_values.add(match.match_value)
        return self


class EquipmentCatalogEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    kind: CatalogKind
    label: str
    workload: Decimal | None
    matches: list[EquipmentCatalogMatchOut]
    created_at: datetime


class LineWorkloadUpdateIn(BaseModel):
    """Set the hours of one machine line (equipment_catalog)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    # Only used when the machine_type is new and an entry must be created.
    label: str | None = Field(default=None, min_length=1, max_length=128)
