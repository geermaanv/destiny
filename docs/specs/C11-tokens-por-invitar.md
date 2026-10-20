# C11-tokens-por-invitar — Una pregunta diaria más en Indagar por cada amigo que se registra

- **Estado**: implemented
- **Módulo**: C (crecimiento) + X3 (Indagar)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 — reunión de check con Pablo, tanda 4: "se ganan tokens por invitar a otras personas; por ahora son más preguntas en Respuestas", "si viene con 10 y comparte y se registra el amigo, ahora tiene 11 por día".

## Problema

Invitar no tiene recompensa. Indagar tiene un límite diario de preguntas (10) que es lo que más se valora; sumar preguntas por invitar ayuda a viralizar sin cobrar nada (MVP 100 % gratis).

## Puntos abiertos

Ninguno. Defaults: tope de 20 preguntas extra por día (para limitar el abuso con cuentas falsas), configurable.

## Requisitos funcionales

- Por cada amigo que **se registra** a partir de una invitación tuya y la acepta, tu límite diario de Indagar sube en **1 pregunta, para siempre** (10 → 11 por día).
- Cuenta como "se registró" quien creó su perfil **después** de la invitación (si ya tenía cuenta y solo acepta, no suma). Cada persona suma una sola vez aunque haya aceptado varias invitaciones tuyas.
- Tope: 20 preguntas extra por día (`bonus_maximo` en `astrochat_v1.json`).
- Indagar muestra el límite con el extra; en Invitar se explica la recompensa: "Por cada amigo que se registre, sumás una pregunta diaria en Indagar".
- Por ahora los tokens no se ven como saldo: son el límite más alto.

## Contrato de datos / API

- `GET /profiles/{id}/astrochat`: `limite` ya incluye el extra; suma `extra_por_invitados`.
- El límite al preguntar usa el mismo cálculo.
- Configuración: `astrochat_v1.json` → `invitados: {"preguntas_por_invitado": 1, "bonus_maximo": 20}`.

## Casos de prueba (`apps/api/tests/test_c11_tokens_por_invitar.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Sin invitados | Límite 10, extra 0 |
| 2 | Un amigo se registra y acepta | Límite 11; puede hacer la pregunta 11 del día |
| 3 | Invitación sin aceptar | No suma |
| 4 | Ya tenía cuenta antes de la invitación | No suma |
| 5 | La misma persona acepta dos invitaciones | Suma 1 |
| 6 | Tope | Con tope 1 y dos amigos, el extra es 1 |

## Criterios de aceptación

- [x] Los 6 casos pasan.
- [x] Indagar muestra el límite con el extra y la pantalla de Invitar explica la recompensa.

## Fuera de alcance

Saldo de tokens visible, gastarlos en otras cosas, comprar tokens (después del MVP gratis).
