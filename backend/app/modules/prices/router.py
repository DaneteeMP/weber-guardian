"""Price HTTP. Thin read-only lookup: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.prices import service
from app.modules.prices.schemas import PriceOut

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
