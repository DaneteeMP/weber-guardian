"""User HTTP. No login here: identity comes from Entra (prod) or dev mock."""
from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me_endpoint(current: CurrentUser = Depends(get_current_user)) -> dict:
    """Return the caller's Guardian identity (role + scope from the DB)."""
    return {
        "external_id": current.external_id,
        "role": current.role,
        "subsidiary_id": current.subsidiary_id,
    }
