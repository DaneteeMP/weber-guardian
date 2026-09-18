# ADR-002 — Autenticación Entra + autorización en Guardian DB

## Estado

Aceptado (F2).

## Contexto

Guardian acabará integrado en SharePoint/Microsoft 365. Construir un login propio (passwords, bcrypt, JWT internos) para eliminarlo después es trabajo tirado y superficie de seguridad extra.

## Decisión

- **Microsoft/Entra autentica** (quién es). Clave de enlace: `users.external_id` = oid Entra (estable ante cambios de email).
- **Guardian DB autoriza** (qué puede, sobre qué): `users.role` + `users.subsidiary_id` (`NULL` = global). Nunca resolver permisos solo desde claims del JWT.
- **Sin login propio**: sin `Login.tsx`, sin passwords/hashes, sin dependencias de auth que retirar después. Cero deps nuevas en F2.
- **Costura `get_current_user()`**: hoy resuelve vía mock dev (`X-Dev-User` + `DEV_AUTH_ENABLED`, solo local); en producción valida identidad Microsoft. Routers y servicios no cambian cuando llegue.
- **Fallback seguro**: sin identidad → `401`; fuera de ámbito → `404` (no `403` que confirme existencia).

## Alternativas descartadas

- Login propio con bcrypt+JWT: descartado (duplica a Entra, hay que borrarlo en la integración).
- Scope solo con claims del token: descartado (los permisos son dato Guardian y cambian sin reemitir tokens).

## Consecuencias

- Altas de usuarios fuera de banda (seed dev + insert) hasta el CRUD admin (F4).
- `DEV_AUTH_ENABLED` jamás en `true` en producción.
- i18n en 5 idiomas (`ES/EN/DE/PT/IT`), italiano añadido a petición.
