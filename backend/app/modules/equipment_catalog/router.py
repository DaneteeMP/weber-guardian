"""HTTP endpoints for the global equipment catalog."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.equipment_catalog import service
from app.modules.equipment_catalog.schemas import (
    EquipmentCatalogEntryIn,
    EquipmentCatalogEntryOut,
)


router = APIRouter(prefix="/equipment-catalog", tags=["equipment_catalog"])


@router.get("", response_model=list[EquipmentCatalogEntryOut])
def list_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_entries(db)


@router.post("", response_model=EquipmentCatalogEntryOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    payload: EquipmentCatalogEntryIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    try:
        return service.create_entry(db, payload)
    except service.EquipmentCatalogConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.put("/{entry_id}", response_model=EquipmentCatalogEntryOut)
def update_endpoint(
    entry_id: UUID,
    payload: EquipmentCatalogEntryIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    try:
        row = service.update_entry(db, entry_id, payload)
    except service.EquipmentCatalogConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog entry not found")
    return row


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    entry_id: UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    try:
        found = service.delete_entry(db, entry_id)
    except service.EquipmentCatalogInUse as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if not found:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalog entry not found")
