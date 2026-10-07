# Specs

Regla dura del proyecto: **ninguna feature se codifica sin una spec en estado `approved`.**

## Workflow

1. Se crea la spec en estado `draft` a partir de `TEMPLATE.md`.
2. Pablo (founder) revisa y resuelve los puntos abiertos (en particular los listados en `../BACKLOG.md`, sección P0).
3. Cuando no quedan puntos abiertos, la spec pasa a `approved`.
4. Se implementa. Al mergear la implementación, la spec pasa a `implemented`.

## Convención de nombres

`<módulo>-<slug>.md`, usando el código de módulo de `../ALCANCE_MVP.md` (ej. `A1-datos-natales.md`, `B5-pantalla-descubrir.md`, `C8-invitacion-whatsapp.md`).

## Índice

| Spec | Módulo | Estado |
|---|---|---|
| [A1-datos-natales](./A1-datos-natales.md) | A1 | implemented |
| [A2-ritmo-notificaciones](./A2-ritmo-notificaciones.md) | A2 | implemented |
| [A3-verificacion-identidad](./A3-verificacion-identidad.md) | A3 | implemented |
| [B4-home-tu-momento](./B4-home-tu-momento.md) | B4 | implemented |
| [B5-pantalla-descubrir](./B5-pantalla-descubrir.md) | B5 | implemented |
| [B6-calendario-memoria](./B6-calendario-memoria.md) | B6 | approved |
| [B7-chat-rompehielos](./B7-chat-rompehielos.md) | B7 | approved |
| [C8-invitacion-whatsapp](./C8-invitacion-whatsapp.md) | C8 | approved |

Todas aprobadas para implementación por German Villamarin (2026-10-07), para desbloquear avance mientras Pablo resuelve los puntos de `../BACKLOG.md` P0 en paralelo. Cada spec dice explícitamente qué queda fuera de alcance de v1 por esos puntos todavía abiertos.
