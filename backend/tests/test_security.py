"""Security seam tests. No network, no Entra, SQLite only."""
import asyncio
import uuid

import pytest
from fastapi import HTTPException

from app.core import security
from app.modules.users.models import User


def _user(db, external_id="oid-admin", role="admin", subsidiary_id=None):
    row = User(external_id=external_id, role=role, subsidiary_id=subsidiary_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _current(external_id, role="admin", subsidiary_id=None):
    return security.CurrentUser(
        id=uuid.uuid4(), external_id=external_id, role=role, subsidiary_id=subsidiary_id
    )


def test_dev_disabled_ignores_header(db, monkeypatch):
    monkeypatch.setattr(security.settings, "dev_auth_enabled", False)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(security.get_current_user(x_dev_user="oid-admin", db=db))
    assert exc.value.status_code == 401


def test_unknown_external_id_is_401(db, monkeypatch):
    monkeypatch.setattr(security.settings, "dev_auth_enabled", True)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(security.get_current_user(x_dev_user="oid-ghost", db=db))
    assert exc.value.status_code == 401


def test_known_user_resolves_role_and_scope_from_db(db, monkeypatch):
    monkeypatch.setattr(security.settings, "dev_auth_enabled", True)
    _user(db, external_id="oid-sales-es", role="sales", subsidiary_id="Weber Iberica")
    me = asyncio.run(security.get_current_user(x_dev_user="oid-sales-es", db=db))
    assert me.role == "sales"
    assert me.subsidiary_id == "Weber Iberica"


def test_require_role_allows_and_denies():
    checker = security.require_role("admin", "sales")
    assert asyncio.run(checker(current=_current("a", role="sales"))).role == "sales"
    with pytest.raises(HTTPException) as exc:
        asyncio.run(checker(current=_current("b", role="viewer")))
    assert exc.value.status_code == 403
