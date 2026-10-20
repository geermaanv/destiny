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
| [A6-test-personalidad](./A6-test-personalidad.md) | A6 | implemented |
| [B4-home-tu-momento](./B4-home-tu-momento.md) | B4 | implemented |
| [B5-pantalla-descubrir](./B5-pantalla-descubrir.md) | B5 | implemented |
| [B5-motor-sinastria](./B5-motor-sinastria.md) | B5 | superseded por A7 |
| [B6-calendario-memoria](./B6-calendario-memoria.md) | B6 | implemented |
| [B7-chat-rompehielos](./B7-chat-rompehielos.md) | B7 | implemented (v2 híbrida) |
| [C8-invitacion-whatsapp](./C8-invitacion-whatsapp.md) | C8 | implemented |
| [X1-redaccion-con-ia](./X1-redaccion-con-ia.md) | X1 (transversal) | approved |

Todas aprobadas para implementación por German Villamarin (2026-10-07). Cada spec dice explícitamente qué queda fuera de alcance de v1.
| [X2-hiperpersonalizacion](./X2-hiperpersonalizacion.md) | X2 (transversal) | implemented |
| [A7-motor-oficial-destiny-1-0](./A7-motor-oficial-destiny-1-0.md) | B5 (motor) | implemented |
| [A8-mi-carta-dimensiones](./A8-mi-carta-dimensiones.md) | A (autoconocimiento) | implemented |
| [U1-reorganizacion-ui](./U1-reorganizacion-ui.md) | transversal (web) | implemented |
| [A9-compartir-mi-carta](./A9-compartir-mi-carta.md) | A (autoconocimiento) | implemented |
| [X3-astrochat](./X3-astrochat.md) | X3 (transversal) | implemented |
| [A10-verificacion-opcional](./A10-verificacion-opcional.md) | A (verificación y sesión) | implemented |
| [A11-fotos](./A11-fotos.md) | A4 / B5 | implemented |
| [B8-filtros-descubrir](./B8-filtros-descubrir.md) | B5 | implemented |
| [B9-circulo-v2](./B9-circulo-v2.md) | B5 | implemented |
| [B10-filtros-activos-intereses](./B10-filtros-activos-intereses.md) | B5 | implemented |
| [U2-indagar-y-calendario](./U2-indagar-y-calendario.md) | transversal + B6 + X3 | implemented |
| [A12-privacidad-y-orden-del-test](./A12-privacidad-y-orden-del-test.md) | A + A6 | implemented |
| [C11-tokens-por-invitar](./C11-tokens-por-invitar.md) | C + X3 | implemented |
| [C12-invitar-simple](./C12-invitar-simple.md) | C (simplifica C8) | implemented |
| [B11-colores-del-calendario](./B11-colores-del-calendario.md) | B6 + B4 | implemented |
