"""Distance HTTP. Thin read-only lookup: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.distances import service
from app.modules.distances.schemas import DistanceOut

router = APIRouter(prefix="/distances", tags=["distances"])


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
