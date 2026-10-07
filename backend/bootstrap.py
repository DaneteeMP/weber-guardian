"""One-shot bootstrap for an EMPTY deployment: migrate, then create the users.

Same idea as bootstrap_demo.py, but it deliberately does NOT seed demo
customers or offers: the instance stays clean so the operator imports their
own data. It exists because the demo database (Supabase) starts empty and the
local network may not reach it, while the Render web service can. Render's
"Docker Command" field takes a single executable with no shell operators, so
the two steps cannot be chained inline; this script is that one command.

It only prepares the schema and the dev identities. It never starts the
server: Render shows the container as exited when it finishes, which is
expected. Set the Docker Command to this once, then clear it so the normal
CMD boots uvicorn.

Every step is safe to repeat: `alembic upgrade head` applies only what is
missing, and seed_dev.py skips rows that already exist.

Usage:
    python bootstrap.py
"""
import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent


def run(label: str, command: list[str], extra_env: dict[str, str] | None = None) -> None:
    print(f"--- {label} ---", flush=True)
    result = subprocess.run(command, cwd=BACKEND_DIR, env={**os.environ, **(extra_env or {})})
    if result.returncode != 0:
        # Stop here: seeding on top of a half-migrated schema would only hide
        # the real error behind a confusing one later.
        print(f"{label} failed with exit code {result.returncode}", flush=True)
        sys.exit(result.returncode)


def main() -> int:
    run("alembic upgrade head", [sys.executable, "-m", "alembic", "upgrade", "head"])
    # seed_dev refuses to run without the dev flag; the deployment must not
    # depend on whether the platform happens to set that variable.
    run("seed_dev", [sys.executable, "seed_dev.py"], {"DEV_AUTH_ENABLED": "true"})
    print("bootstrap finished (no demo customers/offers)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
