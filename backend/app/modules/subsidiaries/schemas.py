"""Subsidiary contracts (Pydantic). Read-only catalog for pickers and badges."""
from pydantic import BaseModel, ConfigDict, Field


class SubsidiaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    short_label: str


class SubsidiaryStatsOut(BaseModel):
    name: str
    short_label: str
    countries: int
    customers: int


class UnassignedCountryOut(BaseModel):
    country: str
    count: int


class CountryAssignment(BaseModel):
    country: str = Field(min_length=1, max_length=128)
    subsidiary: str = Field(min_length=1, max_length=64)


class AssignCountriesIn(BaseModel):
    assignments: list[CountryAssignment] = Field(min_length=1)


class AssignCountriesOut(BaseModel):
    updated: int


class AutoAssignOut(BaseModel):
    updated: int
    warnings: list[str] = Field(default_factory=list)
