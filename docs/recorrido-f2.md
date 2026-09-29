# Recorrido F2 — autorización multi-país compatible Entra (sin login propio)

Regla de arquitectura: `Entra oid → quién es` · `Guardian DB (role, subsidiary_id) → qué puede y sobre qué`.

## 1. Esquema (`0003_users_and_scope.py`)

- `users`: `id UUID`, `external_id UNIQUE` (= oid Entra, estable ante cambios de email), `email`, `display_name`, `role (admin/sales/viewer)`, `subsidiary_id NULL` (`NULL` = alcance global). Sin passwords ni hashes en ningún sitio.
- `customers.subsidiary_id NULL`: `NULL` = fila legacy, visible para todos los ámbitos.
- `offers.created_by NULL→users.id` (`SET NULL` si el usuario se borra): auditoría de autoría.
- Cero dependencias nuevas: ni `pyjwt` ni `bcrypt` (el plan inicial con login propio se descartó porque habría que eliminarlo al integrar SharePoint).

## 2. Identidad (`core/security.py` + `core/config.py`)

- `get_current_user()`: con `DEV_AUTH_ENABLED=true` y cabecera `X-Dev-User`, resuelve la fila por `external_id` y devuelve `{id, role, subsidiary_id}` (rol/filial siempre desde DB, nunca de claims). Sin mock → `401` con `WWW-Authenticate: Bearer`. La validación JWKS real de Entra entra al integrar SharePoint sin cambiar firmas de routers/servicios.
- `require_role("admin", "sales")`: factoría de dependencia, `403` si falta rol. `401` = sin identidad, `403` = sin permiso (sin filtrar si el usuario existe).
- `GET /users/me`: quién soy (rol + filial) para el badge de UI y tests.

## 3. Scope (servicios + routers)

- `list_customers/list_offers`: `subsidiary_id None` (admin/global) ve todo; con valor, ve su filial + legacy `NULL`. `offers` filtra vía join a `customers`.
- `get_offer` fuera de ámbito devuelve `None` → `404` (no `403`: no fuga existencia).
- `create_offer` firma `created_by` con el autor. Crear exige `admin|sales`; leer y `/calculate`, cualquier identidad.
- Frontend no decide visibilidad (regla 6): el filtro vive en el backend.

## 4. Dev local (`seed_dev.py`, `X-Dev-User`, compose)

- `seed_dev.py`: crea `dev-admin/dev-es/dev-de/dev-viewer` + etiqueta filiales; idempotente (`created/skipped`); aborta sin `DEV_AUTH_ENABLED=true`.
- `X-Dev-User`: disfraz local que viaja en la cabecera; en prod se ignora siempre. `docker-compose.yml` lo activa solo-dev (comentado como prohibido en prod).

## 5. Frontend i18n (5 idiomas, sin librería)

- `src/i18n.ts`: dicts `ES/EN/DE/PT/IT` tipados (`Strings` = forma del español; falta una clave = no compila) + `t()` puro.
- `App.tsx`: selector persistido + selector de usuario dev + badge `/me`; páginas con prop `lang`.

## 6. Tests y verificación

- `test_security.py` (mock apagado ignora header, oid fantasma `401`, rol/filial desde DB, matriz `403`), `test_scope.py` (stack completo por HTTP con SQLite compartido: ES⌁DE, legacy, `created_by`, `401/403`, `404` fuera de ámbito).
- Total: **27 passed**, `ruff` limpio, migración aplicada en Postgres, E2E real con `curl` + navegador.

## Herencia revisada

- No existía endpoint `reset/TRUNCATE` abierto en nuestro código (el Rust sí lo tenía): nada que borrar.
- Bug del Rust no reproducido: totales confiados del cliente, huérfanos sin transacción, errores DB crudos.
- Bug heredado nuestro, corregido: el alta de cliente en `Customers.tsx` hacía `fetch` a `http://localhost:8000` quemado con cabeceras montadas a mano (roto en producción, sin scope). Ahora va por `createCustomer()` en `api.ts`: misma base, mismas cabeceras que el resto.

## 7. Selector de filial (scope de vista, beta)

- Cabecera `X-Scope-Subsidiary` (URL-encoded, nombres con espacios): el desplegable `Filial:` de `TopBar`. Es un **scope de vista**, no un filtro de la UI: `get_current_user()` lo resuelve junto a la identidad.
- `CurrentUser.scope_subsidiary_id` = alcance efectivo de datos. Admin: filial elegida del catálogo o ausente = todas. `sales/viewer`: su filial fija; pedir otra → `403`; filial fuera de catálogo → `403` (nunca lista vacía silenciosa).
- Routers pasan `scope_subsidiary_id` a los servicios (customers, offers, equipment, dashboard, imports). `subsidiary_id` sigue siendo la filial "de casa" de la identidad. `/users/me` expone ambos.
- Frontend: `localStorage` + bump de `epoch` al cambiar (toda la app refresca), tarifas de viaje en `OfferBuilder` precargadas según el scope efectivo. El desplegable técnico `dev-*` desaparece: en beta todos arrancan como `dev-admin` (`ensureDevUser()` resetea identidades viejas para no dejar a nadie clavado sin selector). Con Entra, el selector solo sale para admin; ventas/viewer ven su filial como badge fijo.
- Verificado: 79 passed, `ruff` limpio, E2E con `curl` (filial → subconjunto, sin cabecera → todo, filial desconocida → 403, preflight CORS acepta la cabecera nueva).

## Pendiente (fuera de F2)

- Validación JWKS de Entra al integrar SharePoint (solo `security.py`).
- CRUD admin de usuarios (F4). Altas hoy = `seed_dev.py` + insert documentado.
