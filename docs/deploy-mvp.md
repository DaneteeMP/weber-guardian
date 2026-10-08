# Despliegue de la demo publica (MVP)

Objetivo: una URL que se pueda enseñar sin depender de la red de la oficina.
Stack: **Supabase** (Postgres) + **Render** (API) + **Vercel** (frontend). Todo
el codigo sigue siendo el mismo de `docker-compose`: lo unico que cambia son
variables de entorno y quien hospeda cada pieza.

## 0. Decision previa: la puerta de acceso

No hay login real todavia (Entra/SharePoint es F2, ver `ADR-002-entra-auth.md`).
Mientras tanto la demo se protege con **HTTP Basic en la API**:
`BASIC_AUTH_USER` + `BASIC_AUTH_PASSWORD`. Con ambos vacios la puerta queda
desactivada, que es el comportamiento por defecto en local.

El frontend **pide la contraseña dentro de la app** (`components/Gate.tsx`), la
guarda en `sessionStorage` y la envia en cada llamada. No hay proxy delante ni
secreto en el bundle: Vercel solo sirve HTML/JS.

Consecuencia asumida: con la puerta abierta, `DEV_AUTH_ENABLED=true` deja que
cualquiera elija identidad (`X-Dev-User`). Es aceptable para una demo tras una
contraseña compartida y **no** es una postura de produccion.

## 1. Supabase (base de datos)

1. Crear un proyecto y copiar la cadena del **pooler** ("Transaction pooler",
   puerto 6543):
   `postgresql+psycopg://USER:PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres?sslmode=require`.
   El pooler abre conexiones mucho mas rapido que la directa (5432), y eso es lo
   que hacia que la primera carga tardase varios segundos: cada recarga pagaba
   el establecimiento de la conexion TLS. El backend ya desactiva las sentencias
   preparadas del servidor (`prepare_threshold=None`), que el pooler en modo
   transaccion no soporta. La conexion directa tambien sigue valiendo, pero es
   mas lenta de abrir.
2. Crear el schema ejecutando las migraciones **una sola vez**, contra esa
   cadena de conexion:
   ```
   docker compose run --rm -e DATABASE_URL="postgresql+psycopg://.../postgres?sslmode=require" api alembic upgrade head
   ```
   El contenedor de Render no lanza migraciones al arrancar (no hay migraciones
   automaticas en el plan gratuito), por eso se hace aqui y a mano.
3. Identidades: la app todavia no tiene login real y arranca como `dev-admin`,
   asi que **siempre** hacen falta los usuarios dev:
   ```
   docker compose run --rm -e DATABASE_URL="postgresql+psycopg://.../postgres?sslmode=require" api python seed_dev.py
   ```
4. Datos de ejemplo (opcional). Solo si quieres una demo con datos inventados
   (clientes y ofertas); para una instancia vacia que vayas a importar tu, se
   salta este paso:
   ```
   docker compose run --rm -e DATABASE_URL="postgresql+psycopg://.../postgres?sslmode=require" api python seed_demo.py
   ```
   `seed_demo.py` se niega a ejecutarse si la tabla `offers` ya tiene filas, de
   modo que la base de desarrollo con datos reales no se puede contaminar.

### Si la red local no llega a Supabase

En algunas redes (sobre todo detras de VPN o con DNS filtrado) el host de
Supabase solo resuelve a IPv6 y el puerto 5432 no es alcanzable, asi que los
tres comandos de arriba no se pueden ejecutar desde el equipo. La salida la tiene
el propio servicio de Render, y para eso esta `bootstrap_demo.py`: migra y
siembra en un solo comando.

1. En Render, servicio `weberguardian-api` -> **Settings** -> **Docker Command**:
   - Instancia **vacia** (solo esquema + usuarios dev, sin clientes/ofertas):
     ```
     python bootstrap.py
     ```
   - Demo **con** datos inventados (anade clientes y ofertas):
     ```
     python bootstrap_demo.py
     ```
   Ese campo acepta **un unico ejecutable, sin operadores de shell**: escribir
   `sh -c "a && b && c"` falla con `not found`.
2. Guardar y esperar el reinicio. En **Logs** deben aparecer `--- alembic
   upgrade head ---`, `users: 4 created` y `bootstrap finished` (con
   `bootstrap.py`) o ademas `offers: 24 across 8 customers` (con
   `bootstrap_demo.py`). El contenedor acaba en `Exited`, y es lo esperado: el
   script solo prepara datos, no arranca el servidor.
3. **Volver a vaciar el Docker Command** y guardar, para que arranque el CMD
   normal con uvicorn.

Repetir el bootstrap no duplica nada: `alembic upgrade head` solo aplica lo que
falta, `seed_dev.py` se salta las filas existentes y `bootstrap_demo.py`
detecta que ya hay ofertas en vez de depender del codigo de salida de
`seed_demo.py`.

## 2. Render (API)

1. New > Blueprint, apuntando al repositorio. Render lee `render.yaml`
   (que ya fija `region: frankfurt`). Pon el servicio en la **misma region/continente
   que Supabase**: cada consulta viaja Render -> Supabase, y si cruzan el Atlantico
   cada round-trip suma ~0,4 s. Con Supabase en Irlanda, la region EU de Render es
   Frankfurt (~20-30 ms). No se puede cambiar la region de un servicio ya creado:
   hay que borrarlo y recrearlo.
2. Completar las variables `sync: false` en el panel:
   - `DATABASE_URL`: la de Supabase del paso 1.
   - `BASIC_AUTH_USER` / `BASIC_AUTH_PASSWORD`: la contraseña de la demo. Solo
     ASCII, el frontend la codifica con `btoa`.
   - `ALLOWED_ORIGINS`: `https://<tu-app>.vercel.app` (coma si hay mas de uno).
3. `DEV_AUTH_ENABLED` va a `true` en el blueprint; ver la nota del paso 0.
4. Health check: `/health` responde 200 sin credenciales, asi que la plataforma
   no la bloquea.
5. Comprobar: `https://<api>.onrender.com/openapi.json` pide `WWW-Authenticate:
   Basic` y con la contraseña devuelve 200.

Aviso: el plan gratuito duerme tras unos minutos de inactividad, asi que la
primera peticion tras un rato tarda 30-60 s. Con una instancia de pago no pasa.
Se puede evitar el imprevisto de la demo dejando el plan gratuito y aceptando
la espera, o pasando a `starter`.

### Evitar el cold start (plan gratuito)

Cada vez que la instancia se duerme, la primera carga paga el arranque **y** la
apertura de conexiones TLS contra Supabase (varios segundos, una sola vez). Para
evitarlo sin pagar, un cron externo (cron-job.org, UptimeRobot) debe llamar cada
~10 min a:

```
https://weberguardian-api.onrender.com/warmup
```

`/warmup` no pide credenciales y ademas ejecuta un `SELECT 1`, asi que mantiene
despierta la instancia **y** con la conexion a la base ya abierta. Con eso la
carga de las peticiones de la app baja a lo normal (cientos de ms). `/health`
sirve solo para despertar; `/warmup` es el que conviene pings.

## 3. Vercel (frontend)

1. New Project, importar el repositorio y poner **Root Directory = `frontend`**
   (Vite se detecta solo: `npm run build` -> `dist`). No hace falta `vercel.json`.
2. Variable de entorno del build:
   - `VITE_API_BASE=https://<api>.onrender.com/api/v1` (sin barra final).
3. Desplegar. Al abrir la URL aparece la pantalla de acceso pidiendo usuario y
   contraseña de la demo.

## 4. Comprobacion final

- `pytest` y `ruff check` en verde en local (el gate tiene tests en
  `tests/test_security.py`).
- Abrir la URL de Vercel: pide contraseña, entra, y los tres graficos de la
  home tienen datos (donut por estado, barras por mes, ranking de clientes).
- Crear una oferta y comprobar que la fecha se puede editar y que el PDF sale.

## 5. Lo que hay que tener presente

- Sin login real: la puerta Basic es lo unico entre Internet y los datos.
- `BASIC_AUTH_PASSWORD` vive en el panel de Render y en el navegador de quien
  se autentique (`sessionStorage`, se borra al cerrar la pestaña).
- La demo expone datos inventados de `seed_demo.py`, no los clientes reales.
- Render gratuito duerme; Vercel y Supabase no.
