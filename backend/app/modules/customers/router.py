"""Customer HTTP. Thin: validates, calls service, returns. No SQL here."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.customers import service
from app.modules.customers.schemas import CustomerCreate, CustomerOut

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
def list_endpoint(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return service.list_customers(db, limit=limit, offset=offset)


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(payload: CustomerCreate, db: Session = Depends(get_db)):
    try:
        return service.create_customer(db, payload)
    except service.CustomerAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Customer already exists: {exc.customer_id}") from exc
