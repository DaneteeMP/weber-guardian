# WeberGuardian — instrucciones para agentes (contexto + reglas)

## 1. Contexto del proyecto
- Rebuild Python de WeberAssistant. Gestión postventa de maquinaria (ofertas, técnicos, contratos). Empieza en una filial, objetivo multi-país y multi-sector vendible.
- Stack F0: `React+TS+Tailwind` (clon Salesforce), `FastAPI + SQLAlchemy sync + Postgres + Alembic`, `pytest + ruff`, `docker-compose` con `db+api`.
- Layout backend: `app/core/` (config, db), `app/modules/<dominio>/{models,schemas,service,router}.py`, `app/weber/` (adaptador Weber, nace en F1, el núcleo nunca importa de `weber`), `alembic/versions/`.
- Fases: F0 `customers` slim → F1 `offers + pricing_engine` → F2 hardening multi-país → F3 CSV/catálogos → F4 contratos/técnicos → F5 empaquetado. Ver `README.md` y `docs/`.
- Dato real F0: `customer_id` = `SAP Debitor ID` externo UNIQUE, `id` = UUID interno PK. 1 cliente → N equipos (eso será `equipment` en F3, no en F0).

## 2. Workflow obligatorio
- Leer los archivos implicados antes de editar. No editar a ciegas.
- Explicar antes de escribir piezas importantes: qué entra, qué sale, qué capa lo procesa y por qué.
- Un archivo cada vez, con explicación del diff. Nunca bloques gigantes. Parar para preguntar "¿por qué?".

## 3. Verificación estándar
- Python fijado: `3.12-slim` en `backend/Dockerfile`. Es la verdad para F0 por estabilidad, no por límite de Pydantic (2.12+ ya soporta 3.14). No adaptar pines al Python local del host ni subir a 3.14 sin ADR explícito después de cerrar F0.
- `requirements.txt` actual está congelado para F0. Auditoría a `pyproject.toml` limpio solo después del E2E de F0, con justificación por dependencia.
- Comandos: `docker compose up db -d`, `docker compose build api`, `alembic upgrade head`, `pytest`, `ruff check`. Sintaxis rápida sin Docker: `py -m py_compile <archivo>`.
- No exponer errores crudos de DB al usuario. Mapear a errores de dominio → HTTP.

## 4. Definition of Done por archivo
- Código explícito y depurable, docstrings/comentarios en inglés, docs en español.
- Tests que cubren la regla tocada. Sin `except Exception: pass`, TODOs que oculten problemas, defaults silenciosos o `TRUNCATE/reset` abiertos.
- Si se detecta bug heredado de WeberAssistant, documentarlo en `docs/` y decidir conserva/corrige. Actualizar `docs/recorrido-f0.md` o ADR si cambia el diseño.
- Al cerrar cada fase: commit + push a GitHub (un commit por fase, mensaje `F<n>: ...`). Nunca subir secretos (`.env` está gitignorado).

## Reglas de construcción (obligatorias)

1. No implementar varias fases a la vez. Completar F0 antes de tocar F1.
2. Nada de código "mágico" sin explicarlo. Cada archivo nuevo indica qué responsabilidad tiene, por qué existe y quién lo utiliza. Evitar abstracciones cuya necesidad no pueda explicarse.
3. Antes de escribir una pieza importante, explicar el diseño: qué entra, qué sale, qué capa lo procesa y por qué.
4. No copiar Rust línea por línea. WeberAssistant es referencia funcional (requisitos, comportamiento, datos), la implementación se rediseña en Python.
5. No introducir dependencias por comodidad. Antes de añadir una librería, explicar qué problema resuelve y si puede hacerse con lo existente.
6. Backend como fuente de verdad. React no contiene reglas de negocio, cálculos de precios ni decisiones autoritativas.
7. Dinero siempre con Decimal, nunca float. Moneda explícita.
8. Transacciones explícitas. Toda operación atómica va en transacción con rollback claro.
9. Nada de `except Exception: pass`, TODOs para ocultar problemas, unwraps, valores por defecto silenciosos o errores de DB expuestos al usuario.
10. Tests antes de dar por terminada una regla de negocio. Especialmente `pricing_engine.py`.
11. No hacer "clean architecture" por obligación. Si una capa/archivo/patrón no aporta valor todavía, no se crea.
12. Código fácil de depurar. Implementaciones explícitas y sencillas antes que abstracciones.
13. No modificar el esquema PostgreSQL manualmente. Todo cambio pasa por Alembic.
14. OpenAPI representa el contrato real. Pydantic es la fuente de verdad para requests/responses.
15. Después de cada bloque funcional, verificar de extremo a extremo (frontend → API → servicio → DB) y explicar qué ha ocurrido.
16. Problema heredado de WeberAssistant: no reproducirlo por compatibilidad. Documentar comportamiento antiguo y decidir si se conserva o corrige.
17. No cambiar tecnologías o arquitectura sin justificarlo primero.
18. Objetivo: sistema que el desarrollador pueda explicar línea por línea, no código rápido.
19. Ante "más fácil para la IA" vs "más comprensible para el desarrollador", priorizar lo segundo. Antídoto contra vibe coding.
20. Construir archivo a archivo con explicación (config.py → explicar → db.py → explicar → modelo → schema → service → router → test). Nunca bloques gigantes. Parar en cualquier punto para preguntar "¿por qué?".
21. Todos los comentarios y docstrings en el código deben estar en inglés. El resto de documentación puede estar en español.
