"""Basic-kit HTTP. Thin read-only lookup: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.basic_kit import service
from app.modules.basic_kit.schemas import BasicKitOut

router = APIRouter(prefix="/basic-kit", tags=["basic_kit"])


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
