# P2-privacidad-breaker — Que no se puedan deducir respuestas, ubicación ni saltear un bloqueo

- **Estado**: implemented
- **Módulo**: A6 (test), B9 (distancia), B7 (bloqueo)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-22 ("arrancá por todo"), a partir del informe del agente breaker (hallazgos 2, 3 y 4).

## Problema

1. Con una cuenta descartable que responde una sola pregunta del test, Descubrir devolvía el puntaje por eje (aunque el test estuviera incompleto) y, probando opción por opción, se deducían las respuestas del otro, incluida Atracción.
2. Cambiando la propia ubicación varias veces y leyendo la distancia exacta, se ubicaba a otra persona a menos de 300 metros.
3. Quien bloqueaba seguía apareciendo en Descubrir para la otra persona (y al revés).

## Puntos abiertos

Ninguno.

## Requisitos funcionales

### Test de personalidad
- La compatibilidad del test (en Descubrir y en el chat) se muestra **solo si los dos completaron el test**. Con un test incompleto no hay ni total ni ejes ("aparece cuando los dos completen el test").
- Los puntajes por eje del test que ve otra persona se **redondean a múltiplos de 5**.
- Con el test completo, se pueden **cambiar hasta 10 respuestas por día** (configurable); después, 429 "Podés seguir cambiando respuestas mañana". Completar el test por primera vez no cuenta.

### Distancia
- La distancia que se muestra es una **franja**: hasta 5, 10, 25, 50 o 100 km; más lejos, redondeada para arriba a la centena. La tarjeta dice "a menos de N km".
- El filtro solo acepta 5, 10, 25, 50 o 100 km.
- "Dónde vivís" se guarda con las coordenadas **redondeadas a 2 decimales** (~1 km) y se puede cambiar **hasta 3 veces por día**; después, 429.

### Bloqueo
- Si hay un bloqueo entre dos personas (lo haya hecho cualquiera), **no se ven en Descubrir**, tampoco buscando por nombre, y no se puede pedir la explicación de compatibilidad (404).
- La compatibilidad del chat (`/matches/{id}/compatibility`) solo con la conexión aceptada (409 si no).

## Casos de prueba (`apps/api/tests/test_p2_privacidad_breaker.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Test incompleto | `personality` null en Descubrir y en el chat |
| 2 | Ejes del test | Múltiplos de 5 |
| 3 | Límite de cambios | Con el test completo, el cambio 11 del día → 429 |
| 4 | Distancia en franjas | ~4 km se ve como 5; ~280 km como 300 |
| 5 | Filtro de distancia | Solo 5, 10, 25, 50, 100 (otro → 422) |
| 6 | Dónde vivís | Coordenadas a 2 decimales; el cuarto cambio del día → 429 |
| 7 | Bloqueo | No se ven en Descubrir (ni buscando) en ninguna dirección; explicación 404 |
| 8 | Compatibilidad de un chat bloqueado | 409 |

## Criterios de aceptación

- [x] Los casos pasan; el test de A6 "incompleto es provisorio" se reemplaza.

## Fuera de alcance

Deducir el género oculto con los filtros de pareja (pendiente de analizar), límite de cuentas por dispositivo.
