# R3-breaker-segunda-corrida — Bloqueo sin fugas, Círculo rápido y cierre de sesión real

- **Estado**: implemented
- **Módulo**: B7 (conexiones), C13 (invitaciones), B5/B9 (Descubrir), A5/A10 (sesión), A3 (duplicados)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-22, a partir de la segunda corrida del agente breaker (respuestas punto por punto: 2 a 8 "ok"; "Dónde vivís" una vez por mes; invitaciones de varios usos con el bloqueo cortando todo).

## Problema

La segunda corrida del agente breaker encontró: el bloqueo se salteaba por las invitaciones y por la ficha de la conexión; la explicación con IA recibía el test incompleto; Círculo tardaba casi 2 s con 200 perfiles (y 30 s con varios usuarios a la vez); los límites de ubicación y del test y el aceptar/rechazar no aguantaban pedidos simultáneos; "seguir con mi cuenta" podía dar error; cerrar sesión no cerraba en un navegador compartido; y un link reenviado pasaba por encima de un rechazo.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

1. **El bloqueo corta todo**: con un bloqueo entre quien invita y quien acepta, la invitación no muestra la compatibilidad ni conecta ni cuenta como aceptación (404); la ficha de una conexión bloqueada ya no se ve (404) para ninguno de los dos; no se puede volver a bloquear una conexión ya bloqueada.
2. **La explicación con IA usa el test solo si los dos lo completaron** (como la pantalla, spec P2).
3. **Círculo rápido**: la sinastría de cada par se calcula una vez y se reutiliza mientras no cambien sus datos de nacimiento.
4. **Límites que se respetan con pedidos simultáneos**:
   - "Dónde vivís": la primera carga es libre; después, **un cambio cada 30 días** (decisión de German); 429 si no.
   - Cambios del test (10 por día) y aceptar/rechazar una solicitud: de a uno por persona o por conexión.
5. **"Seguir con mi cuenta"** borra el perfil duplicado con todo lo suyo (sesiones, fotos, test, etc.) y entra a la cuenta existente, sin error.
6. **Al cerrar sesión** la web borra la última lista de Círculo guardada en el navegador.
7. **Cerrar sesión cierra de verdad**: también se borra la marca del dispositivo, así nadie más vuelve a entrar desde ese navegador. Quien no verificó su WhatsApp pierde la cuenta, así que la web avisa antes: "Si cerrás sesión sin verificar tu WhatsApp, vas a perder tu cuenta" con "Verificar ahora" o "Cerrar igual".
8. **Un link no pasa por encima de un rechazo**: si quien invita había rechazado a esa persona, aceptar su link no los conecta (para quien fue rechazado sigue "pendiente").

## Casos de prueba (`apps/api/tests/test_r3_breaker_segunda_corrida.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Bloqueo e invitaciones | Revelar y aceptar el link de quien bloqueó → 404, sin aceptación registrada; la ficha de la conexión → 404; volver a bloquear → 409 |
| 2 | Explicación con test incompleto | La IA no recibe el test |
| 3 | Círculo dos veces | La sinastría de cada par se calcula una sola vez |
| 4 | Dónde vivís | Primera carga y un cambio ok; el siguiente en el mes → 429; con 10 a la vez después de la carga, uno solo pasa |
| 5 | Aceptar y rechazar a la vez | Las respuestas coinciden con el estado final |
| 6 | Seguir con mi cuenta con sesión, foto y test en el duplicado | 204/200 y sesión en la cuenta existente |
| 7 | Cerrar sesión | Después, `POST /sessions/start` → 403 |
| 8 | Link de quien me rechazó | No conecta |

## Criterios de aceptación

- [x] Los casos pasan.
- [x] La web avisa antes de cerrar sesión sin verificar y borra la lista guardada.

## Fuera de alcance

Cuentas descartables (en producción se pide WhatsApp, spec A10).
