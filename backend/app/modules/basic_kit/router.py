"""Basic-kit HTTP. Thin lookup + admin create/delete: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.basic_kit import service
from app.modules.basic_kit.schemas import BasicKitCreate, BasicKitOut

router = APIRouter(prefix="/basic-kit", tags=["basic_kit"])


@router.get("", response_model=list[BasicKitOut])
def list_endpoint(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_kits(db, limit=limit, offset=offset)


@router.get("/{model}", response_model=BasicKitOut)
def get_endpoint(
    model: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    row = service.get_kit(db, model)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No kit for model")
    return row


@router.post("", response_model=BasicKitOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    payload: BasicKitCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    try:
        return service.create_kit(db, payload)
    except service.KitAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{model}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    model: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    if not service.delete_kit(db, model):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No kit for model")
