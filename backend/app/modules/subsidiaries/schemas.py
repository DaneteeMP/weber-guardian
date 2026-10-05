"""Subsidiary catalog contracts for shared filial selectors."""
from pydantic import BaseModel, ConfigDict


class SubsidiaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    short_label: str
