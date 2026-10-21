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

## Ampliaciones posteriores (16/10/2026)

### Responsibles (módulo nuevo, migración `0026`)

Corrige lo que decía el alcance real: sí hay gestión de responsibles (los
"técnicos" del plan inicial, la columna Responsible de la oferta).

- `app/modules/responsibles/` (models/schemas/service/router), tabla
  `responsibles`: nombre por filial + `is_active`. Endpoints: `GET` listado
  por filial, `POST` (solo `admin`; duplicado → `409`, filial inexistente →
  `404`), `PATCH`, `DELETE`. Scope ajeno → `404`, sin fugas.
- Frontend: tarjeta **Responsibles** en Configuración → pestaña Rates
  (debajo de las tarifas, con scroll propio); las 3 pestañas originales se
  mantienen. Alta/baja en local y en prod; hoy empieza vacío (pendiente
  dar de alta a David y Xevi Mira en prod).
- Tests: `test_responsibles.py` (servicio) + `test_responsibles_http.py`
  (auth, scope, 409/404) — 14 tests. El patrón HTTP nuevo es
  `monkeypatch` de `dev_auth_enabled` + override de `get_db` + header
  `X-Dev-User`.

### Robustez y UX del frontend

- **Toasts reutilizables** (`components/Toasts.tsx`, `useToasts()`):
  bottom-right, auto-dismiss (4 s éxito/info, 6 s warning, error persiste,
  máx. 4), respeta `prefers-reduced-motion`; migrados Config, OfferBuilder
  y Offers desde sus estados `error/saved/ok/notice` locales.
- **`ErrorBoundary`** envolviendo la app + **probeGate con timeout de 20 s**
  (`AbortController` en `api.ts`): dos pantallas en blanco vividas quedan
  redirigidas a un error legible con botón de reintento en vez de muerte
  silenciosa. Blindaje contra caché de Vercel: Ctrl+Shift+R si el bundle
  viejo queda colgado.
- **Offers con `DataTable`** compartido (TanStack, ordenable por columna) y
  `statusTone.ts` extraído para compartir badges con el builder; gráficos
  lazy con `modulePreload: false` (bundle inicial ~385 kB, charts chunk no
  se descarga hasta abrir la home).
- **Cabecera de oferta 3×3** (Offer no / Guardian Type / Status · Offer date
  / Frequency / Responsible) y **rail derecho** con Guardian Contract Scope
  (flex-1 con scroll interno) + Estimated Costs, fuera del grid de trabajo.
- **Oferta**: fila inferior Comments + Totals (Total Amount en azul), viaje
  desde la ubicación del cliente (selector de sede si el cliente tiene
  varias plantas + lookup de provincia), etiqueta "Audit" → "Inspection"
  (el valor de API sigue siendo `audit`), "Basic Kit" como 4ª opción de
  Guardian Type.
