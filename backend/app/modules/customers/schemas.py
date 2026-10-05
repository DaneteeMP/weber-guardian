"""Pydantic schemas: validate what enters/leaves over HTTP. They never touch the DB."""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.equipment.schemas import CustomerSiteOut


class CustomerCreate(BaseModel):
    customer_id: str = Field(min_length=1, max_length=64)
    account_name: str = Field(min_length=1, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=128)
    province: str | None = Field(default=None, min_length=1, max_length=128)
    country: str | None = Field(default=None, min_length=1, max_length=64)
    subsidiary_id: str | None = Field(default=None, min_length=1, max_length=64)


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    customer_id: str
    account_name: str
    city: str | None
    province: str | None
    country: str | None
    subsidiary_id: str | None
    created_at: datetime


class CustomerComponentOut(BaseModel):
    """One installed row of a machine.

    A machine's own row (component_type "Slicer" or "Line") sits here beside its
    modules, because SAP stores both in the same table with the same
    equipment_name. The UI shows the machine row and the module rows together
    under one machine heading; nothing classifies them as "the machine" vs "a
    module" until the workload rules need to, in the maintenance draft.
    """

    component_type: str | None
    material_no: str | None
    purchase_date: str | None


class CustomerMachineOut(BaseModel):
    """A machine the customer owns, with every installed component row on it."""

    equipment_name: str
    machine_type: str | None
    site_id: uuid.UUID | None
    components: list[CustomerComponentOut]


class CustomerDetailOut(BaseModel):
    """One customer with its addresses and its machines.

    This is the aggregate the Clientes tab shows after selecting a row: the
    address to visit, and the fleet to maintain. It has no ORM model of its own
    (it spans customers, customer_sites and equipment), so the service builds
    it directly.
    """

    customer: CustomerOut
    sites: list[CustomerSiteOut]
    machines: list[CustomerMachineOut]
