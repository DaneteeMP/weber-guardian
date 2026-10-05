"""Distance contracts (Pydantic). Read + admin upsert."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class DistanceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subsidiary_id: str
    province: str
    province_code: str | None
    region: str | None
    capital: str | None
    reference_city: str | None
    service_center: str | None
    origin_city: str | None
    km: Decimal
    driving_hours: Decimal | None
    trip_hours: Decimal
    itinerary: str | None
    route_data_date: date | None


class DistanceUpdate(BaseModel):
    """Full replacement of one subsidiary/province route row."""

    capital: str | None = Field(default=None, max_length=128)
    service_center: str | None = Field(default=None, max_length=64)
    province_code: str | None = Field(default=None, max_length=8)
    region: str | None = Field(default=None, max_length=128)
    reference_city: str | None = Field(default=None, max_length=128)
    origin_city: str | None = Field(default=None, max_length=128)
    km: Decimal = Field(ge=Decimal("0"))
    driving_hours: Decimal | None = Field(default=None, ge=Decimal("0"))
    trip_hours: Decimal = Field(ge=Decimal("0"))
    itinerary: str | None = Field(default=None, max_length=255)
    route_data_date: date | None = None


class DistanceImportRowError(BaseModel):
    line: int = Field(ge=2)
    reason: str = Field(min_length=1)


class DistanceImportReport(BaseModel):
    dry_run: bool
    total_rows: int = Field(ge=0)
    created: int = Field(ge=0)
    updated: int = Field(ge=0)
    errors: list[DistanceImportRowError] = Field(default_factory=list)
