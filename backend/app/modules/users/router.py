"""User HTTP. No login here: identity comes from Entra (prod) or dev mock."""
from fastapi import APIRouter, Depends

from app.core.security import CurrentUser, get_current_user
from app.core.subsidiaries import short_label

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def me_endpoint(current: CurrentUser = Depends(get_current_user)) -> dict:
    """Return the caller's Guardian identity (role + scope from the DB)."""
    return {
        "external_id": current.external_id,
        "role": current.role,
        "subsidiary_id": current.subsidiary_id,
        "subsidiary_short": short_label(current.subsidiary_id),
        "scope_subsidiary_id": current.scope_subsidiary_id,
        "scope_subsidiary_short": short_label(current.scope_subsidiary_id),
    }
