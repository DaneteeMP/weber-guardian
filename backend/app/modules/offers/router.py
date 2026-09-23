"""Offer HTTP. Thin: validates, calls service, returns. No SQL here."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser, get_current_user, require_role
from app.modules.offers import service
from app.modules.offers.schemas import (
    OfferCalculateIn,
    OfferCalculateOut,
    OfferCreate,
    OfferOut,
    OfferStatusUpdate,
)

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("/calculate", response_model=OfferCalculateOut)
def calculate_endpoint(
    payload: OfferCalculateIn,
    current: CurrentUser = Depends(get_current_user),
):
    return service.calculate_price(payload)


@router.get("", response_model=list[OfferOut])
def list_endpoint(
    customer_id: str | None = Query(default=None, min_length=1, max_length=64),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    return service.list_offers(
        db, customer_id=customer_id, limit=limit, offset=offset, subsidiary_id=current.subsidiary_id
    )


@router.get("/{offer_id}", response_model=OfferOut)
def get_endpoint(
    offer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    offer = service.get_offer(db, offer_id, subsidiary_id=current.subsidiary_id)
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    return offer


@router.post("", response_model=OfferOut, status_code=status.HTTP_201_CREATED)
def create_endpoint(
    payload: OfferCreate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    try:
        return service.create_offer(db, payload, created_by=current.id)
    except service.UnknownCustomer as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except service.OfferAlreadyExists as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc


@router.delete("/{offer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_endpoint(
    offer_id: uuid.UUID,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    if not service.delete_offer(db, offer_id, subsidiary_id=current.subsidiary_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")


@router.patch("/{offer_id}", response_model=OfferOut)
def status_endpoint(
    offer_id: uuid.UUID,
    payload: OfferStatusUpdate,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(require_role("admin", "sales")),
):
    try:
        offer = service.set_offer_status(db, offer_id, payload.status, subsidiary_id=current.subsidiary_id)
    except service.BadStatus as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    if offer is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    return offer


@router.get("/{offer_id}/pdf")
def pdf_endpoint(
    offer_id: uuid.UUID,
    request: Request,
    db: Session = Depends(get_db),
    current: CurrentUser = Depends(get_current_user),
):
    """Official offer PDF, rendered server-side from backend data only."""
    doc = service.get_offer_document(db, offer_id, subsidiary_id=current.subsidiary_id)
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Offer not found")
    try:
        pdf = request.app.state.pdf_renderer(doc)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="Offer_{doc.number}.pdf"'},
    )
