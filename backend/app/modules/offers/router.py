"""Offer HTTP. Thin: validates, calls service, returns. No SQL here."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.modules.offers import service
from app.modules.offers.schemas import (
    OfferCalculateIn,
    OfferCalculateOut,
    OfferCreate,
    OfferOut,
)

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("/calculate", response_model=OfferCalculateOut)
def calculate_endpoint(payload: OfferCalculateIn):
    return service.calculate_price(payload)


@router.get("", response_model=list[OfferOut])
def list_endpoint(
    customer_id: str | None = Query(default=None, min_length=1, max_length=64),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return service.list_offers(db, customer_id=customer_id, limit=limit, offset=offset)


@router.get("/{offer_id}", response_model=OfferOut)
def get_endpoint(offer_id: uuid.UUID, db: Session = Depends(get_db)):
    offer = service.get_offer(db, offer_id)
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    return offer


@router.post("", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(payload: OfferCreate, db: Session = Depends(get_db)):
    try:
        return service.create_offer(db, payload)
    except service.UnknownCustomer as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.OfferAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
