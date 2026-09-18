# Recorrido F1 — offers + pricing_engine (Guardian)

Backend como fuente de verdad. React presenta; el servidor calcula y persiste.

## 1. `pricing_engine.py` (puro, sin DB ni FastAPI)

- Entra `PricingInput` agregado (`work_hours, bk_hours, report_hours, trip_hours_base, km` + 5 rates + `discount_rate`, todo `Decimal`, moneda `EUR` explícita). Sale `PricingOutput` con el desglose.
- Reglas migradas de `OfferBuilder`: redondeo a jornadas de 8h (reparto del ajuste mitad a basic kit), `km<200` cerca (viaje×días, media dieta, sin hotel) vs `>=200` lejos (viaje + hotel `(días-1)`, dieta completa+media), descuento 15% sobre horas.
- Bug heredado corregido: el JS hacía `total = hours + discount + expenses + kit` (inflado) y `total_end = total - discount` (el cliente nunca recibía el 15%). Aquí `total = hours + expenses + kit` (bruto), `total_end = total - discount` (neto). Documentado en el docstring y blindado en `test_total_and_total_end_fixed` (1050/906).
- Dinero siempre `Decimal` con 2 decimales (`ROUND_HALF_UP`); horas con 1 decimal. Negativos → `ValueError`.

## 2. Tablas (`models.py` + migración `0002`)

- `offers`: cabecera + snapshot del cálculo en `Numeric` (horas `10,1`, dinero `12,2`, moneda explícita). `id_guardian_offer UNIQUE` (nº humano), `customer_id` FK → `customers.customer_id` (`RESTRICT`: no se puede borrar un cliente con ofertas).
- `offer_items`: líneas (`row_no, equipment, description, import_amount, workload`). FK → `offers.id` con `ON DELETE CASCADE` + `cascade="all, delete-orphan"` en ORM: borrar una oferta borra sus líneas (el Rust las dejaba huérfanas, igual que al fallar a mitad del bucle sin transacción).
- Migración `0002_create_offers.py` (revisa `0001`), aplicada en Postgres y descrita con `psql \d offers`.

## 3. Contratos (`schemas.py`)

- Pydantic es el contrato OpenAPI. El cliente **nunca manda totales**: `OfferCreate` lleva `customer_id + cabecera + pricing + items`; `OfferOut`/`OfferCalculateOut` devuelven el desglose calculado.
- `OfferCalculateIn` valida rangos (`ge=0`, descuento `0..1`); `422` ante vacíos o negativos.

## 4. Servicio (`service.py`)

- `calculate_price()`: dry-run puro, sin DB. Lo usa el `POST /calculate` y el propio `create_offer`.
- `create_offer()`: verifica cliente (`UnknownCustomer → 404`), calcula en servidor, genera nº genérico en-núcleo si falta (el núcleo nunca importa de `weber/`), y hace **un solo `commit`** de cabecera + líneas. Ante `IntegrityError`: `rollback` y distingue 404 (cliente borrado en carrera) de 409 (nº duplicado, `OfferAlreadyExists`). Nada de errores crudos de DB al usuario.
- `list_offers()` (filtro opcional `customer_id`, `limit/offset`) y `get_offer()` con `selectinload(items)` (sin N+1 ni `DetachedInstance` en el router).

## 5. HTTP (`router.py`, montado en `main.py` bajo `/api/v1`)

- `POST /offers/calculate` → preview sin persistir (la UI lo llama en vivo).
- `POST /offers` → `201` o `404/409` de dominio.
- `GET /offers?customer_id=` + `GET /offers/{id}` (`404` si falta). `limit/offset` validados con `Query`.

## 6. Adaptador Weber (`app/weber/`)

- El núcleo nunca importa de aquí. `guardian_numbering.py` conserva el formato legacy observado en `OfferBuilder` (`-01-` Basic Kit, `-02-` Audit, `-03-` Off-Guardian): `guardian_type_of()` parsea, `build_number()` construye con validación. Lo usará el import F3 y el frontend; F1 funciona sin él.

## 7. Tests y verificación

- `test_pricing_engine.py` (redondeo 8h, ramas km, fix total/totalEnd, Decimal 2 decimales, negativos), `test_weber_numbering.py`, `test_offers_service.py` (totales del servidor, 404, 409 sin huérfanos, filtro). Total: **16 passed**, `ruff` limpio, todo en contenedor Python 3.12.
- E2E HTTP contra Postgres con dato real (`0001012933`): `/calculate` (1050/906), `POST /offers` (`W-02-2026-0001` + 2 items), `GET ?customer_id=` y `psql` (1 oferta + 2 líneas).

## Pendiente F1 (hecho, verificar en navegador)

- Frontend `OfferBuilder` (`frontend/src/OfferBuilder.tsx`, Tailwind `weber-blue`, `SectionCard/FieldRow`): preview vía `POST /calculate` en vivo con debounce 300ms, cero cálculo en JS (solo muestra los strings `Decimal` del backend), guardado vía `POST /offers`, errores `404/409/422` visibles. `npm run build` OK (34 módulos).
