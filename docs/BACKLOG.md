# BACKLOG

Backlog priorizado de lo que sigue. Se actualiza en cada sesión — ver `CHANGELOG.md` para el historial de qué ya se hizo.

Regla del proyecto: **nada de esto se codifica sin pasar primero por una spec `approved` en `specs/`** (ver `specs/README.md`). Las 8 specs de abajo ya están `approved` (aprobadas por German Villamarin, 2026-10-07) para poder avanzar con la implementación mientras Pablo resuelve los puntos de producto en paralelo — cada spec documenta explícitamente qué quedó fuera de alcance de v1 por eso.

## P0 — Decisiones de producto pendientes de Pablo

Ya **no bloquean** la implementación (las specs correspondientes las dejaron fuera de alcance de v1 con un default o un stub). Cuando Pablo resuelva cada punto, se actualiza la spec afectada y se ajusta la implementación si corresponde.

- [ ] UX de la pantalla de datos natales (spec `A1-datos-natales.md`).
- [ ] Proveedor de KYC/verificación — Persona, Onfido, Veriff o Didit (spec `A3-verificacion-identidad.md` / ADR 0006).
- [ ] Tonos/copies de notificaciones — "Ritmo Diario" vs. "Pulso del Cosmos" (spec `A2-ritmo-notificaciones.md`).
- [ ] Decisión PWA vs. nativo para push notifications en iOS (ver ADR 0002 — afecta a `A2-ritmo-notificaciones.md`).
- [ ] Qué tipos de relación filtrar — pareja/amistad/etc. (spec `B5-pantalla-descubrir.md`, v1 asume un solo contexto: dating).
- [ ] Integración de actividades en el calendario de memoria (spec `B6-calendario-memoria.md`, v1 no las incluye).
- [ ] Tonos/copies del chat y de los rompehielos de IA (spec `B7-chat-rompehielos.md`, v1 usa copy borrador).
- [ ] Estética y visuales del Hub en general (transversal, no bloquea ninguna spec).

## P1 — Implementar Módulo A (onboarding — gatea todo lo demás)

Specs approved, listas para codear:

- [x] `A1-datos-natales.md` — implementado (modelo `Profile`, endpoints `POST /profiles`, `POST /profiles/{id}/birth-data`, `GET /profiles/{id}`, pantalla `/onboarding/datos-natales`).
- [ ] `A2-ritmo-notificaciones.md`.
- [ ] `A3-verificacion-identidad.md` — con adapter mock de KYC (ver ADR 0006).

## P2 — Implementar Módulo B (core loop diario)

- [ ] `B4-home-tu-momento.md`.
- [ ] `B5-pantalla-descubrir.md` — incluye el contrato de datos del JSON que se manda a Claude API (ver ADR 0004).
- [ ] `B6-calendario-memoria.md`.
- [ ] `B7-chat-rompehielos.md`.

## P3 — Implementar Módulo C (growth loop)

- [ ] `C8-invitacion-whatsapp.md` — generador de reporte parcial + link con `ref_id`.

## Tareas técnicas sueltas

- [ ] Confirmar con Pablo si Postgres es el motor definitivo (ADR 0001) antes de modelar el esquema real.
- [ ] El esquema de datos arrancó con `A1` (tabla `profiles`, campos de carta natal). Falta modelar verificación (A3), matches/compatibilidad (B5), chat (B7) e invitaciones (C8) a medida que se implementan.
- [ ] Hoy las tablas se crean con `Base.metadata.create_all` al levantar la API (sin migraciones). Evaluar sumar Alembic antes de tocar esquema en un entorno con datos reales — no es necesario mientras solo haya datos de desarrollo.
