"""HTTP API for machine-line workloads (equipment_catalog, kind="line").

The line is the machine itself, priced by family (e.g. "40x" for the 402/404/405
slicers). The Offers tab edits it from the "Workload not configured" badge, the
same way it edits modules and slicer products.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.equipment_catalog import service
from app.modules.equipment_catalog.schemas import (
    EquipmentCatalogEntryOut,
    LineWorkloadUpdateIn,
)

router = APIRouter(prefix="/line-workloads", tags=["line-workloads"])


@router.get("", response_model=list[EquipmentCatalogEntryOut])
def list_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_entries(db)


@router.put("/{machine_type}", response_model=EquipmentCatalogEntryOut)
def update_endpoint(
    machine_type: str,
    payload: LineWorkloadUpdateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    """Set the hours of one line, creating the entry when the code is new."""
    try:
        return service.upsert_line_workload(
            db, machine_type, payload.workload, payload.label
        )
    except service.EquipmentCatalogConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
