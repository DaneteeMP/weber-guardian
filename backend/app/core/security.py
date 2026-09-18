"""Identity seam: Entra owns who, Guardian DB owns what and where.

Production Entra validation is not wired yet, so without the local dev
mock every caller gets 401. Dev mock (X-Dev-User + DEV_AUTH_ENABLED=true)
resolves the user row by external_id; role/subsidiary always come from
the DB, never from token claims alone.
"""
import uuid
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.modules.users.models import User


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    external_id: str
    role: str
    subsidiary_id: str | None


async def get_current_user(
    x_dev_user: str | None = Header(default=None, alias="X-Dev-User"),
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
