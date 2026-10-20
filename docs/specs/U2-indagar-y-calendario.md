# U2-indagar-y-calendario — Indagar, una sola caja para preguntar, calendario sin notas

- **Estado**: implemented
- **Módulo**: transversal (web) + B6 (calendario) + X3 (Astrochat)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 — decisiones de la reunión de check con Pablo (`docs/reuniones/2026-10-20-check-pablo.html`), tanda 1.

## Problema

"Respuestas" no termina de transmitir que ahí se busca claridad; la caja para preguntar tiene un título distinto en cada pantalla; el calendario muestra si un día es importante pero no deja entender por qué; y las notas del día suman complejidad sin uso claro.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

1. **Indagar**: la pestaña "Respuestas" pasa a llamarse **Indagar** (barra: Hoy · Carta · Indagar · Círculo · Perfil) y la pantalla se titula igual.
2. **Una sola caja**: en Hoy, Tu día, Carta e Indagar la caja para preguntar se titula **"¿En qué necesitás claridad hoy?"**.
3. **Consultar un día**: en el detalle de un día del calendario, el link "Indagar sobre este día →" abre Indagar con la pregunta precargada (sin enviar) — "¿Qué significa para mí el jueves 23 de octubre?" — para que la persona la ajuste y la mande. Al mandarla, la IA recibe además los datos de **ese día** (Luna, tránsitos y áreas, igual que "Tu día"), así puede explicar por qué es un buen o mal día. No se agrega en "Próximos días" de Hoy.
4. **Sin notas**: se sacan las notas del calendario de todos lados (pantalla, API y datos ya guardados). El registro de ánimo se queda. Queda en el BACKLOG como posible función futura.

## Contrato de datos / API

- `POST /profiles/{id}/astrochat` acepta `dia` opcional (`YYYY-MM-DD`): suma `dia_consultado` a los datos que ve la IA (sin datos personales, como el resto).
- Se eliminan `POST /calendar/day/{day}/annotations`, `annotations` del detalle del día y `has_notes` de los próximos eventos. Se borra la tabla `calendar_annotations`.
- Web: `/astrochat?q=…&dia=YYYY-MM-DD` precarga la pregunta y manda `dia` al enviarla.

## Casos de prueba (`apps/api/tests/test_u2_indagar_y_calendario.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Las notas ya no existen | Crear una nota → 404 o 405; el detalle del día no trae `annotations`; los eventos no traen `has_notes` |
| 2 | Preguntar por un día | Con `dia`, la IA recibe `dia_consultado` con la fecha y sus tránsitos |
| 3 | Sin `dia` | No hay `dia_consultado` |
| 4 | `dia` inválido | 422 |

## Criterios de aceptación

- [x] Los 4 casos pasan; los tests de notas de B6 y de robustez se quitan.
- [x] Barra y pantalla dicen "Indagar"; las cuatro cajas dicen "¿En qué necesitás claridad hoy?".
- [x] El link del calendario precarga la pregunta.

## Fuera de alcance

Volver a tener notas (BACKLOG).

**Ajuste (2026-10-20, German)**: el link "Indagar sobre este día →" ya no deja la pregunta precargada para enviar: la manda sola (como desde Hoy y Tu día), con los datos de ese día.

**Ajuste (2026-10-20, German)**: también cada día de "Próximos días" en Hoy tiene "Indagar sobre este día →" (en la reunión se había dicho que no; German lo pidió al probarlo). El armado de la pregunta está en `lib/indagar.ts`.
