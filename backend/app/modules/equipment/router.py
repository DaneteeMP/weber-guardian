"""Equipment HTTP. Thin read-only list: validates, calls service, returns."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.equipment import service
from app.modules.equipment.schemas import EquipmentOut

router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.get("", response_model=list[EquipmentOut])
def list_endpoint(
    customer_id: str | None = Query(default=None, min_length=1, max_length=64),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_equipment(
        db, customer_id=customer_id, limit=limit, offset=offset, subsidiary_id=current.subsidiary_id
    )
