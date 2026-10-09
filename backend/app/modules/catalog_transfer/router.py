"""HTTP API to move the editable catalog between databases.

Export is a read of global reference data (any authenticated user). Import
writes everything at once, so it is limited to the roles that edit the catalog.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.catalog_transfer import service
from app.modules.catalog_transfer.schemas import CatalogDocument, CatalogImportReport

router = APIRouter(prefix="/catalog", tags=["catalog"])

WRITE_ROLES = require_role("admin", "sales")


@router.get("/export", response_model=CatalogDocument)
def export_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """Download every workload rule and machine line as one portable JSON file."""
    return service.export_catalog(db)


@router.post("/import", response_model=CatalogImportReport)
def import_endpoint(
    payload: CatalogDocument,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(WRITE_ROLES),
):
    """Upsert a snapshot. Idempotent and non-destructive: it never deletes."""
    try:
        return service.import_catalog(db, payload)
    except service.CatalogImportError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
