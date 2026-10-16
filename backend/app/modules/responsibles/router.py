"""Responsible HTTP. Thin scoped CRUD: validates, calls service, returns."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.responsibles import service
from app.modules.responsibles.schemas import ResponsibleCreate, ResponsibleOut, ResponsibleUpdate

router = APIRouter(prefix="/responsibles", tags=["responsibles"])


def _forbid_out_of_scope(current: CurrentUser, subsidiary_id: str) -> None:
    """Scoped identities only touch their own subsidiary; anything else is 404
    (not 403, so existence never leaks across subsidiaries)."""
    if current.subsidiary_id is not None and current.subsidiary_id != subsidiary_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No responsibles for subsidiary")


@router.get("", response_model=list[ResponsibleOut])
def list_endpoint(
    subsidiary_id: str = Query(min_length=1, max_length=64),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    _forbid_out_of_scope(current, subsidiary_id)
    return service.list_responsibles(db, subsidiary_id)


@router.post("", response_model=ResponsibleOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    payload: ResponsibleCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    _forbid_out_of_scope(current, payload.subsidiary_id)
    try:
        return service.create_responsible(db, payload)
    except service.SubsidiaryNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.ResponsibleAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.patch("/{responsible_id}", response_model=ResponsibleOut)
def update_endpoint(
    responsible_id: uuid.UUID,
    payload: ResponsibleUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    row = service.get_responsible(db, responsible_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No responsible found")
    _forbid_out_of_scope(current, row.subsidiary_id)
    try:
        updated = service.update_responsible(db, responsible_id, payload)
    except service.ResponsibleAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    if updated is None:  # pragma: no cover - deleted between the two reads
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No responsible found")
    return updated


@router.delete("/{responsible_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    responsible_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    row = service.get_responsible(db, responsible_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No responsible found")
    _forbid_out_of_scope(current, row.subsidiary_id)
    service.delete_responsible(db, responsible_id)
