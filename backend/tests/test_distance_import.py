"""Italian distance CSV tests: preview, units, validation and atomic upsert."""
from datetime import date
from decimal import Decimal

from app.modules.distances.models import Distance
from app.modules.distances.service import import_route_csv
from app.modules.subsidiaries.models import Subsidiary


HEADER = (
    "Provincia / área equivalente;Sigla;Región;Ciudad de referencia;Km carretera;"
    "Conducción (h:mm);Total viaje (h:mm);Itinerario\n"
)
PREAMBLE = (
    "Italia: distancias desde Egna / Neumarkt;;;;;;;\n"
    "Origen: 39044 Egna / Neumarkt (Bolzano). Trayectos de ida hasta la ciudad indicada.;;;;;;;\n"
    "Tiempo al cuarto de hora más cercano. Sin tráfico en tiempo real, paradas ni esperas de embarque.;;;;;;;\n"
    "Los km excluyen el tramo marítimo. El tiempo total incluye ferry en Sicilia y Cerdeña. Fecha: 01/10/2026.;;;;;;;\n"
)
AGRIGENTO = "Agrigento;AG;Sicilia;Agrigento;1.545;16:30;17:00;Vía Villa San Giovanni–Messina\n"


def _seed_italy(db):
    db.add(Subsidiary(name="Weber Italy", short_label="Italy"))
    db.commit()


def test_italian_route_csv_preview_preserves_distinct_travel_times(db):
    _seed_italy(db)

    report = import_route_csv(
        db,
        (PREAMBLE + HEADER + AGRIGENTO).encode("utf-8"),
        subsidiary_id="Weber Italy",
        origin_city="39044 Egna / Neumarkt (Bolzano)",
        route_data_date=date(2026, 10, 1),
        dry_run=True,
    )

    assert report.dry_run is True
    assert report.total_rows == 1 and report.created == 1 and report.updated == 0
    assert db.query(Distance).count() == 0


def test_italian_route_csv_import_stores_road_km_and_total_one_way_time(db):
    _seed_italy(db)

    report = import_route_csv(
        db,
        (PREAMBLE + HEADER + AGRIGENTO).encode("utf-8"),
        subsidiary_id="Weber Italy",
        origin_city="39044 Egna / Neumarkt (Bolzano)",
        route_data_date=date(2026, 10, 1),
        dry_run=False,
    )
    route = db.query(Distance).one()

    assert report.created == 1 and report.updated == 0
    assert route.province == "Agrigento"
    assert route.province_code == "AG" and route.region == "Sicilia"
    assert route.reference_city == "Agrigento"
    assert route.origin_city == "39044 Egna / Neumarkt (Bolzano)"
    assert route.km == Decimal("1545")
    assert route.driving_hours == Decimal("16.50")
    assert route.trip_hours == Decimal("17.00")
    assert route.route_data_date == date(2026, 10, 1)
    assert route.itinerary == "Vía Villa San Giovanni–Messina"


def test_italian_route_csv_update_is_idempotent(db):
    _seed_italy(db)
    file_content = (PREAMBLE + HEADER + AGRIGENTO).encode("utf-8")
    args = {
        "subsidiary_id": "Weber Italy",
        "origin_city": "39044 Egna / Neumarkt (Bolzano)",
        "route_data_date": date(2026, 10, 1),
        "dry_run": False,
    }

    first = import_route_csv(db, file_content, **args)
    route_id = db.query(Distance).one().id
    second = import_route_csv(db, file_content, **args)

    assert first.created == 1
    assert second.created == 0 and second.updated == 1
    assert db.query(Distance).count() == 1
    assert db.query(Distance).one().id == route_id


def test_invalid_row_aborts_the_whole_route_file(db):
    _seed_italy(db)
    valid_row = AGRIGENTO
    invalid_row = "Alessandria;AL;Piemonte;Alessandria;337;3:47;3:45;Carretera\n"

    report = import_route_csv(
        db,
        (PREAMBLE + HEADER + valid_row + invalid_row).encode("utf-8"),
        subsidiary_id="Weber Italy",
        origin_city="39044 Egna / Neumarkt (Bolzano)",
        route_data_date=date(2026, 10, 1),
        dry_run=False,
    )

    assert report.created == 0 and report.updated == 0
    assert report.errors[0].line == 7
    assert "15-minute increments" in report.errors[0].reason
    assert db.query(Distance).count() == 0
