"""Distance HTTP. Every route is resolved within a filial scope."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.core.subsidiaries import normalize_subsidiary
from app.modules.distances import service
from app.modules.distances.schemas import DistanceImportReport, DistanceOut, DistanceUpdate

router = APIRouter(prefix="/distances", tags=["distances"])


def _target_subsidiary(current: CurrentUser, requested: str | None) -> str | None:
    """Resolve an explicit route-table filial without crossing user scope."""
    wanted = normalize_subsidiary(requested)
    if current.role == "admin":
        if current.scope_subsidiary_id is not None:
            if wanted is not None and wanted != current.scope_subsidiary_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Scope limited to selected subsidiary")
            return current.scope_subsidiary_id
        return wanted

    if wanted is not None and wanted != current.scope_subsidiary_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Scope limited to assigned subsidiary")
    return current.scope_subsidiary_id


def _require_subsidiary(subsidiary_id: str | None) -> str:
    if subsidiary_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Select a subsidiary before looking up or changing a province distance",
        )
    return subsidiary_id


@router.get("", response_model=list[DistanceOut])
def list_endpoint(
    subsidiary_id: str | None = Query(default=None, min_length=1, max_length=64),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    target = _target_subsidiary(current, subsidiary_id)
    if target is not None:
        try:
            service.validate_subsidiary(db, target)
        except service.UnknownSubsidiary as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return service.list_distances(db, subsidiary_id=target, limit=limit, offset=offset)


@router.post("/import", response_model=DistanceImportReport)
async def import_endpoint(
    file: UploadFile,
    subsidiary_id: str = Query(min_length=1, max_length=64),
    origin_city: str = Query(min_length=1, max_length=128),
    route_data_date: date = Query(),
    dry_run: bool = Query(default=True),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    target = _require_subsidiary(_target_subsidiary(current, subsidiary_id))
    try:
        report = service.import_route_csv(
            db,
            await file.read(),
            subsidiary_id=target,
            origin_city=origin_city,
            route_data_date=route_data_date,
            dry_run=dry_run,
        )
    except service.UnknownSubsidiary as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except service.DistanceImportConflict as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if report.errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=report.model_dump())
    return report


@router.get("/{province}", response_model=DistanceOut)
def get_endpoint(
    province: str,
    subsidiary_id: str | None = Query(default=None, min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    target = _require_subsidiary(_target_subsidiary(current, subsidiary_id))
    row = service.get_distance(db, target, province)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown province for subsidiary")
    return row


@router.put("/{province}", response_model=DistanceOut)
def update_endpoint(
    province: str,
    payload: DistanceUpdate,
    subsidiary_id: str | None = Query(default=None, min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    target = _require_subsidiary(_target_subsidiary(current, subsidiary_id))
    try:
        return service.upsert_distance(db, target, province, payload)
    except service.UnknownSubsidiary as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except service.InvalidServiceCenter as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.delete("/{province}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    province: str,
    subsidiary_id: str | None = Query(default=None, min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    target = _require_subsidiary(_target_subsidiary(current, subsidiary_id))
    if not service.delete_distance(db, target, province):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown province for subsidiary")
