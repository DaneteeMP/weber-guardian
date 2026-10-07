"""Pydantic contracts for the cleaned component name dictionary."""
from datetime import datetime
from decimal import Decimal
import uuid

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ComponentNameOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    material_no: str
    name_en: str
    type_code: str | None
    component_type: str | None
    description: str | None
    source_rows: int
    has_conflict: bool
    created_at: datetime


class ComponentNameUpdateIn(BaseModel):
    """Manual edit of a cleaned row, used to settle conflicting entries."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name_en: str | None = Field(default=None, min_length=1, max_length=256)
    type_code: str | None = Field(default=None, max_length=64)
    component_type: str | None = Field(default=None, max_length=128)
    description: str | None = Field(default=None, max_length=512)
    has_conflict: bool | None = None


class ImportReportOut(BaseModel):
    """What one dictionary import did, so a bad file is visible, not silent.

    The file is the legacy German/English export, so every number here can go
    wrong in a way that must be read, not guessed at.
    """

    encoding: str
    rows_read: int
    rows_blank: int
    rows_without_material_no: int
    material_numbers_without_name: int
    entries_written: int
    entries_total_after: int
    entries_with_conflict: int
    duplicate_rows_collapsed: int
    stale_entries_deleted: int
    unmapped_material_numbers: list[str] = Field(default_factory=list)


class ComponentWorkloadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    component_type: str
    workload: Decimal | None
    needs_review: bool
    legacy_type_code: str | None
    created_at: datetime


class ComponentWorkloadCreateIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=256)
    component_type: str = Field(min_length=1, max_length=128)
    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    needs_review: bool | None = None

    @model_validator(mode="after")
    def validate_review_state(self) -> "ComponentWorkloadCreateIn":
        if self.workload is None and self.needs_review is False:
            raise ValueError("a workload without hours must remain marked for review")
        return self


class ComponentWorkloadUpdateIn(BaseModel):
    """Edit workload values without changing the product identity."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=256)
    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    needs_review: bool | None = None


class ModuleWorkloadOut(BaseModel):
    """Legacy module workload, keyed by the component type code."""

    model_config = ConfigDict(from_attributes=True)

    type_code: str
    label: str
    workload: Decimal | None
    needs_review: bool


class ModuleWorkloadUpdateIn(BaseModel):
    """Set the legacy hours of one module type_code."""

    model_config = ConfigDict(str_strip_whitespace=True)

    workload: Decimal | None = Field(default=None, ge=Decimal("0"))
    needs_review: bool | None = None
    # Only used when the type_code is new and a row must be created.
    label: str | None = Field(default=None, min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_review_state(self) -> "ModuleWorkloadUpdateIn":
        if self.workload is None and self.needs_review is False:
            raise ValueError("a workload without hours must remain marked for review")
        return self


class WorkloadImportReportOut(BaseModel):
    """Summary of dictionary cleaning and product workload reconciliation."""

    encoding: str
    rows_read: int
    rows_blank: int
    rows_without_material_no: int
    source_entries: int
    source_conflicts: int
    products_discovered: int
    workloads_created: int
    workloads_preserved: int
    workloads_needing_review_created: int
    rows_without_component_type: int
