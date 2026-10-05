"""Add German state capitals and supplied regional routes.

Revision ID: 0012
Revises: 0011

The distances, nearest hub and travel times are the business-provided
Weber Germany values. Travel times include quarter-hour increments.
"""
from decimal import Decimal
import uuid

from alembic import op
import sqlalchemy as sa


revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


GERMAN_ROUTES = [
    ("Baden-Württemberg", "Stuttgart", "Wolfertschwenden", "161", "1.50"),
    ("Bayern", "München", "Wolfertschwenden", "119", "1.25"),
    ("Berlin", "Berlin", "Werther", "394", "3.75"),
    ("Brandenburg", "Potsdam", "Werther", "364", "3.50"),
    ("Bremen", "Bremen", "Oldenburg", "49", "0.75"),
    ("Hamburg", "Hamburg", "Oldenburg", "168", "1.75"),
    ("Hessen", "Wiesbaden", "Frankfurt", "39", "0.75"),
    ("Mecklenburg-Vorpommern", "Schwerin", "Oldenburg", "264", "2.50"),
    ("Niedersachsen", "Hannover", "Werther", "113", "1.25"),
    ("Nordrhein-Westfalen", "Düsseldorf", "Werther", "177", "1.75"),
    ("Rheinland-Pfalz", "Mainz", "Frankfurt", "41", "0.75"),
    ("Saarland", "Saarbrücken", "Frankfurt", "184", "2.00"),
    ("Sachsen", "Dresden", "Frankfurt", "463", "4.75"),
    ("Sachsen-Anhalt", "Magdeburg", "Werther", "259", "2.50"),
    ("Schleswig-Holstein", "Kiel", "Oldenburg", "252", "2.25"),
    ("Thüringen", "Erfurt", "Frankfurt", "260", "2.75"),
]


def upgrade() -> None:
    op.add_column("distances", sa.Column("capital", sa.String(128), nullable=True))
    op.alter_column(
        "distances",
        "trip_hours",
        existing_type=sa.Numeric(10, 1),
        type_=sa.Numeric(10, 2),
        existing_nullable=False,
    )

    distance_table = sa.table(
        "distances",
        sa.column("id", sa.Uuid()),
        sa.column("subsidiary_id", sa.String(64)),
        sa.column("province", sa.String(128)),
        sa.column("capital", sa.String(128)),
        sa.column("service_center", sa.String(64)),
        sa.column("km", sa.Numeric(10, 1)),
        sa.column("trip_hours", sa.Numeric(10, 2)),
    )
    op.bulk_insert(
        distance_table,
        [
            {
                "id": uuid.uuid4(),
                "subsidiary_id": "Weber Germany",
                "province": province,
                "capital": capital,
                "service_center": service_center,
                "km": Decimal(km),
                "trip_hours": Decimal(hours),
            }
            for province, capital, service_center, km, hours in GERMAN_ROUTES
        ],
    )


def downgrade() -> None:
    bind = op.get_bind()
    german_rows = bind.execute(
        sa.text("SELECT count(*) FROM distances WHERE subsidiary_id = 'Weber Germany'")
    ).scalar_one()
    if german_rows:
        raise RuntimeError(
            "Cannot downgrade 0012 while German route rows exist; "
            "the previous schema cannot retain their capitals, centers, or quarter-hour values."
        )
    op.alter_column(
        "distances",
        "trip_hours",
        existing_type=sa.Numeric(10, 2),
        type_=sa.Numeric(10, 1),
        existing_nullable=False,
    )
    op.drop_column("distances", "capital")
