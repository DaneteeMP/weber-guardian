"""FastAPI app. Mounts routers under /api/v1. Free OpenAPI at /docs."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.customers.router import router as customers_router
from app.modules.offers.router import router as offers_router

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
app.include_router(offers_router, prefix="/api/v1")
