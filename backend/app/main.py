"""FastAPI app. Mounts routers under /api/v1. Free OpenAPI at /docs."""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.basic_auth import BasicAuthMiddleware
from app.core.config import settings
from app.core.db import engine
from app.modules.basic_kit.router import router as basic_kit_router
from app.modules.component_names.module_workload_router import router as module_workloads_router
from app.modules.component_names.router import router as component_names_router
from app.modules.component_names.workload_router import router as component_workloads_router
from app.modules.customers.router import router as customers_router
from app.modules.distances.router import router as distances_router
from app.modules.equipment_catalog.line_workload_router import router as line_workloads_router
from app.modules.imports.router import router as imports_router
from app.modules.machine_prices.router import router as machine_prices_router
from app.modules.offers.router import router as offers_router
from app.modules.prices.router import router as prices_router
from app.modules.subsidiaries.router import router as subsidiaries_router
from app.modules.users.router import router as users_router

app = FastAPI(title="Guardian Contract Management API", version="0.1.0")

# One startup line so the platform logs show the effective config: a wrong or
# empty ALLOWED_ORIGINS is the usual cause of "CORS: no Access-Control-Allow-Origin".
print(
    f"startup: CORS origins={settings.cors_origins} "
    f"dev_auth={settings.dev_auth_enabled} gate={settings.basic_auth_enabled}",
    flush=True,
)

# Composition root: the only place allowed to wire the Weber adapter into
# the core. Routers read request.app.state.pdf_renderer; modules never
# import app.weber.
#
# Import is deferred to the first PDF request: reportlab and pypdfium2 (plus
# its native library) are heavy, and on the free hosting plan a cold start is
# dominated by import time. Once imported, the module stays in sys.modules so
# later calls are a dict lookup.
def _pdf_renderer(doc):
    from app.weber.pdf import build_offer_pdf

    return build_offer_pdf(doc)


app.state.pdf_renderer = _pdf_renderer

# Demo gate first, CORS last: middleware runs in reverse order of addition, so
# CORS ends up outermost and stamps headers on the 401 this returns too.
app.add_middleware(BasicAuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "Content-Disposition", "WWW-Authenticate"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/warmup")
def warmup():
    """Cheap keep-alive that also touches the database.

    Exposed without the Basic gate (see EXEMPT_PATHS), so an external cron can
    call it every few minutes. It opens a pooled connection and runs SELECT 1,
    which keeps both the free instance and its remote Supabase connection warm,
    so real users skip the cold-start cost. It returns no data.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return {"status": "ok"}


app.include_router(customers_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")
app.include_router(machine_prices_router, prefix="/api/v1")
app.include_router(offers_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(prices_router, prefix="/api/v1")
app.include_router(subsidiaries_router, prefix="/api/v1")
app.include_router(distances_router, prefix="/api/v1")
app.include_router(basic_kit_router, prefix="/api/v1")
app.include_router(component_names_router, prefix="/api/v1")
app.include_router(component_workloads_router, prefix="/api/v1")
app.include_router(module_workloads_router, prefix="/api/v1")
app.include_router(line_workloads_router, prefix="/api/v1")
