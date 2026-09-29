"""Security seam tests. No network, no Entra, SQLite only."""
import asyncio
import uuid

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core import security
from app.main import app as api_app
from app.modules.subsidiaries.models import Subsidiary
from app.modules.users.models import User


def _user(db, external_id="oid-admin", role="admin", subsidiary_id=None):
    row = User(external_id=external_id, role=role, subsidiary_id=subsidiary_id)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _current(external_id, role="admin", subsidiary_id=None, scope_subsidiary_id=None):
    return security.CurrentUser(
        id=uuid.uuid4(),
        external_id=external_id,
        role=role,
        subsidiary_id=subsidiary_id,
        scope_subsidiary_id=scope_subsidiary_id,
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
    # No scope header: sales keep their own filial as the effective scope.
    assert me.scope_subsidiary_id == "Weber Iberica"


def test_scope_header_resolves_effective_scope(db, monkeypatch):
    monkeypatch.setattr(security.settings, "dev_auth_enabled", True)
    db.add(Subsidiary(name="Weber Iberica", short_label="Iberica"))
    _user(db, external_id="oid-admin", role="admin")
    db.commit()
    me = asyncio.run(
        security.get_current_user(
            x_dev_user="oid-admin", x_scope_subsidiary="Weber%20Iberica", db=db
        )
    )
    # Admin identity stays global; the view scope follows the header.
    assert me.subsidiary_id is None
    assert me.scope_subsidiary_id == "Weber Iberica"


def test_require_role_allows_and_denies():
    checker = security.require_role("admin", "sales")
    assert asyncio.run(checker(current=_current("a", role="sales"))).role == "sales"
    with pytest.raises(HTTPException) as exc:
        asyncio.run(checker(current=_current("b", role="viewer")))
    assert exc.value.status_code == 403


def test_basic_gate_disabled_by_default(monkeypatch):
    """With no credentials configured the gate must not interfere at all."""
    monkeypatch.setattr(security.settings, "basic_auth_user", "")
    monkeypatch.setattr(security.settings, "basic_auth_password", "")
    with TestClient(api_app) as client:
        assert client.get("/openapi.json").status_code == 200


def test_basic_gate_blocks_unauthorised_calls(monkeypatch):
    monkeypatch.setattr(security.settings, "basic_auth_user", "demo")
    monkeypatch.setattr(security.settings, "basic_auth_password", "s3cret")
    with TestClient(api_app) as client:
        # /openapi.json needs no app auth, so a 401 here can only come from the gate.
        anonymous = client.get("/openapi.json")
        assert anonymous.status_code == 401
        assert anonymous.headers["www-authenticate"].startswith("Basic")
        assert client.get("/openapi.json", auth=("demo", "wrong")).status_code == 401
        assert client.get("/openapi.json", auth=("demo", "s3cret")).status_code == 200


def test_basic_gate_leaves_health_and_preflight_open(monkeypatch):
    """Platform health checks and CORS preflights must never need credentials."""
    monkeypatch.setattr(security.settings, "basic_auth_user", "demo")
    monkeypatch.setattr(security.settings, "basic_auth_password", "s3cret")
    with TestClient(api_app) as client:
        assert client.get("/health").status_code == 200
        # localhost:5173 is the default allowed origin baked into the CORS
        # middleware at import time, so this is a valid preflight.
        preflight = client.options(
            "/api/v1/offers",
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
        )
        assert preflight.status_code == 200


def test_cors_origins_parsing(monkeypatch):
    monkeypatch.setattr(security.settings, "allowed_origins", "https://a.vercel.app, https://b.vercel.app ,")
    assert security.settings.cors_origins == ["https://a.vercel.app", "https://b.vercel.app"]


def test_basic_gate_accepts_non_ascii_password(monkeypatch):
    """A non-ASCII password must be rejected cleanly, not raise a 500."""
    monkeypatch.setattr(security.settings, "basic_auth_user", "demo")
    monkeypatch.setattr(security.settings, "basic_auth_password", "contraseña")
    with TestClient(api_app, raise_server_exceptions=False) as client:
        assert client.get("/openapi.json", auth=("demo", "contraseña")).status_code == 200
        assert client.get("/openapi.json", auth=("demo", "contrasena")).status_code == 401
