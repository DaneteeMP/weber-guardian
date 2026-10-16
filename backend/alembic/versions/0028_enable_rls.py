"""enable Row Level Security on every public table

Revision ID: 0028
Revises: 0027

Supabase lints every public table without RLS as a security error: without
it, the PostgREST API could serve our rows to anyone holding an anon key.
We do not use PostgREST at all (the API talks straight to Postgres and
enforces auth + subsidiary scope itself), so no permissive policy is added:
RLS on with zero policies denies everything through the REST API.

This changes nothing for the app: migrations and the API connect as the
postgres superuser, which bypasses RLS entirely, as does the service_role.
It WOULD break a future restricted (non-bypass) database role: that role
would need explicit policies.

Convention going forward: every migration that creates a table enables RLS
on it (see the loop below covering the tables existing today, including the
legacy component_workloads / module_workloads ones with no models left).
"""
import sqlalchemy as sa
from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None

_RLS_LOOP = """
DO $$
DECLARE
    tbl text;
BEGIN
    FOR tbl IN
        SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        -- Single % here: SQLAlchemy text() passes them through untouched to
        -- Postgres on this stack (psycopg3); the doubled %% seen in --sql
        -- renders is a display artifact, not what executes.
        EXECUTE format('ALTER TABLE public.%I {action} ROW LEVEL SECURITY', tbl);
        RAISE NOTICE '0028: % ROW LEVEL SECURITY on %', '{action}', tbl;
    END LOOP;
END
$$;
"""


def upgrade() -> None:
    op.execute(sa.text(_RLS_LOOP.format(action="ENABLE")))


def downgrade() -> None:
    op.execute(sa.text(_RLS_LOOP.format(action="DISABLE")))
