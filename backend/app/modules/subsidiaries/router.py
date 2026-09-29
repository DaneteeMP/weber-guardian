"""Subsidiary HTTP. Thin catalog + admin assignment: validates, calls service, returns."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.subsidiaries import service
from app.modules.subsidiaries.schemas import (
    AssignCountriesIn,
    AssignCountriesOut,
    AutoAssignOut,
    SubsidiaryOut,
    SubsidiaryStatsOut,
    UnassignedCountryOut,
)

router = APIRouter(prefix="/subsidiaries", tags=["subsidiaries"])


@router.get("", response_model=list[SubsidiaryOut])
def list_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_subsidiaries(db)


@router.get("/stats", response_model=list[SubsidiaryStatsOut])
def stats_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    return service.stats(db)


@router.get("/unassigned-countries", response_model=list[UnassignedCountryOut])
def unassigned_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    return service.unassigned_countries(db)


@router.post("/assign-countries", response_model=AssignCountriesOut)
def assign_endpoint(
    payload: AssignCountriesIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    try:
        return AssignCountriesOut(updated=service.assign_countries(db, payload))
    except service.UnknownSubsidiary as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/auto-assign", response_model=AutoAssignOut)
def auto_assign_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin")),
):
    updated, warnings = service.auto_assign_all(db)
    return AutoAssignOut(updated=updated, warnings=warnings)
