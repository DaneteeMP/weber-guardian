"""Equipment contracts (Pydantic). Read-only for now: rows are born in the CSV import."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class CustomerSiteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    physical_street: str | None
    physical_city: str | None
    physical_postal_code: str | None
    physical_province: str | None
    physical_country: str | None


class EquipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: str
    equipment_name: str | None
    machine_type: str | None
    component_type: str | None
    material_no: str | None
    purchase_date: str | None
    site: CustomerSiteOut | None
    row_hash: str
    created_at: datetime
