# Specs

Regla dura del proyecto: **ninguna feature se codifica sin una spec en estado `approved`.**

## Workflow

1. Se crea la spec en estado `draft` a partir de `TEMPLATE.md`.
2. Se resuelven los puntos abiertos que bloqueen (por ahora decide German Villamarin); los que no bloquean se dejan fuera de alcance con un default.
3. Cuando no quedan puntos abiertos, la spec pasa a `approved`.
4. Se implementa. Al mergear la implementación, la spec pasa a `implemented`.

## Convención de nombres

`<módulo>-<slug>.md`, usando el código de módulo de `../ALCANCE_MVP.md` (ej. `A1-datos-natales.md`, `B5-pantalla-descubrir.md`, `C8-invitacion-whatsapp.md`).

## Índice

| Spec | Módulo | Estado |
|---|---|---|
| [A1-datos-natales](./A1-datos-natales.md) | A1 | implemented |
| [A2-ritmo-notificaciones](./A2-ritmo-notificaciones.md) | A2 | implemented |
| [A3-verificacion-identidad](./A3-verificacion-identidad.md) | A3 | implemented (v1 WhatsApp, modo mock; v2 selfie/video pospuesta) |
| [A4-perfil-liviano](./A4-perfil-liviano.md) | A4 | draft |
| [B4-home-tu-momento](./B4-home-tu-momento.md) | B4 | implemented |
| [B5-pantalla-descubrir](./B5-pantalla-descubrir.md) | B5 | implemented |
| [B6-calendario-memoria](./B6-calendario-memoria.md) | B6 | implemented |
| [B7-chat-rompehielos](./B7-chat-rompehielos.md) | B7 | implemented |
| [C8-invitacion-whatsapp](./C8-invitacion-whatsapp.md) | C8 | implemented |

Todas aprobadas para implementación por German Villamarin (2026-10-07). Cada spec dice explícitamente qué queda fuera de alcance de v1.
