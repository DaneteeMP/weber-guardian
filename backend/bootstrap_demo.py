"""One-shot bootstrap for the demo database: migrate, then seed.

Why it exists: the demo database on Supabase starts empty, and it must be
migrated and seeded from a machine that can actually reach it. The Render web
service can (the local development network cannot), and its "Docker Command"
field takes a single executable with no shell operators, so the three steps
cannot be chained inline. This script is that one command.

It only prepares data; it never starts the server. Render will show the
container as exited when it finishes, which is expected: set the Docker
Command to this once, then clear it so the normal CMD boots uvicorn.

Every step is safe to repeat. `alembic upgrade head` applies only what is
missing, and both seeds skip rows that already exist.
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


def offers_already_seeded() -> bool:
    """Whether the demo offers are in place.

    Asked before running seed_demo because that script refuses to run on a
    non-empty offers table. Its exit code 1 would otherwise be reported as a
    bootstrap failure on a perfectly healthy second run.
    """
    import sqlalchemy as sa

    from app.core.config import settings

    with sa.create_engine(settings.database_url).connect() as conn:
        return bool(conn.execute(sa.text("select count(*) from offers")).scalar())


def main() -> int:
    run("alembic upgrade head", [sys.executable, "-m", "alembic", "upgrade", "head"])
    # seed_dev refuses to run without the dev flag, and the demo service must
    # not depend on whether that variable happens to be set in the environment.
    run("seed_dev", [sys.executable, "seed_dev.py"], {"DEV_AUTH_ENABLED": "true"})
    if offers_already_seeded():
        print("--- seed_demo --- skipped: offers already present", flush=True)
    else:
        run("seed_demo", [sys.executable, "seed_demo.py"])
    print("bootstrap finished", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
