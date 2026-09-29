"""Customer HTTP. Thin: validates, calls service, returns. No SQL here."""
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.customers import service
from app.modules.customers.schemas import CustomerCreate, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
def list_endpoint(
    response: Response,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: str | None = Query(default=None, min_length=1, max_length=128),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    rows = service.list_customers(
        db, limit=limit, offset=offset, subsidiary_id=current.scope_subsidiary_id, search=search
    )
    response.headers["X-Total-Count"] = str(
        service.count_customers(db, subsidiary_id=current.scope_subsidiary_id, search=search)
    )
    return rows


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    payload: CustomerCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    try:
        return service.create_customer(db, payload, scope_subsidiary=current.scope_subsidiary_id)
    except service.CustomerAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Customer already exists: {exc.customer_id}") from exc
    except service.OutsideScope as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
