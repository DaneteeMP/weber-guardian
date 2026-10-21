"""Subsidiary catalog contracts for shared filial selectors."""
from pydantic import BaseModel, ConfigDict, Field


class SubsidiaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    short_label: str


class SubsidiaryCountryOut(BaseModel):
    """One row of the supervision mapping (country -> subsidiary)."""

    model_config = ConfigDict(from_attributes=True)

    country: str
    subsidiary: str


class SubsidiaryCountryIn(BaseModel):
    """Create or move a country. The subsidiary must exist in the catalog."""

    country: str = Field(min_length=1, max_length=128)
    subsidiary: str = Field(min_length=1, max_length=64)


class SubsidiaryStatsOut(BaseModel):
    """Per-subsidiary counters for the admin tab: supervised countries and
    customers tagged with this subsidiary."""

    name: str
    short_label: str
    countries: int
    customers: int


class UnassignedCountryOut(BaseModel):
    """A customer country with no supervising subsidiary in the map, by volume."""

    country: str
    count: int
