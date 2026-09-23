"""Dashboard HTTP. Thin: resolves scope from identity, returns counts."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.dashboard import service
from app.modules.dashboard.schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardStats)
def stats_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.get_stats(db, subsidiary_id=current.subsidiary_id)
