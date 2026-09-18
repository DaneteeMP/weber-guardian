# WeberGuardian

Python rebuild of WeberAssistant. After-sales management for machinery (offers, technicians, contracts).

## Project order

- F0: minimal `customers` vertical (this scaffold)
- F1: real business `offers + pricing_engine`
- F2: security + multi-country
- F3: CSV / external data
- F4: contracts + technicians
- F5: sellable product

See `docs/` for ADRs and the walkthrough.

## Requirements

- Docker + Docker Compose (source of truth)
- Python 3.12 inside Docker (`backend/Dockerfile`). Host Python may differ; do not adapt pins to the host.
- Node 20+ (frontend, F0 UI still pending)

## Quick start

```powershell
# 1. DB
docker compose up db -d

# 2. Backend env file (first time only)
Copy-Item backend\.env.example -Destination backend\.env

# 3. Build API (Python 3.12) and run migrations + tests
docker compose build api
docker compose run --rm api alembic upgrade head
docker compose run --rm api pytest -q
docker compose run --rm api ruff check .

# 4. Run API
docker compose up api
```

Local (without Docker, Python 3.12 only):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs
