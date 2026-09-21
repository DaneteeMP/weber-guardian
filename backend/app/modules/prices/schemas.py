"""Price contracts (Pydantic). Read-only: rows are seeded, admin CRUD arrives in F4."""
import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PriceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subsidiary_id: str
    currency: str
    km_rate: Decimal
    tech_rate: Decimal
    diet_full_rate: Decimal
    diet_half_rate: Decimal
    hotel_rate: Decimal
