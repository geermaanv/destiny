# R2-concurrencia-y-flujos — Sin duplicados, límites que se respetan y conexiones que no se traban

- **Estado**: implemented
- **Módulo**: B7 (conexiones), X3 (Indagar), A12 (privacidad), C13 (invitaciones)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-22 ("arrancá por todo"), a partir del informe del agente breaker (hallazgos 5 a 9).

## Problema

- Pedidos simultáneos creaban varias conexiones (y chats) entre las mismas dos personas, y pasaban el límite diario de Indagar (15 preguntas con límite 10, con gasto de IA).
- Registrándose por WhatsApp se salteaba el aviso de privacidad, y la API aceptaba cualquier "versión" del aviso.
- Aceptar una invitación no conectaba si ya había una solicitud pendiente o rechazada entre los dos.
- Una conexión rechazada quedaba trabada para siempre, y quien había pedido se enteraba del rechazo.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

1. **Una sola conexión por par**: pedidos simultáneos (en cualquier dirección) terminan en una sola conexión.
2. **El límite diario de Indagar se respeta** aunque lleguen muchas preguntas a la vez.
3. **Privacidad antes de verificar**: para pedir el código de WhatsApp de un perfil que todavía no terminó el registro, tiene que haber aceptado el aviso (409 si no). La versión del aviso tiene que ser una vigente (`privacidad_v1`); otra → 422.
4. **La invitación conecta igual**: si entre los dos ya había una solicitud pendiente o rechazada, aceptar la invitación la acepta (con su rompehielos). Un bloqueo no se levanta.
5. **Rechazo sin trabas ni avisos**:
   - Si quien rechazó después pide conexión, se conectan (los dos lo quisieron).
   - Quien fue rechazado sigue viendo su pedido como "pendiente" (no se entera del rechazo), y volver a pedir no cambia nada.

## Casos de prueba (`apps/api/tests/test_r2_concurrencia_y_flujos.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | 10 pedidos de conexión a la vez, en las dos direcciones | Una sola conexión |
| 2 | 20 preguntas a Indagar a la vez con límite 3 | Exactamente 3 aceptadas |
| 3 | Pedir código de WhatsApp sin aceptar el aviso | 409; versión inventada del aviso → 422 |
| 4 | Invitación con solicitud pendiente o rechazada previa | Quedan conectados |
| 5 | Quien rechazó pide conexión | Quedan conectados |
| 6 | Quien fue rechazado | Ve "pendiente" y volver a pedir no cambia nada |

## Criterios de aceptación

- [x] Los casos pasan.

## Fuera de alcance

Límite de cuentas por dispositivo (hallazgo 14, por diseño con tope 20).
