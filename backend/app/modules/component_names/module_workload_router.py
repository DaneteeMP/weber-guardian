"""HTTP API for the legacy module workloads, keyed by component type code.

Ordinary maintenance modules price from this table (the restored legacy
``TblWorkLoad``). Slicers price from the product catalog
(``component_workloads``). Both are the same "Workload Catalog" from the user's
point of view, so both are editable here.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.component_names import workloads as workload_service
from app.modules.component_names.schemas import (
    ModuleWorkloadOut,
    ModuleWorkloadUpdateIn,
)

router = APIRouter(prefix="/module-workloads", tags=["module-workloads"])


@router.get("", response_model=list[ModuleWorkloadOut])
def list_endpoint(
    response: Response,
    search: str | None = Query(default=None, min_length=1, max_length=128),
    needs_review: bool | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    rows = workload_service.list_module_workloads(
        db, search=search, needs_review=needs_review, limit=limit, offset=offset
    )
    response.headers["X-Total-Count"] = str(
        workload_service.count_module_workloads(db, search=search, needs_review=needs_review)
    )
    return rows


@router.put("/{type_code}", response_model=ModuleWorkloadOut)
def update_endpoint(
    type_code: str,
    payload: ModuleWorkloadUpdateIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    """Set the hours of one module type_code (offer badge / catalog edit).

    A code the legacy list never had is created on the spot: the offer shows it
    because a real machine carries it, so it must be configurable.
    """
    try:
        return workload_service.update_module_workload(
            db, type_code, payload.workload, payload.needs_review, payload.label
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc
