"""Optional HTTP Basic gate for the public demo deployment.

Local dev and the test suite leave BASIC_AUTH_USER/BASIC_AUTH_PASSWORD unset,
so this middleware is a no-op there. When both are set, every request must
carry matching Basic credentials, which keeps the API from being readable by
anyone who finds the Render URL in the browser bundle.

This is a demo gate in front of the real identity seam (app/core/security.py),
not a replacement for it: it decides "may you reach the app at all", not
"which subsidiary are you".
"""
import base64
import secrets

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

# Health probes come from the platform and carry no credentials.
EXEMPT_PATHS = {"/health"}


class BasicAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # CORS preflights never carry credentials; blocking them would make
        # every cross-origin call from the browser fail before it is sent.
        if (
            not settings.basic_auth_enabled
            or request.method == "OPTIONS"
            or request.url.path in EXEMPT_PATHS
        ):
            return await call_next(request)
        if not self._credentials_ok(request.headers.get("authorization")):
            return Response(
                "Authentication required",
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="WeberGuardian demo"'},
            )
        return await call_next(request)

    @staticmethod
    def _credentials_ok(header: str | None) -> bool:
        if not header or not header.lower().startswith("basic "):
            return False
        try:
            decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
        except (ValueError, UnicodeDecodeError):
            return False
        user, _, password = decoded.partition(":")
        # compare_digest keeps the check constant-time on both fields. It
        # works on bytes, which also avoids a TypeError when the configured
        # password is not ASCII (the frontend restricts itself to ASCII because
        # of btoa, but the API must not blow up on it).
        return secrets.compare_digest(
            user.encode("utf-8"), settings.basic_auth_user.encode("utf-8")
        ) and secrets.compare_digest(
            password.encode("utf-8"), settings.basic_auth_password.encode("utf-8")
        )
