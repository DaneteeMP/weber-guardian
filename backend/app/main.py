"""FastAPI app. Mounts routers under /api/v1. Free OpenAPI at /docs."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.basic_kit.router import router as basic_kit_router
from app.modules.customers.router import router as customers_router
from app.modules.distances.router import router as distances_router
from app.modules.equipment.router import router as equipment_router
from app.modules.imports.router import router as imports_router
from app.modules.offers.router import router as offers_router
from app.modules.prices.router import router as prices_router
from app.modules.users.router import router as users_router

app = FastAPI(title="WeberGuardian API", version="0.1.0")

# F0 dev only: allow the Vite dev server to call the API from the browser.
# Tightened with auth + explicit origins in F2.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(customers_router, prefix="/api/v1")
app.include_router(equipment_router, prefix="/api/v1")
app.include_router(imports_router, prefix="/api/v1")
app.include_router(offers_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")
app.include_router(prices_router, prefix="/api/v1")
app.include_router(distances_router, prefix="/api/v1")
app.include_router(basic_kit_router, prefix="/api/v1")
