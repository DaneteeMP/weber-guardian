"""Distance HTTP. Thin lookup + admin upsert: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.distances import service
from app.modules.distances.schemas import DistanceOut, DistanceUpdate

router = APIRouter(prefix="/distances", tags=["distances"])


@router.get("", response_model=list[DistanceOut])
def list_endpoint(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_distances(db, limit=limit, offset=offset)


@router.get("/{province}", response_model=DistanceOut)
def get_endpoint(
    province: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    row = service.get_distance(db, province)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown province")
    return row


@router.put("/{province}", response_model=DistanceOut)
def update_endpoint(
    province: str,
    payload: DistanceUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    return service.upsert_distance(db, province, payload)
