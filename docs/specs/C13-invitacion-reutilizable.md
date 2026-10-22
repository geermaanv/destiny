# C13-invitacion-reutilizable — Un link de invitación sirve para varias personas

- **Estado**: implemented
- **Módulo**: C (crecimiento); cambia C8 y C11
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-22 (bug: una amiga suya se registró con un link de Pablo y quedó en "Solicitud fallida").

## Problema

Cada invitación servía para una sola persona. Pablo mandó un link que se reenvió: la primera persona quedó conectada y las otras tres (Iñaki, Miguel W., Carla) se registraron pero, al final, la API respondió "esta invitación ya la usó otra persona" y la app se quedó en una pantalla de error, sin entrar y sin conectarlas.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

- **El link sirve para varias personas**: cada una que se registra y acepta queda conectada con quien invitó (su propio chat, con rompehielos).
- Aceptar dos veces la misma persona no duplica nada.
- La pregunta extra de Indagar (C11) suma por cada persona distinta que se registró con tus links.
- "Mis invitaciones" informa cuántas personas aceptaron cada link.
- **Si conectar falla igual se entra a la app** (Hoy) con un aviso, sin trabarse en una pantalla de error.

## Contrato de datos / API

- Tabla `invitation_acceptances` (`ref_id`, `invitee_profile_id`, `accepted_at`). `Invitation.invitee_profile_id` queda como la primera persona (compatibilidad).
- `POST /invitations/{ref}/accept` ya no responde 409 "ya la usó otra persona".
- `GET /invitations/mine` suma `aceptaron: int`.

## Casos de prueba (`apps/api/tests/test_c13_invitacion_reutilizable.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Dos personas usan el mismo link | Las dos quedan conectadas con quien invitó, cada una con su chat |
| 2 | La misma persona acepta dos veces | Misma conexión, sin duplicar |
| 3 | Pregunta extra | Suma por cada una (dos personas → +2) |
| 4 | Mis invitaciones | `aceptaron` = 2 |

## Criterios de aceptación

- [x] Los casos pasan.
- [x] El paso final del registro entra a la app aunque conectar falle.

## Fuera de alcance

Link personal fijo por persona (C9), límite de usos por link.
