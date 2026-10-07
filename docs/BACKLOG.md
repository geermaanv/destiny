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
- [x] `A2-ritmo-notificaciones.md` — implementado (`notification_rhythm` en `Profile`, endpoint `POST /profiles/{id}/notification-preference`, pantalla `/onboarding/ritmo-notificaciones`).
- [x] `A3-verificacion-identidad.md` — implementado (adapter mock de KYC en `app/adapters/kyc.py`, endpoints `POST`/`GET /profiles/{id}/verification`, pantalla `/onboarding/verificacion`). Onboarding completo A1→A2→A3 encadenado y validado end-to-end.

## P2 — Implementar Módulo B (core loop diario)

- [x] `B4-home-tu-momento.md` — implementado (`app/astro.py` con `astronomy-engine` real para fase lunar + signo, `MoodCheckin`, endpoints `/home/today`, `/home/frequency-count`, `/mood-checkins`, pantalla `/home`).
- [x] `B5-pantalla-descubrir.md` — implementado. `app/compatibility.py` (aspecto Sol-Sol real vía `astronomy-engine`, simplificación v1 — ver nota abajo), `app/explainer.py` (adapter: `ClaudeResonanceExplainer` si hay `ANTHROPIC_API_KEY`, si no `MockResonanceExplainer` con copy borrador), endpoints `GET /discover` y `GET /discover/{id}/explanation`, pantalla `/discover`. Gating por verificación ya aplicado (ver abajo).
- [x] `B6-calendario-memoria.md` — implementado. `app/aspects.py` extrae la clasificación de aspectos compartida con `B5`; `app/transits.py` calcula Luna del día vs. Sol natal del usuario (simplificación v1, mismo criterio que `B5`). Modelo `CalendarAnnotation`. Endpoints `GET /calendar/{year}/{month}`, `GET /calendar/day/{day}`, `POST /calendar/day/{day}/annotations`. Pantalla `/calendario` (grilla mensual + anotaciones).
- [ ] `B7-chat-rompehielos.md`.

## P3 — Implementar Módulo C (growth loop)

- [ ] `C8-invitacion-whatsapp.md` — generador de reporte parcial + link con `ref_id`.

## Tareas técnicas sueltas

- [ ] Confirmar con Pablo si Postgres es el motor definitivo (ADR 0001) antes de modelar el esquema real.
- [x] Esquema de datos: `profiles` ya tiene carta natal (A1), ritmo de notificaciones (A2) y verificación (A3). Falta modelar matches/compatibilidad (B5), chat (B7) e invitaciones (C8) a medida que se implementan.
- [x] Gating real de `/discover` según `verification_status` — implementado en `B5-pantalla-descubrir.md` (`_require_verified_profile`, 403 si no verificado).
- [ ] Hoy las tablas se crean con `Base.metadata.create_all` al levantar la API (sin migraciones). Evaluar sumar Alembic antes de tocar esquema en un entorno con datos reales — no es necesario mientras solo haya datos de desarrollo.
- [ ] `ANTHROPIC_API_KEY` no está configurada en ningún entorno todavía — `app/explainer.py` usa `MockResonanceExplainer` (copy borrador, no LLM real). Cuando Pablo/German tengan la key, se agrega a `.env` y el adapter cambia solo con eso, sin tocar código (ver `app/explainer.py::get_explainer`).
- [ ] `app/compatibility.py` calcula compatibilidad solo con el aspecto Sol-Sol (simplificación v1, documentada en el código). Una carta completa (Luna, Venus, Marte, ascendente) da una señal más rica — evaluar si vale la pena antes de sumar más signos al cálculo.
