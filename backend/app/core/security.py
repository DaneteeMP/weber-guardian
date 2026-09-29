"""Identity seam: Entra owns who, Guardian DB owns what and where.

Production Entra validation is not wired yet, so without the local dev
mock every caller gets 401. Dev mock (X-Dev-User + DEV_AUTH_ENABLED=true)
resolves the user row by external_id; role/subsidiary always come from
the DB, never from token claims alone.

X-Scope-Subsidiary is the "Filial:" view selector: admins may point it
at any catalog filial (or omit it to see everything), while sales and
viewers are pinned to their own filial. Asking for a different one is
rejected, never silently ignored. The value arrives URL-encoded because
filial names are free text and HTTP headers are not.
"""
import uuid
from dataclasses import dataclass
from urllib.parse import unquote

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.core.subsidiaries import normalize_subsidiary
from app.modules.subsidiaries.models import Subsidiary
from app.modules.users.models import User


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    external_id: str
    role: str
    # Home filial of the identity (who the person is).
    subsidiary_id: str | None
    # Effective data scope (what the person is looking at).
    scope_subsidiary_id: str | None


def _resolve_scope(
    db: Session, role: str, own: str | None, header: str | None
) -> str | None:
    """Effective data scope for the caller.

    Empty header: admins see everything (None), others see their own
    filial. Set header: admins get the requested catalog filial, others
    must request exactly their own filial. Unknown filials are rejected
    instead of silently returning empty lists everywhere.
    """
    # FastAPI injects a real str via DI; direct calls (tests, REPL) see
    # the Header(None) sentinel instead, which counts as "not sent".
    requested = unquote(header).strip() if isinstance(header, str) else ""
    if not requested:
        return None if role == "admin" else own
    wanted = normalize_subsidiary(requested)
    if role != "admin":
        if wanted != own:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Scope limited to subsidiary {own}",
            )
        return own
    if db.get(Subsidiary, wanted) is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Unknown subsidiary in scope header: {wanted}",
        )
    return wanted


async def get_current_user(
    x_dev_user: str | None = Header(default=None, alias="X-Dev-User"),
    x_scope_subsidiary: str | None = Header(default=None, alias="X-Scope-Subsidiary"),
    db: Session = Depends(get_db),
) -> CurrentUser:
    """Resolve the caller. 401 when identity cannot be established."""
    if settings.dev_auth_enabled and x_dev_user:
        user = db.scalar(select(User).where(User.external_id == x_dev_user))
        if user is not None:
            return CurrentUser(
                id=user.id,
                external_id=user.external_id,
                role=user.role,
                subsidiary_id=user.subsidiary_id,
                scope_subsidiary_id=_resolve_scope(
                    db, user.role, user.subsidiary_id, x_scope_subsidiary
                ),
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def require_role(*allowed: str):
    """Dependency factory: 403 unless the current role is allowed."""

    async def checker(current: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current.role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return current

    return checker
