"""Price HTTP. Thin read/update: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.prices import service
from app.modules.prices.schemas import PriceOut, PriceUpdate

router = APIRouter(prefix="/prices", tags=["prices"])


@router.get("/{subsidiary_id}", response_model=PriceOut)
def get_endpoint(
    subsidiary_id: str,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    row = service.get_prices(db, subsidiary_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prices for subsidiary")
    if current.subsidiary_id is not None and current.subsidiary_id != subsidiary_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prices for subsidiary")
    return row


@router.put("/{subsidiary_id}", response_model=PriceOut)
def update_endpoint(
    subsidiary_id: str,
    payload: PriceUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    """Replace rates. Admins edit any filial; scoped admins only their own."""
    if current.subsidiary_id is not None and current.subsidiary_id != subsidiary_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prices for subsidiary")
    row = service.update_prices(db, subsidiary_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No prices for subsidiary")
    return row
