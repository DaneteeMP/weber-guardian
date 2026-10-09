"""Pydantic contracts for global workload rules and material links.

Hours are Decimal end to end (never float). A rule without hours is always
marked for review, enforced here and again in the service.
"""
from datetime import datetime
from decimal import Decimal
from typing import Literal
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WorkloadRuleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    workload: Decimal | None
    legacy_type_code: str | None
    category: str
    needs_review: bool
    note: str | None
    linked_materials: int
    created_at: datetime


class WorkloadRuleCreateIn(BaseModel):
    """A rule created by hand. The legacy code is optional; the category is set by the system."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=128)
    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    legacy_type_code: str | None = Field(default=None, max_length=16)
    needs_review: bool | None = None

    @model_validator(mode="after")
    def validate_review_state(self) -> "WorkloadRuleCreateIn":
        if self.workload is None and self.needs_review is False:
            raise ValueError("a workload rule without hours must remain marked for review")
        return self


class WorkloadRuleUpdateIn(BaseModel):
    """Edit the name, hours, legacy code and review flag.

    Fields that are not sent keep their stored value.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=128)
    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    legacy_type_code: str | None = Field(default=None, max_length=16)
    needs_review: bool | None = None

    @model_validator(mode="after")
    def validate_review_state(self) -> "WorkloadRuleUpdateIn":
        if self.workload is None and self.needs_review is False:
            raise ValueError("a workload rule without hours must remain marked for review")
        return self


class RuleMaterialOut(BaseModel):
    """One dictionary material linked to a rule."""

    material_no: str
    name_en: str | None
    type_code: str | None
    component_type: str | None
    has_conflict: bool
    customers: int


class WorkloadRuleDetailOut(WorkloadRuleOut):
    materials: list[RuleMaterialOut]


class MaterialLinkIn(BaseModel):
    workload_rule_id: uuid.UUID


class MaterialLinkOut(BaseModel):
    material_no: str
    workload_rule_id: uuid.UUID
    previous_rule_id: uuid.UUID | None
    previous_rule_name: str | None
    changed: bool


class MaterialRuleOut(BaseModel):
    id: uuid.UUID
    name: str
    workload: Decimal | None
    needs_review: bool


class MaterialResolutionOut(BaseModel):
    """How one material number resolves today, shown in the catalog search."""

    material_no: str
    state: Literal["resolved", "no_rule", "not_in_dictionary", "slicer"]
    dictionary_material_no: str | None
    name_en: str | None
    type_code: str | None
    component_type: str | None
    has_conflict: bool
    rule: MaterialRuleOut | None
    customers: int


class UnresolvedMaterialOut(BaseModel):
    material_no: str
    name_en: str | None
    type_code: str | None
    component_type: str | None
    reason: Literal["no_rule", "no_hours", "dictionary_conflict", "not_in_dictionary"]
    customers: int
