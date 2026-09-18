# Recorrido F0 (qué hace cada pieza)

1. React `Customers.tsx` (`frontend/src/Customers.tsx`) llama a `GET /api/v1/customers` con `fetch` directo a `http://localhost:8000`. La API permite el origen `http://localhost:5173` vía CORS dev en `app/main.py`.
2. `app/main.py` recibe la petición y delega al `router` de customers.
3. `router.py` valida la query con FastAPI (`limit/offset` vía `Query(ge/le)`), pide una `Session` a `get_db()`.
4. `service.py` ejecuta `SELECT ... LIMIT/OFFSET` con SQLAlchemy sync y devuelve modelos.
5. `schemas.py` (`CustomerOut`) convierte los modelos a JSON.
6. `POST` igual pero con `CustomerCreate` validando la entrada (`Field(min_length/max_length)`, `422` ante strings vacíos).

- `config.py`: de dónde sale DATABASE_URL (`.env`, Docker lo sobrescribe con el host `db`).
- `db.py`: quién abre/cierra la sesión (una `Session` por request, cerrada vía `yield`).
- `models.py`: cómo es la tabla (`id` interno vs `customer_id` externo). Tipo `Uuid` genérico: `UUID` en Postgres, `CHAR(32)` en SQLite, así el mismo modelo vale en prod y tests.
- `service.py`: transacción explícita. `try: commit / except IntegrityError: rollback + raise CustomerAlreadyExists`. La restricción `UNIQUE(customer_id)` es la autoridad contra duplicados bajo concurrencia, no un `if` en Python.
- `router.py`: traduce `CustomerAlreadyExists` a HTTP `409` con solo `customer_id` en el detalle (sin fugar errores crudos de DB).
- `tests/`: solo a nivel de servicio (SQLite en memoria). Cubren crear+listar y el error de dominio por duplicado, incluyendo que la sesión sigue usable tras el rollback.
- `alembic/env.py`: carga `DATABASE_URL` + `Base.metadata` (importa los modelos para que autogenerate los vea), añade la raíz del proyecto a `sys.path` (Alembic carga `env.py` por ruta), ejecuta migraciones online (conectado) u offline (solo SQL).
- `alembic/versions/0001`: cómo nace la tabla en Postgres (`sa.Uuid()`, `customer_id UNIQUE`, `created_at now()`).
