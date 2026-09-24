"""FastAPI app. Mounts routers under /api/v1. Free OpenAPI at /docs."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.basic_kit.router import router as basic_kit_router
from app.modules.customers.router import router as customers_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.distances.router import router as distances_router
from app.modules.equipment.router import router as equipment_router
from app.modules.imports.router import router as imports_router
from app.modules.machine_prices.router import router as machine_prices_router
from app.modules.offers.router import router as offers_router
from app.modules.prices.router import router as prices_router
from app.modules.users.router import router as users_router
from app.weber.pdf import build_offer_pdf

app = FastAPI(title="WeberGuardian API", version="0.1.0")

# Composition root: the only place allowed to wire the Weber adapter into
# the core. Routers read request.app.state.pdf_renderer; modules never
# import app.weber.
app.state.pdf_renderer = build_offer_pdf

# F0 dev only: allow the Vite dev server to call the API from the browser.
# Tightened with auth + explicit origins in F2.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(customers_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(equipment_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")
app.include_router(machine_prices_router, prefix="/api/v1")
app.include_router(offers_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(prices_router, prefix="/api/v1")
app.include_router(distances_router, prefix="/api/v1")
app.include_router(basic_kit_router, prefix="/api/v1")
