"""Responsible contracts (Pydantic). Admin-managed dropdown values."""
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ResponsibleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    subsidiary_id: str
    name: str
    active: bool


class ResponsibleCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    subsidiary_id: str = Field(min_length=1, max_length=64)
    name: str = Field(min_length=1, max_length=128)


class ResponsibleUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=128)
    active: bool | None = None
