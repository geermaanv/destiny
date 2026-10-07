# BACKLOG

Backlog priorizado de lo que sigue. Se actualiza en cada sesión — ver `CHANGELOG.md` para el historial de qué ya se hizo.

Regla del proyecto: **nada de esto se codifica sin pasar primero por una spec `approved` en `specs/`** (ver `specs/README.md`). Las 8 specs de abajo ya están `approved` (aprobadas por German Villamarin, 2026-10-07) para poder avanzar con la implementación mientras Pablo resuelve los puntos de producto en paralelo — cada spec documenta explícitamente qué quedó fuera de alcance de v1 por eso.

## P0 — Decisiones de producto pendientes de Pablo

Ya **no bloquean** la implementación (las specs correspondientes las dejaron fuera de alcance de v1 con un default o un stub). Cuando Pablo resuelva cada punto, se actualiza la spec afectada y se ajusta la implementación si corresponde.

- [ ] UX de la pantalla de datos natales (spec `A1-datos-natales.md`).
- [ ] Confirmar el cambio de verificación a WhatsApp para v1, con selfie/video en vivo pospuesta a v2 (spec `A3-verificacion-identidad.md` / ADR 0008).
- [ ] Número dedicado de WhatsApp para Destiny y titular de la cuenta de Meta Business (operativo; el desarrollo avanza en modo mock).
- [ ] Proveedor de KYC/verificación para **v2** — Persona, Onfido, Veriff o Didit (spec `A3-verificacion-identidad.md` / ADR 0006). Ya no bloquea v1.
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
- [ ] `A3-verificacion-identidad.md` **v1 WhatsApp** — a implementar: `phone_e164` + `verification_method` en `Profile`, tabla `phone_verification_codes`, `POST /profiles/{id}/verification/whatsapp`, webhook `GET`/`POST /webhooks/whatsapp` (con modo mock en desarrollo), pantalla `/onboarding/verificacion` con link `wa.me` + polling.
- [x] `A3-verificacion-identidad.md` (versión original, selfie/video) — implementado con mock (adapter mock de KYC en `app/adapters/kyc.py`, endpoints `POST`/`GET /profiles/{id}/verification`, pantalla `/onboarding/verificacion`). Onboarding completo A1→A2→A3 encadenado y validado end-to-end.

## P2 — Implementar Módulo B (core loop diario)

- [x] `B4-home-tu-momento.md` — implementado (`app/astro.py` con `astronomy-engine` real para fase lunar + signo, `MoodCheckin`, endpoints `/home/today`, `/home/frequency-count`, `/mood-checkins`, pantalla `/home`).
- [x] `B5-pantalla-descubrir.md` — implementado. `app/compatibility.py` (aspecto Sol-Sol real vía `astronomy-engine`, simplificación v1 — ver nota abajo), `app/explainer.py` (adapter: `ClaudeResonanceExplainer` si hay `ANTHROPIC_API_KEY`, si no `MockResonanceExplainer` con copy borrador), endpoints `GET /discover` y `GET /discover/{id}/explanation`, pantalla `/discover`. Gating por verificación ya aplicado (ver abajo).
- [x] `B6-calendario-memoria.md` — implementado. `app/aspects.py` extrae la clasificación de aspectos compartida con `B5`; `app/transits.py` calcula Luna del día vs. Sol natal del usuario (simplificación v1, mismo criterio que `B5`). Modelo `CalendarAnnotation`. Endpoints `GET /calendar/{year}/{month}`, `GET /calendar/day/{day}`, `POST /calendar/day/{day}/annotations`. Pantalla `/calendario` (grilla mensual + anotaciones).
- [x] `B7-chat-rompehielos.md` — implementado. `app/icebreaker.py`: tercer adapter con el mismo patrón que KYC/explainer (mock sin `ANTHROPIC_API_KEY`, Claude real con ella). Modelos `Match`/`ChatMessage`. Endpoints `POST /matches` (crea el match + genera e inserta el icebreaker automáticamente), `GET`/`POST /chats/{match_id}/messages`. Pantalla `/chat/[matchId]`, con botón "Match" agregado a `/discover` para completar el flujo.

## P3 — Implementar Módulo C (growth loop)

- [x] `C8-invitacion-whatsapp.md` — implementado. Modelo `Invitation`. `POST /invitations` (teaser aproximado por signo solar únicamente — `approximate_longitude_for_sign`, punto medio del signo; `locked_fields` explícitos), `GET /invitations/{ref_id}` (preload del invitado), `GET /invitations/{ref_id}/reveal` (compatibilidad real una vez que el invitado completa su carta). Pantallas `/invitar` y `/onboarding/invitacion`; `ref` se encadena por todo el onboarding (A1→A2→A3) y la revelación real se muestra al verificarse. **Con esto, los 8 módulos del MVP están implementados.**

## Tareas técnicas sueltas

- [ ] Confirmar con Pablo si Postgres es el motor definitivo (ADR 0001) antes de modelar el esquema real.
- [x] Esquema de datos: `profiles` (A1-A3), `MoodCheckin`/`CalendarAnnotation` (B4/B6), `Match`/`ChatMessage` (B7). Falta modelar invitaciones (C8).
- [x] Gating real de `/discover` según `verification_status` — implementado en `B5-pantalla-descubrir.md` (`_require_verified_profile`, 403 si no verificado).
- [ ] Hoy las tablas se crean con `Base.metadata.create_all` al levantar la API (sin migraciones). Evaluar sumar Alembic antes de tocar esquema en un entorno con datos reales — no es necesario mientras solo haya datos de desarrollo.
- [ ] `ANTHROPIC_API_KEY` no está configurada en ningún entorno todavía — `app/explainer.py` (B5) y `app/icebreaker.py` (B7) corren en modo mock. Cuando Pablo/German tengan la key, se agrega a `.env` y ambos adapters cambian solo con eso, sin tocar código.
- [ ] `app/compatibility.py` calcula compatibilidad solo con el aspecto Sol-Sol (simplificación v1, documentada en el código). Una carta completa (Luna, Venus, Marte, ascendente) da una señal más rica — evaluar si vale la pena antes de sumar más signos al cálculo.
- [x] Hosting para que Pablo vea el avance — resuelto por ahora: MacBook Air de German + túnel `ngrok`, con proxy de `apps/web` a la API para que un solo túnel alcance (ver ADR `0007-hosting-local-tunel.md`, incluye el runbook). Ejecutarlo requiere una sesión de Claude Code **local** en esa Mac (esta sesión cloud no tiene acceso a esa máquina). No reemplaza una decisión de hosting real para usuarios fuera del equipo.
- [ ] Las dependencias de `apps/api/requirements.txt` están fijadas a versiones que no soportan Python 3.14 (hoy se usa 3.12). Evaluar actualizarlas (confirmar con Pablo antes, regla de dependencias) o fijar la versión de Python en el repo (`.python-version`).
- [ ] Cuando se corra el runbook de la ADR 0007, setear `WEB_BASE_URL` en `apps/api/.env` a la URL de `ngrok` del momento, para que el link de invitación de `C8-invitacion-whatsapp.md` sea válido desde afuera (si no, sigue apuntando a `localhost:3000`).
