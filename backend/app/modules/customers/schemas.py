"""Pydantic schemas: validate what enters/leaves over HTTP. They never touch the DB."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    account_name: str = Field(min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=128)
    province: str | None = Field(default=None, min_length=1, max_length=128)
    country: str | None = Field(default=None, min_length=1, max_length=64)


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: str
    account_name: str
    city: str | None
    province: str | None
    country: str | None
    created_at: datetime
