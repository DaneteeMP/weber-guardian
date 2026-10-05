"""Subsidiary catalog HTTP used by shared filial selectors."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.subsidiaries import service
from app.modules.subsidiaries.schemas import SubsidiaryOut

router = APIRouter(prefix="/subsidiaries", tags=["subsidiaries"])


@router.get("", response_model=list[SubsidiaryOut])
def list_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """List filial names used by the app-wide scope selector."""
    return service.list_subsidiaries(db)
