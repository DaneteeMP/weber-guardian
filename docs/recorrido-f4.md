# Recorrido F4 — PDF oficial + picker + dashboard (Guardian)

## Alcance real de F4

Contratos y técnicos, como iban en el plan inicial, **no se implementan**:
el contrato de mantenimiento *es* el PDF que nace de la oferta (ya hecho
abajo) y no hay gestión de técnicos por ahora. F4 = paridad pendiente
con WeberAssistant (PDF, picker, dashboard).

## 1. PDF oficial en backend (`GET /offers/{id}/pdf`)

- Decisión (tuya): el frontend solo solicita y descarga; el backend valida,
  carga datos oficiales, calcula con su motor y genera. Nada del enfoque
  `generateOfferPdf.ts` del frontend antiguo.
- Arquitectura puerto-adaptador: `offers/document.py` (`OfferDocument` puro
  + protocolo `PdfRenderer`) en el núcleo; renderer `reportlab` en
  `app/weber/pdf.py`; `main.py` lo inyecta vía `app.state.pdf_renderer`.
  Los módulos nunca importan `app.weber`.
- Contenido contractual en `app/weber/contract_es.py` (portado del generador
  antiguo, con 2 líneas truncadas corregidas). Textos por filial: hoy ES.
- `GET /offers/{id}/pdf`: auth + scope (fuera de ámbito = `404`), idioma no-ES
  = `422` explícito, descarga `application/pdf` (`Offer_<nº>.pdf`).
- Ejecutores por filial (`ES/BNL/DE/AR` + alias de texto libre como
  `España/Deutschland`): probado contra contratos reales ejecutados de las
  4 filiales. Desconocido = `422`, nunca dirección ajena. Calle de AR
  pendiente del dato real.
- Frontend: botón PRINT (descarga el blob tras guardar).
- Dep justificada: `reportlab` (Python puro; `WeasyPrint` exigiría pango/cairo).

## 2. Picker de equipos (`OfferBuilder`)

- Paridad con tu app: listas disponible/seleccionadas desde
  `GET /equipment?customer_id=`, botón añadir al desglose (sin duplicar
  líneas existentes). El cálculo sigue en `/calculate`; la UI no suma nada.
- Etiquetas en los 5 idiomas.

## 3. Dashboard (paridad con mejora)

- Tu Rust: contadores globales sin scope. Aquí: `GET /dashboard`
  (clientes, equipos, ofertas, líneas + top países) **filtrado por filial**.
- Página con tarjetas + top-20 países. Verificado con datos reales
  (2.474 clientes, 42.318 equipos, ~90 países).

## 4. Tests y verificación

- `test_offer_pdf.py` (bytes `%PDF-`, rechazos explícitos, matriz
  `200/404/401`), `test_dashboard.py` (global vs filial).
- Total: **43 passed**, `ruff` limpio, E2E PDF descargado (12,7 KB) y
  dashboard sobre datos reales.

## Herencia

- `generateOfferPdf.ts` no copiado: el contenido vive en backend y los
  totales son los del motor (el JS pintaba el bug `total/totalEnd`).
- Bloque Ibérica hardcodeado del original → tabla `EXECUTORS` por filial.
