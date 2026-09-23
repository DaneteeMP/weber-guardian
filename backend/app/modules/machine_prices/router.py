"""Machine-price HTTP. Thin lookup + admin upsert/delete."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.machine_prices import service
from app.modules.machine_prices.schemas import MachinePriceOut, MachinePriceUpsert

router = APIRouter(prefix="/machine-prices", tags=["machine_prices"])


@router.get("", response_model=list[MachinePriceOut])
def list_endpoint(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_prices(db, limit=limit, offset=offset)


@router.get("/{model}", response_model=MachinePriceOut)
def get_endpoint(
    model: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    row = service.get_price(db, model)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No price for model")
    return row


@router.put("/{model}", response_model=MachinePriceOut)
def update_endpoint(
    model: str,
    payload: MachinePriceUpsert,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    return service.upsert_price(db, model, payload)


@router.delete("/{model}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    model: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    if not service.delete_price(db, model):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No price for model")
