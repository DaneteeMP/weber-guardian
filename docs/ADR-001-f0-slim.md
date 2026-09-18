# ADR-001 — F0 slim

- SQLAlchemy sync, sin async (aprender primero el recorrido completo).
- Estructura mínima por módulo, crece cuando duela. Sin repository/utils prematuros.
- `id UUID` PK interna + `customer_id` UNIQUE externo (SAP/Salesforce). Tipo `Uuid` genérico para que prod (Postgres) y tests (SQLite) compartan el mismo modelo.
- Sin JWT/RBAC/tenancy en F0. Solo local/demo. Entran en F2.
- Paginación mínima `limit/offset` desde que `list_*` es real, validada con `Query(ge/le)`.
- Validación a la entrada: `Field(min_length=1, max_length=...)` iguales a la columna. Strings vacíos estilo CSV reciben `422`, nunca llegan a la DB.
- Duplicados: `UNIQUE(customer_id)` es la autoridad. El service captura `IntegrityError`, hace rollback y lanza `CustomerAlreadyExists`; el router lo traduce a `409` sin exponer errores de DB.
- Decimal/NUMERIC desde F1 (dinero). PDF Weber en `app/weber/`.
- `modules/` no sabe que existe `weber/`. Weber se adapta al núcleo.
- Python fijado: `3.12-slim` en Docker por estabilidad de F0. Sin subir a 3.14 ni cambiar dependencias para adaptarse al host sin ADR explícito después de cerrar F0.
- `requirements.txt` congelado para F0. Auditoría a `pyproject.toml` limpio solo después del E2E de F0, con justificación por dependencia.
