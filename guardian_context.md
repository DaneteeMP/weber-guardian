# Contexto del proyecto para IA

Documento de traspaso. Leer antes de tocar código. Las reglas obligatorias de
construcción están en `AGENTS.md`; este fichero explica **qué es el sistema, qué
está hecho y qué está a medias**.

## 1. Qué es

WeberGuardian es un rebuild en Python de `WeberAssistant`: gestión postventa de
maquinaria (clientes, equipos, ofertas, tarifas, rutas, técnicos, contratos).

Objetivo de negocio: empezar por **una filial** (actualmente `Weber Italy`) y
hacerlo vendible multi-país y multi-sector.

WeberAssistant (Rust) es **referencia funcional** (requisitos, comportamiento,
datos), nunca una fuente de código a portar línea a línea.

## 2. Stack y layout

- Backend: `FastAPI` + `SQLAlchemy sync` + `Postgres` + `Alembic`, Python 3.12
  fijado en `backend/Dockerfile`.
- Frontend: `React` + `TS` + `Tailwind` + `TanStack Table` + `i18n`
  (es/en/de/fr/it).
- Auth: `BasicAuthMiddleware` como gate demo + roles `sales/admin` con scope
  por filial en `app/core/security.py`.
- Infra: `docker-compose.yml` con `db + api`; `render.yaml` para el despliegue
  público.

```
backend/app/core/                 config, db, security, basic_auth
backend/app/modules/<dominio>/    models.py schemas.py service.py router.py
backend/app/weber/                adaptador Weber (PDF); el núcleo no lo importa
backend/alembic/versions/         un fichero por migración, numerado
backend/tests/                    pytest
frontend/src/                     una pantalla por dominio
docs/                             ADRs + recorrido por fases (español)
```

**Regla de capas**: los routers traducen HTTP→dominio y nada más. Las reglas
de negocio y los cálculos viven en `service.py`. La validación de entrada es de
Pydantic. `main.py` es el único punto donde se cablea `app.weber`.

## 3. Comandos de verificación

```powershell
docker compose up db -d
docker compose build api
docker compose run --rm api alembic upgrade head
docker compose run --rm api pytest -q
docker compose run --rm api ruff check .
npm run build            # en frontend/
```

La imagen de la API hornea el código: **cambios de `.py` o migraciones exigen
`docker compose build api`**, si no los tests corren contra el código viejo.
El Python del host no tiene dependencias (`No module named 'sqlalchemy'`): no
usar `py -m pytest`.

## 4. Estado de fases

- **F0** `customers` slim → **F1** `offers + pricing_engine` → **F2** hardening
  multi-país → **F3** CSV/datos externos → **F4** contratos/técnicos →
  **F5** empaquetado vendible.
- F0–F3 implementados y documentados en `docs/recorrido-f0.md` … `f3.md`.
- F4 aparece en `docs/recorrido-f4.md` pero está incompleto.

### Última cabeza de migraciones: `0014`

| Migración | Contenido | Estado |
|---|---|---|
| `0001`–`0010` | customers, offers, users/scope, equipment, catálogos, precios máquina, Velocity One | publicadas |
| `0011` | `customer_sites` + `equipment.site_id` + `Distance.subsidiary_id` | **solo local** |
| `0012` | 16 rutas alemanas | **solo local** |
| `0013` | catálogo global `equipment_catalog` (20 entradas) | **solo local** |
| `0014` | metadatos de rutas italianas | **solo local, aplicada en local** |

Las migraciones `0011`–`0014` **no están en producción**. Commit publicado más
reciente: `d079506`.

## 5. Datos reales conocidos

- `customer_id` = `SAP Debitor ID` externo, UNIQUE. `id` = UUID interno.
- Filiales: `Weber Iberica`, `Weber France`, `Weber Germany`, `Weber Italy`.
  `Weber Italy` supervisa `Italy` y `Malta`.
- Weber Italy en la BD local: **168 clientes, 3.038 equipos, 0 ofertas**.
- Rutas italianas: 110 filas, origen `39044 Egna / Neumarkt (Bolzano)`,
  fecha de datos `2026-10-01`, fuente
  `C:\Users\danma\Documents\Italia_Distancias_desde_Egna_CSV.csv`.
  Semántica: trayectos de ida; `km` de carretera sin tramo marítimo;
  `driving_hours` = conducción; `trip_hours` = total de ida con ferry;
  tiempos al cuarto de hora.
- Rutas alemanas: 16 filas, catálogo cerrado, **congelado por decisión de
  negocio**.
- Catálogo de equipos: 17 líneas + 3 módulos, todos con `workload` y `price` en
  `NULL`.

## 6. Pausado por decisión del usuario

No retomar sin que lo pida explícitamente:

- **Alemania**: la tabla de 16 rutas está cargada; falta decidir mapeo
  PLZ→Bundesland y otros catálogos.
- **Catálogo de equipos**: implementado y testeado, pero las **49
  asociaciones de línea son inferencias** creadas por la IA (similitud de
  numeración), marcadas `is_confirmed=false`. No sirven como dato de negocio.
  Faltan los `material_no` de los 3 módulos y todos los precios/workloads.
- No inventar códigos, precios ni mappings para "completar" tablas.

## 7. En curso / pendiente inmediato

1. **Importar las 110 rutas italianas reales** en la BD local. El importador
   está hecho y testeado; la carga real falló con
   `curl: (52) Empty reply from server`. Reintentar con health check y auth
   correctos, exigir `total_rows=110` y `errors=[]`, luego `dry_run=false`.
2. **Importar ubicaciones físicas de clientes.** El CSV SAP
   (`C:\Users\danma\Downloads\report1790238371853.csv`) trae `Physical Street`,
   `Physical City`, `Physical Zip/Postal Code`, `Physical State/Province`,
   `Physical Country`. El importador existente ya soporta esas columnas y crea
   `customer_sites` deduplicados. Sin province en `customer_sites` no se puede
   enlazar un sitio con su fila de `Distance` ni precargar km/tiempo en la
   oferta.
3. **Tarifas de Italia**: las define la filial. Están vacías a propósito. La UI
   permite crearlas sin valores precargados; `currency` es obligatoria.

## 8. Convenciones que no se negocian

- Dinero en `Decimal`, nunca `float`. Moneda explícita.
- Toda operación atómica va en transacción con rollback claro.
- Errores de DB nunca al usuario: se traducen a errores de dominio → HTTP.
- Todo cambio de esquema pasa por Alembic, nunca SQL manual.
- Sin `except Exception: pass`, sin TODOs que oculten fallos, sin valores por
  defecto silenciosos.
- Tests obligatorios para cada regla de negocio, sobre todo `pricing_engine.py`.
- **Comentarios y docstrings en inglés; docs en español.**
- Un archivo cada vez, explicando el diff. Nada de bloques gigantes.
- Nada de "clean architecture" por obligación: si una capa no aporta valor
  todavía, no se crea.
- Backend es la fuente de verdad. React no calcula precios ni reglas.
- No hacer commit ni push sin autorización explícita del usuario.

## 9. Despliegue (solo si se pide)

- Frontend: `https://weber-guardian.vercel.app` · API:
  `https://weberguardian-api.onrender.com`.
- Usar la URL Vercel de producción, nunca una preview con hash (CORS).
- Render usa el **Session pooler** de Supabase (no la pooled completa).
- `ALLOWED_ORIGINS=https://weber-guardian.vercel.app`.
- La contraseña de Supabase apareció en una conversación: **rotarla**.
- Basic gate y `DEV_AUTH_ENABLED=true` son temporales.
- `npm audit` marca una vulnerabilidad alta preexistente de Vite `6.3.*`; no
  aplicar `audit fix --force`.

## 10. Mapa de endpoints clave

| Dominio | Prefijo | Nota |
|---|---|---|
| customers | `/api/v1/customers` | slim, F0 |
| equipment | `/api/v1/equipment` | incluye `site_id` |
| offers | `/api/v1/offers` | `pricing_engine` calcula todo |
| prices | `/api/v1/prices/{subsidiary}` | upsert, `404` filial inexistente, `409` concurrencia |
| distances | `/api/v1/distances` | `POST /import` con `dry_run` y `origin_city` |
| equipment_catalog | `/api/v1/equipment-catalog` | resolver individual y por lotes |
| imports | `/api/v1/imports` | CSV SAP, dry-run, reporte de errores |

## 11. Ficheros que se tocan más a menudo

- `backend/app/modules/distances/service.py` — parser de rutas y upsert atómico.
- `backend/app/modules/imports/service.py` — importación SAP y sitios físicos.
- `backend/app/modules/prices/service.py` — tarifas por filial.
- `backend/app/modules/offers/pricing_engine.py` — cálculo autoritativo.
- `frontend/src/OfferBuilder.tsx` — resolución de equipos y catálogo.
- `frontend/src/Config.tsx` — tarifas + distancias.
- `docs/recorrido-f3.md` — Importar, catálogos, rutas, tarifas.

## 12. Cómo continuar

1. Leer `AGENTS.md` y este fichero.
2. `git status` para ver el trabajo local sin commitear; no revertirlo.
3. `docker compose up db -d`, `docker compose build api`, `alembic upgrade head`.
4. Trabajar un archivo, explicarlo, y validar con pytest + ruff + build.
5. Preguntar antes de commit, push, despliegue o migraciones en producción.