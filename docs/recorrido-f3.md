# Recorrido F3 — datos reales: CSV + catálogos (Guardian)

## 1. Importación (`app/modules/imports/`)

- `POST /imports/upload?dry_run=true&subsidiary_id=` (`admin|sales`, multipart → `python-multipart`, única dependencia nueva justificada: sin alternativa stdlib).
- `service.run_import()`: tope 20 MB (los exports SAP reales rondan 7 MB); decode `utf-8-sig→cp1252` (mojibake tipo `B�seler`); parseo `;` + `"`; cabecera exigida (`SAP Debitor ID`, `Account Name`, `Material No.`); `""`→`NULL` (nunca se guarda vacío); validación fila a fila con nº de línea (SAP/nombre/material obligatorios, nombres consistentes por SAP, materiales únicos en fichero).
- 1 cliente por `SAP Debitor ID` aunque venga en N filas; equipos colgados por `material_no UNIQUE`. Corrida **atómica**: 1 error → `422` con el informe y cero escrituras. Segunda subida = todo `skipped`.
- `schemas.py`: el informe es el producto (`ImportReport` + `RowError{line}`; `1` = fichero/cabecera, `≥2` = filas).

## 2. Catálogos (tablas + lectura, migración `0005`)

- `equipment` (migración `0004`): una fila por máquina (`equipment_name, machine_type, component_type, material_no UNIQUE, customer_id FK CASCADE`); nace del import; `GET /equipment?customer_id=` con auth y scope.
- `prices`: una fila por filial (`km/tech/dietas/hotel`, `Numeric`); `GET /prices/{subsidiary}` (fuera de tu filial → `404`, sin fugar). Semilla con los valores que la UI tecleaba a mano.
- `distances`: `province → km, trip_hours`; desconocida = `404` y la oferta usa km 0 (sin adivinar en silencio).
- `basic_kit`: `model → horas + repuestos`.
- Admin CRUD de catálogos queda para F4; hoy se siembran (`seed_dev.py`, idempotente).

## 3. `salesforce/SyncPort` (vacío)

Interfaz `push_offer/pull_customers` con `NotImplementedError`. Reserva la costura para F4+; importar este módulo nunca toca red.

## 4. Frontend

- `OfferBuilder`: precarga rates del catálogo según tu filial (`/me → /prices/{sub}`); el cálculo autoritativo sigue en `/calculate`.
- `ImportData`: selector de fichero + filial + Simular/Importar; renderiza el informe (creados/omitidos/errores con línea). El `422` trae el informe dentro del `detail` y se parsea en pantalla.
- `i18n.ts`: clave `nav_import` en los 5 idiomas.

## 5. Tests y verificación

- `test_imports.py` (formas reales del SAP: `dry_run` no escribe, corrida idempotente, 1 error aborta todo, `cp1252`, cabecera mala), `test_catalogs.py` (lecturas + `None` en desconocidos).
- Total: **32 passed**, `ruff` limpio, migraciones hasta `0005` en Postgres.
- E2E Zambeef real: `dry_run` → crear (cliente ZM + 2 equipos) → re-subida `skipped` → `GET /equipment` + `psql`.

## Herencia

- `import_data.rs` frágil del Rust: sustituido (encoding, `""`, duplicados, informe con líneas). No reproducido.
