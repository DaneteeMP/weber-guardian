# ADR-003 — Catálogo de workloads

Contexto: WeberAssistant calculaba el tiempo de mantenimiento por material/módulo
(`TblWorkLoad` legacy). La migración `0018` solo sembró 63 códigos con horas; el
resto de materiales nunca tuvo valor. El catálogo editable se reconstruye desde
cero, familia a familia.

## Decisión

- **Reglas globales** (`workload_rules`): una fila por regla real ("Checkweigher
  100" = 1.00 h). Las horas son `Numeric(10,2)` (Decimal, nunca float). No hay
  override por cliente ni por máquina: cambiar una regla afecta a todo borrador
  futuro que resuelva a ella.
- **Un material = como mucho una regla** (`workload_rule_materials.material_no`
  es UNIQUE). Enlazar de nuevo es mover la fila, no crear una segunda.
- **`legacy_type_code` es trazabilidad, no identidad**: no es único porque varias
  reglas pueden venir del mismo código legacy (CCW, CCA, WPR). El código real de
  la regla es su `name`.
- **Horas `NULL` = `needs_review`**: una regla sin horas existe pero aparece como
  material no resuelto hasta que se puntúa. Nunca un valor por defecto silencioso.
- **Clasificación de variantes en código, una carpeta por familia**
  (`component_names/families/<code>/rules.py`). `classify_family` despacha por
  `type_code` y devuelve `None` cuando la familia no tiene clasificador todavía;
  `None` significa "sin decidir", **nunca** "mono".
- **El catálogo es datos, no migraciones**: se mueve con export/import JSON
  (`catalog_transfer`), upsert idempotente y no destructivo por clave natural,
  una transacción, nunca borra. Las horas viajan como **string** para conservar
  la escala Decimal exacta.
- **Borrado protegido**: una regla en uso (material enlazado e instalado en ≥1
  cliente) devuelve `409`; una línea en uso, igual. Sin borrados silenciosos.
- **Esquema solo por Alembic** (`0024_workload_rules.py`), nunca a mano.

## Consecuencias

- Las reglas sin horas quedan visibles como unresolved; son trabajo pendiente, no
  un error.
- El **diccionario** (`component_names`) debe importarse **antes** del catálogo:
  un `material_no` sin fila en el destino se omite y se reporta (`materials_skipped`).
- Reimportar el propio export es un no-op; sirve para verificar que destino y
  origen tienen el mismo catálogo.
- El frontend no contiene reglas de negocio: solo pinta lo que dicta la API.

## Alternativas descartadas

- **Horas por material** (como el legacy): inmaintanible, miles de filas y sin
  una regla única que corregir en un sitio.
- **Un clasificador global** para todas las familias: mezclaría criterios de
  dominios distintos en un solo archivo difícil de revisar.
- **Distinguir variantes sin separar horas** (p. ej. mono/multi del CCW bajo el
  mismo código): perdería la diferenciación de precio, que es justo el objetivo.
