# B11-colores-del-calendario — Cada día con el color de su tipo

- **Estado**: implemented
- **Módulo**: B6 (calendario) y B4 (Hoy, Próximos días)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 (tipos fluye, desafía, intenso y tranquilo; tranquilo en verde suave; "avanzá").

## Problema

El calendario solo marca si un día tiene un tránsito importante, sin decir de qué tipo es. Con colores se ve el mes de un vistazo.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

- Cada día tiene un **tipo**, según el aspecto entre la Luna y tu Sol natal (el mismo cálculo de B6):
  - **Fluye** (celeste): trígono o sextil.
  - **Desafía** (coral): cuadratura u oposición.
  - **Intenso** (violeta): conjunción.
  - **Tranquilo** (verde muy suave): sin aspecto mayor. Es la mayoría de los días: el tinte es apenas visible para que resalten los demás.
- Nombres neutros, no "bueno/malo": Destiny no predice.
- Calendario: el fondo de cada día con su color y una leyenda debajo del mes. Próximos días de Hoy y la lista de eventos del calendario: un punto del color del tipo.

## Contrato de datos / API

- `GET /calendar/{year}/{month}`: cada día suma `tipo` ("fluye" | "desafia" | "intenso" | "tranquilo"). `has_key_transit` sigue (= tipo distinto de tranquilo).
- `GET /calendar/upcoming`: cada evento suma `tipo`.

## Casos de prueba (`apps/api/tests/test_b11_colores_del_calendario.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Tipo de cada día del mes | Coincide con el aspecto del día; tranquilo si y solo si no hay tránsito importante |
| 2 | Eventos próximos | Traen el tipo de su aspecto (nunca tranquilo) |

## Criterios de aceptación

- [x] Los casos pasan.
- [x] Calendario con colores y leyenda; puntos de color en Próximos días y en la lista de eventos.

## Fuera de alcance

Elegir los colores en Tu estilo; tipos según otros planetas.
