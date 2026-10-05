"""HTTP API for the product-based Workload Catalog.

This is the visible catalog API. The component_names table and its importer
remain internal support for resolving SAP material numbers.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.component_names import service as component_name_service
from app.modules.component_names import workloads as workload_service
from app.modules.component_names.schemas import (
    ComponentWorkloadCreateIn,
    ComponentWorkloadOut,
    ComponentWorkloadUpdateIn,
    WorkloadImportReportOut,
)

router = APIRouter(prefix="/component-workloads", tags=["component-workloads"])


@router.post("/import", response_model=WorkloadImportReportOut)
async def import_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    """Import SAP product identities and add only new workload products."""
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="uploaded file is empty",
        )
    try:
        return workload_service.import_workload_catalog(db, content)
    except component_name_service.DictionaryFileError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("", response_model=list[ComponentWorkloadOut])
def list_endpoint(
    response: Response,
    search: str | None = Query(default=None, min_length=1, max_length=128),
    component_type: str | None = Query(default=None, min_length=1, max_length=128),
    needs_review: bool | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    rows = workload_service.list_workloads(
        db,
        search=search,
        component_type=component_type,
        needs_review=needs_review,
        limit=limit,
        offset=offset,
    )
    response.headers["X-Total-Count"] = str(
        workload_service.count_workloads(
            db,
            search=search,
            component_type=component_type,
            needs_review=needs_review,
        )
    )
    return rows


@router.post("", response_model=ComponentWorkloadOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    payload: ComponentWorkloadCreateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    try:
        return workload_service.create_workload(db, payload)
    except workload_service.ComponentWorkloadConflict as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A workload already exists for this component type or Slicer model",
        ) from exc


@router.patch("/{workload_id}", response_model=ComponentWorkloadOut)
def update_endpoint(
    workload_id: UUID,
    payload: ComponentWorkloadUpdateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    try:
        return workload_service.update_workload(
            db,
            workload_id,
            payload.model_dump(exclude_unset=True),
        )
    except workload_service.ComponentWorkloadNotFound as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component workload not found",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.delete("/{workload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    workload_id: UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    if not workload_service.delete_workload(db, workload_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Component workload not found",
        )
