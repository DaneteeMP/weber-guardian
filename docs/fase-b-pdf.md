# Fase B — Motor PDF (WeasyPrint) + modal Imprimir PDF

## Qué cambia y por qué

El PDF de ofertas pasó de generador raster (imagen sin texto seleccionable) a **WeasyPrint + Jinja2**: texto seleccionable y buscable, wordmark Weber y anexos modulares derivados del alcance Guardian. El contrato completo está traducido a **es/en/de/pt/it** (ver *Traducciones*). `app/weber/pdf/` implementa el motor; `app/weber/pdf/__init__.py` exporta `render_document as build_offer_pdf`, de modo que `main.py` no cambia (fachada). El generador raster (`legacy_raster.py`) fue **eliminado**.

## Estructura

| Pieza | Responsabilidad |
|---|---|
| `pdf/values.py` | `OfferValues`: tokens del documento (`executor_block`, `executor_is_provisional`, `token_values(doc, locale)`). Único puente datos→plantilla. |
| `locales.py` | Normalización de idioma (`normalize_locale`: códigos es/en/de/pt/it + alias legacy, default `en`). |
| `layout.py` | `BASE_CSS` (fuentes Noto Sans, marca, `.draft-banner`). |
| `content/` | Texto EN de origen (`cover`, `master`, `annex1`-`annex7`, `summary`, `breakdown`, `signatures`, `labels`) con `id` estable por nodo + catálogos de traducción `es/de/pt/it`. |
| `pdf/templates/document.html` | Plantilla Jinja2 única. Claves de sección y tokens `{{...}}`. |
| `pdf/renderer.py` | Compone secciones por alcance, inserta anexos personalizados (`_insert_custom_annexes`, **antes** de `summary` para que firmas queden al final), renderiza HTML y genera el PDF. Rechaza idioma no soportado (422). |

**Regla core/weber**: el núcleo (`app/modules/**`) **nunca importa** `app.weber`. La validación de idioma solo ocurre al render; el modelo guarda el idioma como string libre (max 32).

## Portada

La primera página reproduce la portada legacy: wordmark Weber arriba a la derecha (elemento de página), logo Guardian centrado, título azul centrado (`cover.title`, p. ej. «CONTRATO DE MANTENIMIENTO») y dos bloques de parte.

- **Ejecutor** (Weber) y **Ordenante** (cliente): etiqueta, nombre legal en azul y negrita, dirección (las líneas vacías se omiten) y alias alineado a la derecha. Se implementa con el bloque `party` (renderer + plantilla + CSS `.party`).
- Los textos de etiqueta/alias/preámbulo se traducen por idioma (`cover.executor.label`/`.alias`, `cover.customer.label`/`.alias`, `cover.preamble`); los términos Ejecutor/Ordenante son por idioma: Executor/Client · Auftragnehmer/Auftraggeber · Executor/Cliente · Esecutore/Committente.
- Nombres y direcciones salen de los tokens de la oferta (`Weber_Legal_Entity`, `Customer_Legal_Name`, `Weber_Address`, `Customer_Postcode_City`, ...). La calle del cliente no está en el modelo: si viene vacía, la línea se omite.
- Los datos de acuerdo/oferta/fechas/facturación ya **no** se muestran en la portada (siguen en el Anexo 1, sección «Información del contrato»).

## Página de desglose (Anexo comercial)

**Penúltima** página, justo antes de las firmas: reproduce el «ANEXO 1, Relación de máquinas y módulos» legacy (`content/breakdown.py`).

- Recuadro del cliente (nombre + dirección; las líneas vacías se omiten) y meta a la derecha (Fecha, N.º oferta) y bajo el recuadro (Frecuencia de Inspección, Tipo).
- Tabla por línea de oferta: Nº de línea, Módulo (equipo + descripción) e Importe; totales (Total, Kit básico de recambios, Descuento, Importe total sin IVA).
- Texto introductorio + lista de condiciones + «NOTAS:» con los descuentos.

Se implementa con el bloque `commercial_breakdown` (renderer + plantilla + CSS `.breakdown`). Los textos (título, etiquetas, cabeceras, totales y notas) se traducen por idioma (`breakdown.*`). Para intercalarla entre el resumen y las firmas, la sección de firmas se separó en `content/signatures.py`; el orden de `SECTIONS` es `… summary → breakdown → signatures`.

### Guardian type (Tipo)

El «Tipo» del desglose es el **Guardian type** de la oferta: `Inspection` (valor interno `audit`), `Off-Guardian` o `Basic Kit`. Antes solo alimentaba el cálculo; ahora se persiste en `offers.offer_type` (migración **0030**), se expone en `OfferOut` y se imprime vía el token `{{Guardian_Type}}` (`guardian_type.*` en los catálogos). El selector del builder se corrigió a esas **tres** opciones (se eliminó la opción errónea `Guardian`).

## Modal Imprimir PDF (frontend)

`frontend/src/components/PrintPdfModal.tsx`, abierto desde `OfferBuilder` (botón "IMPRIMIR PDF") y desde la fila de `Offers`. Ocupa ~96vw de la pantalla (preview del PDF a pantalla casi completa).

- **Idioma del contrato** (`language`) y **anexos personalizados** (`custom_annexes`). El alcance Guardian se edita **solo** en el rail del builder: el modal no lo toca.
- **Anexos Word**: botón "Adjuntar Word (.docx)" → el backend parsea el archivo (`python-docx`: párrafos con negritas/cursivas y tablas → HTML sanitizado, sin imágenes) y lo añade a la oferta. El archivo original **no se conserva**. Título por defecto = nombre del archivo (editable). Límites: .docx únicamente, 5 MB, 10 anexos por oferta.
- **Auto-guardado** vía `PATCH /offers/{id}/document` (solo `language` + `custom_annexes`): el **idioma guarda al instante** al cambiar el selector; las ediciones de anexos se agrupan con debounce de 500 ms. Tras cada guardado o subida se refresca el preview (blob URL en `<iframe>`). El botón Descargar se deshabilita mientras hay cambios sin guardar, guardando, renderizando o subiendo; bloqueado mientras algún anexo no tenga título.
- Las respuestas se descartan si una edición posterior ya haya sido enviada (contador `sequence`).

## Backend del modal

- Migración **0029**: columna `custom_annexes JSON NOT NULL DEFAULT '[]'` en `offers`.
- `PATCH /offers/{offer_id}/document` (`admin`/`sales`): `OfferDocumentSettingsIn` con `language`, `guardian_selections`, `custom_annexes`. **Semántica partial**: campo omitido o `None` = mantener valor. Títulos de anexos requeridos (min 1 tras strip), máximo 10.
- `POST /offers/{offer_id}/document/annexes` (`admin`/`sales`, multipart): recibe un `.docx`, lo parsea con `offers/docx_annex.py` (texto escapado; solo `<p>`, `<strong>`, `<em>`, `<table>`) y añade `{title, body_html}` a `custom_annexes` en transacción. 422 si la extensión no es .docx, el archivo supera 5 MB o no contiene texto.
- Anexos personalizados: con `body_html` se imprimen como HTML parseado; con solo `body` (texto manual vía API) se imprimen como párrafos verbatim (sin traducción, sin resolución de tokens). Página propia cada uno, **antes** de `summary` (firmas siempre al final).

## Traducciones

El texto de origen del contrato es **inglés** y vive **inline** en los módulos de `app/weber/content/` (`cover`, `master`, `annex1`-`annex7`, `summary`, `breakdown`, `signatures`), con un `id` estable por nodo. Cada idioma añade un catálogo `MESSAGES` en `content/{es,de,pt,it}.py`:

- `content/__init__.py` mantiene `_CATALOGS` (`es`/`de`/`pt`/`it`) y `get_text(locale, node_id, default)`: si falta el `id`, cae al inglés. `node_text` traduce nodos `id`/`text`; las listas (`ul`/`ol`/`dl`/`lines`) se traducen como listas.
- El renderer traduce **todo** el documento: portada, el **contrato legacy** (0 + I–IX), los seis anexos de módulo con sus servicios Sxxx, el desglose comercial, el resumen y las firmas. Después resuelve los tokens `{{...}}`.
- No se traducen los nodos que contienen **solo** tokens (`annex1.special.conditions`) ni los contenedores (`cover.executor`, `cover.customer`, `breakdown`, `annex3.rates`, `annex1.equipment`, `annex1.modules`, `annex1.summary`, `summary.scope`, `summary.signatures`): su contenido traducible vive en los nodos anidados.
- Los catálogos son **borrador generado** pendiente de revisión legal. `tests/test_content.py` exige paridad total: los cuatro catálogos cubren todos los `id` traducibles, con la misma forma (str vs lista) que el origen, la misma cantidad de elementos y sin claves desconocidas.

## Filtro de datos y tarifas por banda

- **Filtro de datos (anexos)**: en las secciones `annex*` el renderer elimina cualquier párrafo, ítem de lista o fila de tabla que contenga un `{{...}}` sin valor (`_missing_tokens`). Las cláusulas descriptivas se mantienen; un anexo solo desaparece si se queda sin contenido. Así el contrato nunca imprime frases con datos vacíos.
- **Tarifas por banda**: `prices` gana `band1..3_rate_without/with` (migración **0031**), editables en Config → Subsidiary rates con una tabla propia (matriz horas × tipo de día → I/II/III + tarifas con/sin contrato). El bloque `band_rates` del Anexo 3 (Service Support) imprime las dos tablas solo si la filial tiene las bandas configuradas.

## Banner DRAFT

Si la filial no tiene datos legales (`executor_is_provisional`), la portada muestra `DRAFT - SUBSIDIARY LEGAL DETAILS REQUIRED` en rojo. Comportamiento heredado conservado a propósito (decisión de diseño, no bug).

## Verificación

- Backend: 394 tests + ruff limpio (1 fallo preexistente conocido: `test_scope.py::test_equipment_response_includes_physical_site`).
- Frontend: `npm run build` (tsc + vite) y `npm run test` (13 tests) verdes.
- Muestras E2E: PDF de 16 páginas renderizado y verificado (portada, contrato legacy, anexos con tarifas por banda, desglose y firmas) en **es/de/pt/it**; banner DRAFT verificado.
