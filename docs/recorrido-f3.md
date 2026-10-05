# Recorrido F3 — datos reales: CSV + catálogos (Guardian)

## 1. Importación (`app/modules/imports/`)

- `POST /imports/upload?dry_run=true&subsidiary_id=` (`admin|sales`, multipart → `python-multipart`, única dependencia nueva justificada: sin alternativa stdlib).
- `service.run_import()`: tope 20 MB (los exports SAP reales rondan 7 MB); decode `utf-8-sig→cp1252` (mojibake tipo `B�seler`); parseo `;` + `"`; cabecera exigida (`SAP Debitor ID`, `Account Name`, `Material No.`); `""`→`NULL` (nunca se guarda vacío); validación fila a fila con nº de línea (SAP/nombre/material obligatorios, nombres consistentes por SAP).
- 1 cliente por `SAP Debitor ID` aunque venga en N filas; equipos deduplicados por hash de la fila instalada (cliente, equipo, componente, material, compra y sitio), porque un número de material puede repetirse. Corrida **atómica**: 1 error → `422` con el informe y cero escrituras. Segunda subida = todo `skipped`.
- Las columnas físicas opcionales (`Physical Street/City/Zip/State/Province/Country`) se agrupan en `customer_sites` por SAP + dirección normalizada; cada fila de equipo referencia su sitio. Esto evita sobrescribir una dirección cuando un cliente tiene varias plantas. El código postal se conserva como texto.
- `schemas.py`: el informe es el producto (`ImportReport` + `RowError{line}`; `1` = fichero/cabecera, `≥2` = filas).

## 2. Catálogos (tablas + lectura, migración `0005`)

- `equipment` (migración `0004`, ampliada en `0011`): una fila por componente instalado (`equipment_name, machine_type, component_type, material_no, customer_id, site_id`); nace del import; `GET /equipment?customer_id=` incluye su sitio físico, con auth y scope.
- `prices`: una fila por filial (`currency/km/tech/dietas/hotel`, `Numeric`); `GET /prices/{subsidiary}` (fuera de tu filial → `404`, sin fugar). El admin puede crear la fila solo para una filial registrada; no hay tarifa automática y moneda/valores deben indicarse explícitamente.
- `distances` (`0011`/`0012`/`0014`): clave única `subsidiary + province`. `0012` conserva las 16 rutas alemanas. `0014` añade sigla, región, ciudad de referencia, origen, horas de conducción, itinerario y fecha de los datos. Para Italia, `km` es carretera sin tramo marítimo; `driving_hours` es conducción; `trip_hours` es el tiempo total de ida, ferry incluido cuando aplique.
- `POST /distances/import`: CSV admin con simulación y validación completa por fila. Reconoce la cabecera italiana después de filas de notas, interpreta km con separador de miles (`1.545` → `1545`) y tiempos `h:mm` a cuartos de hora. Importación atómica mediante upsert por filial/provincia; las provincias omitidas se conservan. El CSV de Egna (01/10/2026) se importó localmente: 110 rutas, 0 errores.
- `basic_kit`: `model → horas + repuestos`. Se conserva como concepto separado; actualmente el motor de precios no consulta esta tabla, sino que recibe `bk_price` en el payload de oferta. No fusionarla con otros catálogos sin decidir el efecto en precios.
- `machine_prices`: `model → precio anual + inspecciones`; también permanece separado del precio manual de módulos.
- `equipment_catalog` (`0013`): catálogo global de 17 familias de línea y 3 módulos, con workload y precio editables; ambos comienzan en `NULL` hasta cargar valores verificados. Las asociaciones son exactas (`machine_type` para líneas, `material_no` para módulos), sin reglas por prefijo. Los códigos candidatos insertados por `0013` quedan `is_confirmed=false`; el resolver solo devuelve coincidencias confirmadas. No se cargan identificadores de módulos porque los valores SAP disponibles no permiten distinguir mono, multitrack y Bandsystem con certeza.
- `seed_dev.py` rellena `equipment_catalog.price` y `workload` con importes y horas **inventados** para que la demo no muestre celdas vacías. Contradice a propósito la decisión de `0013` de esperar datos verificados, y por eso la regla que lo hace seguro juzga cada campo por separado: solo se escribe un campo que esté en `NULL`, así que un valor metido por un administrador gana siempre y el seed no lo pisa. Al cargar la lista real hay que borrar `EQUIPMENT_CATALOG_VALUES` del seed. Cubierto por `tests/test_seed_dev.py`.
- `0015_confirm_line_catalog_matches.py` confirma los 49 códigos `machine_type` que `0013` insertó como candidatos, replicando su `LINE_CANDIDATES` para que ambos ficheros se comparen uno a uno. Antes de actualizar cuenta las filas que encuentra y revienta si no son 49: un `UPDATE` que casa menos filas de las previstas informa éxito igual y dejaría parte del catálogo sin resolver. El `downgrade` va sin guardia a propósito, para que revertir una revisión siempre sea posible.
- Las 3 entradas de módulo del catálogo siguen **sin ninguna asociación** `material_no`, así que ningún módulo resuelve y sus precios no salen en ninguna oferta. Los `component_type` reales de SAP (Slicer, Interleaver, Transport Conveyor, ...) no están en el catálogo: tiene 3 opciones de checkweigher y los datos traen 50 `component_type` distintos. Hasta que se cargue el mapeo real, la columna Module de la oferta muestra el `component_type` y la fila queda marcada como sin precio.
- `frontend/src/catalogLines.ts` es la función pura que reparte el catálogo entre las filas de la oferta, con sus tests en `catalogLines.test.ts` (vitest). Reglas: el precio de línea va **una sola vez**, en una fila propia etiquetada con el label del catálogo; un módulo confirmado suma en su propia fila; un componente sin coincidencia conserva su `component_type` y queda marcado. `OfferBuilder` ya no calcula esto inline.
- `prices` (tarifas de viaje) se siembra para las 6 filiales que usa `seed_demo.py`. Antes faltaban Benelux, France, Italy y Latina: `GET /prices/{filial}` devolvía 404, `OfferBuilder` se tragaba el error con `.catch(() => {})` y la oferta se calculaba con todas las tarifas a 0. `currency` va explícito en cada fila del seed; para Weber Latina se sembró EUR, que es una decisión pendiente de revisar cuando exista la lista por país.
- El CRUD del catálogo global está en la pestaña admin Equipos; los catálogos anteriores conservan sus pantallas en Configuración. Los datos globales no dependen de la filial seleccionada.

## 3. `salesforce/SyncPort` (vacío)

Interfaz `push_offer/pull_customers` con `NotImplementedError`. Reserva la costura para F4+; importar este módulo nunca toca red.

## 4. Frontend

- `OfferBuilder`: precarga rates del catálogo según tu filial (`/me → /prices/{sub}`); el cálculo autoritativo sigue en `/calculate`.
- `Config`: las tarifas parten vacías y cada filial puede introducir su moneda/valores; en Distancias Italia aparece el importador CSV con preview antes de activar Importar.
- `ImportData`: selector de fichero + filial + Simular/Importar clientes/equipos; renderiza el informe (creados/omitidos/errores con línea). El `422` trae el informe dentro del `detail` y se parsea en pantalla. Para rellenar las ubicaciones de los 168 clientes italianos hace falta importar el SAP CSV que incluya sus columnas físicas.
- `i18n.ts`: clave `nav_import` en los 5 idiomas.

## 5. Tests y verificación

- `test_imports.py` (formas reales del SAP: `dry_run` no escribe, corrida idempotente, 1 error aborta todo, `cp1252`, cabecera mala), `test_catalogs.py` (lecturas + creación de tarifa de filial), `test_distance_import.py` (prefacio CSV, formatos km/tiempo, simulación, atomicidad e idempotencia).
- `test_imports.py`: también cubre sitios repetidos en varias filas, conservación de ceros iniciales del código postal y enriquecimiento idempotente de equipos que ya se habían importado sin dirección.
- E2E Zambeef real: `dry_run` → crear (cliente ZM + 2 equipos) → re-subida `skipped` → `GET /equipment` + `psql`.

## Herencia

- `import_data.rs` frágil del Rust: sustituido (encoding, `""`, duplicados, informe con líneas). No reproducido.
