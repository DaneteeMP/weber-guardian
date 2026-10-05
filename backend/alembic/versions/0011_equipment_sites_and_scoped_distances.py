"""Physical equipment sites and subsidiary-scoped distances.

Revision ID: 0011
Revises: 0010

Physical addresses belong to equipment sites, not only to the SAP customer:
one customer may have machines at more than one address. Existing distance
rows were the Iberica catalogue, so they are retained under Weber Iberica.
"""
from alembic import op
import sqlalchemy as sa


revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "customer_sites",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "customer_id",
            sa.String(64),
            sa.ForeignKey("customers.customer_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("site_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("physical_street", sa.String(255), nullable=True),
        sa.Column("physical_city", sa.String(128), nullable=True),
        sa.Column("physical_postal_code", sa.String(24), nullable=True),
        sa.Column("physical_province", sa.String(128), nullable=True),
        sa.Column("physical_country", sa.String(64), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_customer_sites_customer_id", "customer_sites", ["customer_id"])

    op.add_column("equipment", sa.Column("site_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_equipment_site_id_customer_sites",
        "equipment",
        "customer_sites",
        ["site_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_equipment_site_id", "equipment", ["site_id"])

    op.drop_constraint("distances_province_key", "distances", type_="unique")
    op.add_column("distances", sa.Column("subsidiary_id", sa.String(64), nullable=True))
    op.add_column("distances", sa.Column("service_center", sa.String(64), nullable=True))
    op.execute("UPDATE distances SET subsidiary_id = 'Weber Iberica'")
    op.alter_column("distances", "subsidiary_id", nullable=False)
    op.create_foreign_key(
        "fk_distances_subsidiary_id_subsidiaries",
        "distances",
        "subsidiaries",
        ["subsidiary_id"],
        ["name"],
    )
    op.create_index("ix_distances_subsidiary_id", "distances", ["subsidiary_id"])
    op.create_unique_constraint(
        "uq_distances_subsidiary_province", "distances", ["subsidiary_id", "province"]
    )


def downgrade() -> None:
    bind = op.get_bind()
    site_count = bind.execute(sa.text("SELECT count(*) FROM customer_sites")).scalar_one()
    non_iberica_rows = bind.execute(
        sa.text("SELECT count(*) FROM distances WHERE subsidiary_id <> 'Weber Iberica'")
    ).scalar_one()
    if site_count:
        raise RuntimeError(
            "Cannot downgrade 0011 while physical customer sites exist; "
            "the previous schema has nowhere to preserve these addresses."
        )
    if non_iberica_rows:
        raise RuntimeError(
            "Cannot downgrade 0011 while non-Iberica distance rows exist; "
            "the previous schema allowed only one row per province."
        )

    op.drop_constraint("uq_distances_subsidiary_province", "distances", type_="unique")
    op.drop_index("ix_distances_subsidiary_id", table_name="distances")
    op.drop_constraint("fk_distances_subsidiary_id_subsidiaries", "distances", type_="foreignkey")
    op.drop_column("distances", "service_center")
    op.drop_column("distances", "subsidiary_id")
    op.create_unique_constraint("distances_province_key", "distances", ["province"])

    op.drop_index("ix_equipment_site_id", table_name="equipment")
    op.drop_constraint("fk_equipment_site_id_customer_sites", "equipment", type_="foreignkey")
    op.drop_column("equipment", "site_id")
    op.drop_index("ix_customer_sites_customer_id", table_name="customer_sites")
    op.drop_table("customer_sites")
