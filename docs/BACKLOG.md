# BACKLOG

Backlog priorizado de lo que sigue. Se actualiza en cada sesión — ver `CHANGELOG.md` para el historial de qué ya se hizo.

Regla del proyecto: **nada de esto se codifica sin pasar primero por una spec `approved` en `specs/`** (ver `specs/README.md`).

## P0 — Decisiones del founder que bloquean escribir specs

Sin esto, las specs de los módulos correspondientes no pueden pasar de `draft` a `approved`. Ver detalle de cada punto en `ALCANCE_MVP.md`.

- [ ] UX de la pantalla de datos natales (Módulo A1).
- [ ] Proveedor de KYC/verificación — Persona, Onfido, Veriff o Didit (Módulo A3 / ADR 0006).
- [ ] Tonos/copies de notificaciones — "Ritmo Diario" vs. "Pulso del Cosmos" (Módulo A2).
- [ ] Decisión PWA vs. nativo para push notifications en iOS (ver ADR 0002 — afecta directamente a A2).
- [ ] Qué tipos de relación filtrar — pareja/amistad/etc. (Módulo B5).
- [ ] Integración de actividades en el calendario de memoria (Módulo B6).
- [ ] Tonos/copies del chat y de los rompehielos de IA (Módulo B7).
- [ ] Estética y visuales del Hub en general.

## P1 — Specs a escribir (Módulo A, onboarding — gatea todo lo demás)

- [ ] `A1-datos-natales.md` — bloqueada por UX pendiente.
- [ ] `A2-ritmo-notificaciones.md` — bloqueada por decisión PWA/nativo + copies.
- [ ] `A3-verificacion-identidad.md` — bloqueada por elección de vendor KYC.

## P2 — Specs a escribir (Módulo B, core loop diario)

- [ ] `B4-home-tu-momento.md`.
- [ ] `B5-pantalla-descubrir.md` — incluye el contrato de datos del JSON que se manda a Claude API (ver ADR 0004). Bloqueada parcialmente por tipos de relación a filtrar.
- [ ] `B6-calendario-memoria.md` — bloqueada por integración de actividades.
- [ ] `B7-chat-rompehielos.md` — bloqueada por copies/tono.

## P3 — Specs a escribir (Módulo C, growth loop)

- [ ] `C8-invitacion-whatsapp.md` — generador de reporte parcial + link con `ref_id`.

## Tareas técnicas sueltas (no bloqueadas por decisiones de producto)

- [ ] Validar que `apps/api` levanta con venv + `uvicorn` y responde `/health` (scaffold recién creado, falta probar end-to-end).
- [ ] Confirmar con Pablo si Postgres es el motor definitivo (ADR 0001) antes de modelar el esquema real.
