"""subsidiary supervision catalog + canonical full names

Revision ID: 0009
Revises: 0008

- subsidiaries: canonical Weber names + short display labels.
- subsidiary_countries: supervision mapping (country -> subsidiary),
  seeded from the business list. Spellings kept as received; matching
  normalizes at lookup time (see app.core.subsidiaries).
- Existing short codes retagged to full names (ES->Weber Iberica,
  DE->Weber Germany). ZM was local test data -> NULL (unknown).
"""
from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

SUBSIDIARIES = [
    ("Weber Benelux", "Benelux"),
    ("Weber Brazil", "Brazil"),
    ("Weber Colombia", "Colombia"),
    ("Weber Croatia", "Croatia"),
    ("Weber Czech", "Czech"),
    ("Weber Denmark", "Denmark"),
    ("Weber Finland", "Finland"),
    ("Weber France", "France"),
    ("Weber Germany", "Germany"),
    ("Weber Iberica", "Iberica"),
    ("Weber Inc", "Inc"),
    ("Weber Italy", "Italy"),
    ("Weber Latam", "Latam"),
    ("Weber Latina", "Latina"),
    ("Weber Norway", "Norway"),
    ("Weber Poland", "Poland"),
    ("Weber Romania", "Romania"),
    ("Weber Russia", "Russia"),
    ("Weber Singapore", "Singapore"),
    ("Weber Sweden", "Sweden"),
    ("Weber Switzerland", "Switzerland"),
    ("Weber Partners", "Partners"),
]

# (country as received, subsidiary)
SUPERVISION = [
    ("Belgium", "Weber Benelux"), ("Luxembourg", "Weber Benelux"), ("Netherlands", "Weber Benelux"),
    ("Brazil", "Weber Brazil"),
    ("Colombia", "Weber Colombia"),
    ("Albania", "Weber Croatia"), ("Bosnia-Herz.", "Weber Croatia"), ("Croatia", "Weber Croatia"),
    ("Kosovo", "Weber Croatia"), ("Macedonia", "Weber Croatia"), ("Montenegro", "Weber Croatia"),
    ("Serbia", "Weber Croatia"), ("Slovenia", "Weber Croatia"),
    ("Czech Republic", "Weber Czech"), ("Slovakia", "Weber Czech"),
    ("Denmark", "Weber Denmark"),
    ("Finland", "Weber Finland"),
    ("France", "Weber France"),
    ("Germany", "Weber Germany"),
    ("Portugal", "Weber Iberica"), ("Spain", "Weber Iberica"),
    ("Canada", "Weber Inc"), ("USA", "Weber Inc"),
    ("Italy", "Weber Italy"), ("Malta", "Weber Italy"),
    ("Bolivia", "Weber Latam"), ("Chile", "Weber Latam"), ("Paraguay", "Weber Latam"),
    ("Peru", "Weber Latam"), ("Uruguay", "Weber Latam"),
    ("Barbados", "Weber Latina"), ("Costa Rica", "Weber Latina"), ("Dominican Rep.", "Weber Latina"),
    ("El Salvador", "Weber Latina"), ("Guatemala", "Weber Latina"), ("Honduras", "Weber Latina"),
    ("Jamaica", "Weber Latina"), ("Mexico", "Weber Latina"), ("Nicaragua", "Weber Latina"),
    ("Panama", "Weber Latina"), ("Puerto Rico", "Weber Latina"), ("Trinidad,Tobago", "Weber Latina"),
    ("Norway", "Weber Norway"),
    ("Poland", "Weber Poland"),
    ("Moldova", "Weber Romania"), ("Romania", "Weber Romania"),
    ("Russian Fed.", "Weber Russia"),
    ("Singapore", "Weber Singapore"),
    ("Sweden", "Weber Sweden"),
    ("Switzerland", "Weber Switzerland"),
    ("Argentina", "Weber Partners"), ("Australia", "Weber Partners"), ("Austria", "Weber Partners"),
    ("Belarus", "Weber Partners"), ("Bulgaria", "Weber Partners"), ("China", "Weber Partners"),
    ("Cyprus", "Weber Partners"), ("Ecuador", "Weber Partners"), ("Egypt", "Weber Partners"),
    ("Estonia", "Weber Partners"), ("Greece", "Weber Partners"), ("Hong Kong", "Weber Partners"),
    ("Hungary", "Weber Partners"), ("Iceland", "Weber Partners"), ("Ireland", "Weber Partners"),
    ("Israel", "Weber Partners"), ("Japan", "Weber Partners"), ("Kenya", "Weber Partners"),
    ("Latvia", "Weber Partners"), ("Liechtenstein", "Weber Partners"), ("Lithuania", "Weber Partners"),
    ("Malaysia", "Weber Partners"), ("Morocco", "Weber Partners"), ("New Zealand", "Weber Partners"),
    ("Oman", "Weber Partners"), ("Palestine", "Weber Partners"), ("Philippines", "Weber Partners"),
    ("Taiwan", "Weber Partners"), ("Thailand", "Weber Partners"), ("Turkey", "Weber Partners"),
    ("Ukraine", "Weber Partners"), ("United Kingdom", "Weber Partners"), ("Utd.Arab Emir.", "Weber Partners"),
    ("Uzbekistan", "Weber Partners"), ("Venezuela", "Weber Partners"), ("Vietnam", "Weber Partners"),
    ("South Africa", "Weber Partners"), ("South Korea", "Weber Partners"),
]


def upgrade() -> None:
    op.create_table(
        "subsidiaries",
        sa.Column("name", sa.String(64), primary_key=True),
        sa.Column("short_label", sa.String(32), nullable=False),
    )
    op.create_table(
        "subsidiary_countries",
        sa.Column("country", sa.String(128), primary_key=True),
        sa.Column("subsidiary", sa.String(64), sa.ForeignKey("subsidiaries.name"), nullable=False),
    )
    for name, short in SUBSIDIARIES:
        op.execute(sa.text("INSERT INTO subsidiaries (name, short_label) VALUES (:n, :s)").bindparams(n=name, s=short))
    for country, subsidiary in SUPERVISION:
        op.execute(
            sa.text("INSERT INTO subsidiary_countries (country, subsidiary) VALUES (:c, :s)").bindparams(c=country, s=subsidiary)
        )
    op.execute(sa.text("UPDATE customers SET subsidiary_id='Weber Iberica' WHERE subsidiary_id='ES'"))
    op.execute(sa.text("UPDATE customers SET subsidiary_id='Weber Germany' WHERE subsidiary_id='DE'"))
    op.execute(sa.text("UPDATE customers SET subsidiary_id=NULL WHERE subsidiary_id='ZM'"))
    op.execute(sa.text("UPDATE users SET subsidiary_id='Weber Iberica' WHERE subsidiary_id='ES'"))
    op.execute(sa.text("UPDATE users SET subsidiary_id='Weber Germany' WHERE subsidiary_id='DE'"))
    op.execute(sa.text("UPDATE prices SET subsidiary_id='Weber Iberica' WHERE subsidiary_id='ES'"))
    op.execute(sa.text("UPDATE prices SET subsidiary_id='Weber Germany' WHERE subsidiary_id='DE'"))


def downgrade() -> None:
    op.execute(sa.text("UPDATE prices SET subsidiary_id='DE' WHERE subsidiary_id='Weber Germany'"))
    op.execute(sa.text("UPDATE prices SET subsidiary_id='ES' WHERE subsidiary_id='Weber Iberica'"))
    op.execute(sa.text("UPDATE users SET subsidiary_id='DE' WHERE subsidiary_id='Weber Germany'"))
    op.execute(sa.text("UPDATE users SET subsidiary_id='ES' WHERE subsidiary_id='Weber Iberica'"))
    op.execute(sa.text("UPDATE customers SET subsidiary_id='DE' WHERE subsidiary_id='Weber Germany'"))
    op.execute(sa.text("UPDATE customers SET subsidiary_id='ES' WHERE subsidiary_id='Weber Iberica'"))
    op.drop_table("subsidiary_countries")
    op.drop_table("subsidiaries")
