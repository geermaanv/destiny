# A6-test-personalidad — Test de personalidad de Pablo dentro del perfil

- **Estado**: implemented
- **Módulo**: A6 (nuevo, Módulo A — perfil)
- **Owner de decisión de producto**: **Pablo Maiztegui es la última palabra sobre el modelo** (preguntas, tablas, pesos, topes). German Villamarin decide la integración en la app.
- **Aprobada para implementación por**: German Villamarin, 2026-10-12
- **Fuente**: `docs/referencias/pablo_test_express_v4.html` ("Test express de compatibilidad V4.0", armado por Pablo). ADR `0011-modelo-matematico-pablo.md`.

## Problema

Además de la sinastría, Destiny compara a dos personas con un cuestionario de personalidad diseñado por Pablo: 32 preguntas en los mismos 4 ejes (atracción, afecto, comunicación, compromiso). El objetivo es **un modelo matemático determinístico**: el resultado sale de tablas y fórmulas, no de consultar a una IA.

## Decisiones (German, 2026-10-12)

- El test de Pablo es **la fuente de verdad**: se implementa tal cual (preguntas, opciones, matrices 5×5, cruces, topes, 70/30, pesos por tipo de relación).
- **Va dentro del perfil** ("Mi perfil" → "Test de personalidad"), **no** en el registro. Es opcional y se puede completar de a partes.
- **Se muestra separado** de la astrología (como dice el HTML de Pablo: "no se suma al score de sinastría").
- **Todo parametrizable**: el modelo vive en `apps/api/app/personality/config/test_v4.json`, generado desde el HTML de Pablo (`scripts/import_pablo_test.mjs`). Pesos, matrices, topes, 70/30 y pesos por tipo se cambian ahí, sin tocar código.
- Las **explicaciones y rompehielos los sigue generando la IA** (como hoy); la IA no calcula ningún puntaje.
- Los **pesos por tipo de relación del motor de sinastría** se alinean con los del test de Pablo (formal 25/25/25/25 · ocasional 60/10/25/5 · amistad 10/35/40/15 · laboral 10/10/40/40).

## El modelo (de Pablo)

- 32 preguntas, 8 por eje, 5 opciones (A–E). Se puede elegir **1 o 2**: con dos, la primera pesa 70 % y la segunda 30 %.
- Cada pregunta tiene una **matriz 5×5** (0–100) según su tipo: ordinal, ritmo, frecuencia, crítico (por distancia entre opciones) o nominal (misma 100, relacionada 65, distinta 35).
- Con dos opciones se toma el **mejor emparejamiento** 70/30 entre las dos personas (problema de transporte 2×2).
- **4 cruces** "lo que necesito ↔ lo que el otro da" (iniciativa sexual, contención, lenguaje del amor, desacuerdo), cada sentido con la mitad del peso.
- **Puntaje del eje** = Σ(puntaje × peso) / Σ pesos respondidos. Se informa la **cobertura** (qué parte del eje está respondida).
- **Topes en E4**: si las respuestas principales están en extremos opuestos (A vs. E) en tipo de vínculo, exclusividad o hijos, E4 no supera 59; en convivencia, 69.
- **Total** = ejes ponderados por tipo de relación. Solo se informa cuando **los dos** respondieron las 32.

Equivalencia de contextos: Descubrir "Pareja" = formal, "Casual" = sexual, "Amistad" = amistad, "Trabajo" = laboral.

## Privacidad

- Las respuestas se guardan en el servidor y **nunca se muestran a otra persona**: los demás solo ven el resultado de la comparación.
- Antes de empezar se avisa que hay preguntas íntimas (sexualidad, hijos) y para qué se usan.

## Contrato de datos / API

```
GET  /personality/test                    -> preguntas y opciones (sin matrices)
GET  /profiles/{id}/personality           -> mis respuestas y progreso (solo con mi sesión)
PUT  /profiles/{id}/personality           -> { "answers": { "E1.01": [2], "E1.02": [1, 3], ... } }  (parcial, se va guardando)
GET  /discover?...                        -> cada candidato suma "personality": { axes, coverage, total, complete } (o null si alguno no respondió nada)
```

Modelo: tabla `personality_answers` (`profile_id`, `answers` JSON, `updated_at`).

## UX / Flujo

1. "Mi perfil" muestra una tarjeta "Test de personalidad" con el progreso (N/32) y "Empezar" / "Continuar".
2. `/perfil/test`: un eje por vez (8 preguntas), elegir 1 o 2 opciones (la primera es la principal), se guarda solo, "⇄ Invertir" principal/secundaria, "Siguiente eje".
3. En Descubrir, al abrir una tarjeta: "Astrología" (lo de hoy) y, separado, "Personalidad" con sus 4 ejes y el total (o "provisorio: falta completar" si alguno no terminó).

## Casos de prueba

Tests en `apps/api/tests/test_a6_test_personalidad.py`. Los resultados esperados se generan **con el código original de Pablo** (`scripts/pablo_golden.mjs` → `tests/fixtures/pablo_golden.json`).

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | La configuración tiene 32 preguntas (8 por eje), 4 cruces y 4 topes | Igual que el HTML de Pablo |
| 2 | Respuestas idénticas | 100 en los 4 ejes y en todos los tipos |
| 3 | 18 parejas de referencia (idénticas, opuestas, dos opciones cruzadas, topes, parciales y al azar) | Mismos puntajes por eje, cobertura y total que el código de Pablo (±0,01) |
| 4 | Extremos opuestos en "hijos" | E4 topeado en 59 |
| 5 | Extremos opuestos en "convivencia" | E4 topeado en 69 |
| 6 | Cambiar un peso o una matriz en la configuración | Cambia el resultado sin tocar código |
| 7 | Guardar respuestas parciales y leerlas | Se guardan; progreso N/32 |
| 8 | Más de 2 opciones, opción fuera de A–E o pregunta inexistente | 422 |
| 9 | Leer o editar las respuestas de otro | 401 sin sesión / 403 con otra sesión |
| 10 | Descubrir con los dos tests completos | `personality` con 4 ejes, total y `complete: true` |
| 11 | Descubrir con un test incompleto | Ejes provisorios con cobertura, total `null`, `complete: false` |
| 12 | Descubrir cuando el otro no respondió nada | `personality: null` |
| 13 | Las respuestas del otro nunca aparecen en Descubrir | No hay respuestas en la respuesta de la API |
| 14 | Pesos por tipo del motor de sinastría | Iguales a los de Pablo |

## Implementación (2026-10-12)

- Modelo: `app/personality/engine.py` (port de `scoreChoices`, `compareAxis` y el total de Pablo) + `app/personality/config/test_v4.json`, importado del HTML con `node scripts/import_pablo_test.mjs`. Referencias: `node scripts/pablo_golden.mjs` → `tests/fixtures/pablo_golden.json` (18 parejas).
- API: `GET /personality/test`, `GET`/`PUT /profiles/{id}/personality` (tabla `personality_answers`), `personality` en cada candidato de `/discover` según el contexto.
- Web: tarjeta "Test de personalidad" en Mi perfil, cuestionario `/perfil/test`, bloque "Personalidad" separado de "Astrología" en Descubrir.
- Resultado: 36 tests nuevos (113 en total), todos en verde; las 18 parejas dan los mismos números que el código de Pablo.

## Fuera de alcance

- Editar pesos y matrices desde la app (hoy se editan en el archivo de configuración). El HTML de Pablo lo permite por dispositivo; en Destiny sería una pantalla de administración futura.
- Compartir respuestas con códigos (el HTML de Pablo lo necesita porque no tiene servidor; Destiny no).
- Sumar el resultado del test al de la sinastría.

**Cambio posterior (2026-10-20, spec A12)**: antes de empezar se acepta un aviso de privacidad (sin aceptarlo no se guardan respuestas); los grupos se ordenan según lo que busca la persona (pesos de Pablo, Atracción al final si no hay dato) y antes de Atracción hay una pantalla de entrada con "Responder más tarde" para quien no busca pareja ni casual.

**Cambio posterior (2026-10-22, spec P2)**: la compatibilidad del test se muestra solo con los dos tests completos (ya no hay resultado "provisorio"), con los ejes en múltiplos de 5, y con el test completo se pueden cambiar hasta 10 respuestas por día.
