"""Subsidiary catalog HTTP used by shared filial selectors.

GET /subsidiaries                    filial names (TopBar scope selector, import UI)
GET  /subsidiaries/countries         supervision mapping (country -> subsidiary)
GET  /subsidiaries/stats             per-subsidiary counters (admin tab)
GET  /subsidiaries/unassigned-countries  customer countries outside the map
POST/PATCH/DELETE                    mapping writes, global admins only
"""
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user
from app.modules.subsidiaries import service
from app.modules.subsidiaries.schemas import (
    SubsidiaryCountryIn,
    SubsidiaryCountryOut,
    SubsidiaryOut,
    SubsidiaryStatsOut,
    UnassignedCountryOut,
)

router = APIRouter(prefix="/subsidiaries", tags=["subsidiaries"])


def require_global_admin(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """403 unless the caller is an admin with the 'All subsidiaries' scope.

    A subsidiary-scoped admin manages their own filial data; the country
    supervision mapping is cross-filial and belongs to the global admin only.
    """
    if current.role != "admin" or current.scope_subsidiary_id is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only an admin with the 'All subsidiaries' scope can manage countries",
        )
    return current


@router.get("", response_model=list[SubsidiaryOut])
def list_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """List filial names used by the app-wide scope selector."""
    return service.list_subsidiaries(db)


@router.get("/countries", response_model=list[SubsidiaryCountryOut])
def list_countries_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """Full supervision mapping. Any identity may read: the import uses it
    server-side and the names leak nothing sensitive."""
    return service.list_countries(db)


@router.get("/stats", response_model=list[SubsidiaryStatsOut])
def stats_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_global_admin),
):
    """Country and customer counters per subsidiary (admin tab only)."""
    return service.stats(db)


@router.get("/unassigned-countries", response_model=list[UnassignedCountryOut])
def unassigned_countries_endpoint(
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_global_admin),
):
    """Customer countries the supervision map does not cover, by volume."""
    return service.unassigned_countries(db)


@router.post(
    "/countries",
    response_model=SubsidiaryCountryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_country_endpoint(
    payload: SubsidiaryCountryIn,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_global_admin),
):
    try:
        return service.add_country(db, payload.country, payload.subsidiary)
    except service.CountryAlreadyMapped as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc
    except service.SubsidiaryNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/countries/{country}", response_model=SubsidiaryCountryOut)
def move_country_endpoint(
    payload: SubsidiaryCountryIn,
    country: str = Path(min_length=1, max_length=128),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_global_admin),
):
    """Reassign a mapped country to another subsidiary. The path country wins
    over the body one; the body only carries the new subsidiary."""
    try:
        return service.move_country(db, country, payload.subsidiary)
    except service.CountryNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.SubsidiaryNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/countries/{country}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country_endpoint(
    country: str = Path(min_length=1, max_length=128),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_global_admin),
):
    try:
        service.delete_country(db, country)
    except service.CountryNotFound as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
