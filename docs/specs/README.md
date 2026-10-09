# Specs

Regla dura del proyecto: **spec → casos de prueba → código.** Ninguna feature se codifica sin una spec `approved` y sin sus casos de prueba escritos antes.

## Workflow

1. Se crea la spec en estado `draft` a partir de `TEMPLATE.md`.
2. Se resuelven los puntos abiertos que bloqueen (por ahora decide German Villamarin); los que no bloquean se dejan fuera de alcance con un default.
3. Cuando no quedan puntos abiertos, la spec pasa a `approved`.
4. **Casos de prueba**: se completa la sección "Casos de prueba" de la spec y se escriben los tests automáticos en `apps/api/tests/test_<spec>.py`. Tienen que fallar antes de programar.
5. Se implementa hasta que los tests pasen (`cd apps/api && .venv/bin/pytest`). La spec pasa a `implemented`.

## Convención de nombres

`<módulo>-<slug>.md`, usando el código de módulo de `../ALCANCE_MVP.md` (ej. `A1-datos-natales.md`, `B5-pantalla-descubrir.md`, `C8-invitacion-whatsapp.md`).

## Índice

| Spec | Módulo | Estado |
|---|---|---|
| [A1-datos-natales](./A1-datos-natales.md) | A1 | implemented |
| [A2-ritmo-notificaciones](./A2-ritmo-notificaciones.md) | A2 | implemented |
| [A3-verificacion-identidad](./A3-verificacion-identidad.md) | A3 | implemented (v1 WhatsApp, modo mock; v2 selfie/video pospuesta) |
| [A4-perfil-liviano](./A4-perfil-liviano.md) | A4 | implemented |
| [A5-sesion](./A5-sesion.md) | A5 | implemented |
| [B4-home-tu-momento](./B4-home-tu-momento.md) | B4 | implemented |
| [B5-pantalla-descubrir](./B5-pantalla-descubrir.md) | B5 | implemented |
| [B5-motor-sinastria](./B5-motor-sinastria.md) | B5 | implemented (tablas v1-provisoria) |
| [B6-calendario-memoria](./B6-calendario-memoria.md) | B6 | implemented |
| [B7-chat-rompehielos](./B7-chat-rompehielos.md) | B7 | implemented (v2 híbrida) |
| [C8-invitacion-whatsapp](./C8-invitacion-whatsapp.md) | C8 | implemented |

Todas aprobadas para implementación por German Villamarin (2026-10-07). Cada spec dice explícitamente qué queda fuera de alcance de v1.
