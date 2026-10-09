# <Módulo>-<slug> — <Título>

- **Estado**: draft | approved | implemented
- **Módulo**: referencia a `../ALCANCE_MVP.md` (ej. A1, B5, C8)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: quién y cuándo

## Problema

Qué resuelve esta feature para el usuario, en 2-3 líneas.

## Puntos abiertos

Lista de decisiones que todavía no están tomadas (copiar los puntos relevantes de `BACKLOG.md`, sección P0). La spec no puede pasar a `approved` mientras esta lista no esté vacía.

- [ ]

## Requisitos funcionales

Qué tiene que hacer, en lenguaje llano. No implementación.

## Contrato de datos / API

Forma de los datos de entrada/salida relevantes (JSON de ejemplo, endpoints, modelos). No es diseño de base de datos final, es el contrato mínimo para implementar.

## UX / Flujo

Pasos de la pantalla o interacción. Puede ser texto o un link a un diseño.

## Casos de prueba

Se escriben **antes del código** (regla del proyecto: spec → casos de prueba → código). Cada caso en lenguaje simple, con su test automático en `apps/api/tests/test_<spec>.py`.

| # | Caso | Resultado esperado | Test |
|---|---|---|---|
| 1 | | | |

## Criterios de aceptación

Lista chequeable de qué tiene que ser verdad para considerar esto hecho.

- [ ]

## Fuera de alcance

Qué explícitamente no cubre esta spec (para evitar scope creep).
