"""Import contracts (Pydantic). The report is the product of an upload.

A real run is atomic: any row error aborts with 422 and this report,
nothing is stored. dry_run=true never writes, it only returns the report.
"""
from pydantic import BaseModel, Field


class RowError(BaseModel):
    # line 1 = file/header level, >= 2 = data rows (header is line 1).
    line: int = Field(ge=1)
    reason: str = Field(min_length=1)


class ImportReport(BaseModel):
    dry_run: bool
    total_rows: int = Field(ge=0)
    customers_created: int = Field(ge=0)
    customers_skipped: int = Field(ge=0)
    equipment_created: int = Field(ge=0)
    equipment_skipped: int = Field(ge=0)
    errors: list[RowError] = Field(default_factory=list)
    # Non-blocking notes (e.g. countries without a supervising filial).
    warnings: list[str] = Field(default_factory=list)
