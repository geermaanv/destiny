# X1-redaccion-con-ia — Explicaciones y rompehielos redactados con IA (OpenRouter)

- **Estado**: implemented
- **Módulo**: X1 (transversal: lo usan B5 Descubrir y B7 chat)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-12
- **Relacionado**: ADR 0011 (el modelo matemático calcula; la IA solo redacta).

## Problema

Las explicaciones de Descubrir ("qué los une y qué tienen que trabajar") y los rompehielos del chat hoy salen de plantillas fijas, porque no hay key de IA configurada. German decidió que los redacte una IA, vía **OpenRouter** (ya lo usa y permite elegir modelos más baratos).

## Decisiones (German, 2026-10-12)

- Proveedor: **OpenRouter**. La key va en `apps/api/.env` (`OPENROUTER_API_KEY`) y **el modelo es un parámetro** (`OPENROUTER_MODEL`): se cambia sin tocar código.
- **La IA solo redacta** a partir del resultado ya calculado (ejes, aspectos principales, tipo de vínculo). Nunca calcula ni cambia un número.
- **Sin key, o si OpenRouter falla, se usa el texto de plantilla**: la pantalla nunca se rompe ni se queda esperando.
- El **tránsito personal del día** y **"Mi carta"** NO llaman a la IA en vivo: sus textos se generan una sola vez, Pablo los revisa y quedan como contenido fijo (specs propias, fuera de esta).

## Qué se le manda a la IA (minimización de datos)

Solo el resultado calculado:

- Explicación: tipo de vínculo, total, cada eje de astrología **con su nivel ya calculado** (alto ≥ 60, medio, bajo < 40), **"lo que más los une" y "lo que tienen que trabajar" ya decididos por el modelo** (entre los ejes que importan para el vínculo), y los aspectos más fuertes (ej. "Venus de una persona en trígono con la Luna de la otra"). Si los dos tienen el test de personalidad, también sus 4 ejes.
- **La IA no interpreta los números**: en la comparación de modelos (2026-10-12) varios leyeron "22" como alto. El modelo matemático decide qué es fuerte y qué es débil; la IA solo lo pone en palabras.
- Rompehielos: tipo de vínculo y el eje y aspecto más destacados.

**Nunca**: nombres, teléfonos, fechas, horas ni lugares de nacimiento, fotos, respuestas del test.

## Cómo tiene que escribir (guía editorial, en el prompt del sistema)

- Castellano rioplatense, con voseo, cálido y concreto. Sin jerga astrológica difícil.
- Explicación: 2 o 3 oraciones (máx. ~60 palabras): qué los une, qué tienen que trabajar. Puede citar los números que recibe, pero no inventar otros.
- Rompehielos: 1 o 2 oraciones, en primera persona del plural, que terminen en una pregunta para empezar a charlar.
- Nada de predicciones ("van a ser felices"), contenido sexual explícito, ni mencionar que es una IA.

## Reglas técnicas

- Llamada: `POST https://openrouter.ai/api/v1/chat/completions` con el modelo configurado, `max_tokens` 300, timeout 8 s, sin reintentos, y **razonamiento desactivado** (`reasoning: {enabled: false}`): los modelos que "piensan" gastaban los tokens pensando y devolvían texto vacío.
- Sin formato: texto plano, sin markdown.
- Se limpia la respuesta (espacios, comillas) y se recorta a un máximo (explicación 420 caracteres, rompehielos 280) cortando por oración.
- **Cache de explicaciones**: misma pareja + mismo vínculo + mismo modelo + misma versión de tablas → se reutiliza el texto guardado (no se paga dos veces). Tabla `ai_texts` (clave, texto, modelo, tokens usados, fecha).
- El rompehielos se genera una vez por conexión (ya queda guardado como primer mensaje del chat).
- Se registran modelo y tokens de cada llamada (para seguir el costo).

## Comparación de modelos

`apps/api/scripts/compare_llm_models.py` corre los mismos casos de prueba contra una lista de modelos de OpenRouter y escribe `docs/referencias/comparacion-modelos-ia.md` con los textos, el tiempo de respuesta y el costo estimado. German elige el modelo y lo pone en `OPENROUTER_MODEL`.

Candidatos iniciales (precio por millón de tokens, entrada / salida, según la API pública de OpenRouter al 2026-10-12): `qwen/qwen3.7-flash` (0,03 / 0,13), `mistralai/mistral-small-3.2-24b-instruct` (0,09 / 0,25), `openai/gpt-5-nano` (0,05 / 0,40), `google/gemini-2.5-flash-lite` (0,10 / 0,40), `anthropic/claude-haiku-5.5` (0,10 / 0,50), `deepseek/deepseek-v3.2` (0,26 / 0,80).

## Casos de prueba

Tests en `apps/api/tests/test_x1_redaccion_con_ia.py` (OpenRouter simulado: no se llama a internet).

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Sin key configurada | Texto de plantilla, sin llamar a la red |
| 2 | Con key | Llama a OpenRouter con el modelo configurado y la key en el encabezado |
| 3 | Lo que se manda a la IA | No incluye nombres, teléfono, fecha/hora/lugar de nacimiento ni respuestas del test |
| 4 | Respuesta correcta | Se usa el texto de la IA, limpio |
| 5 | Error, timeout o texto vacío | Texto de plantilla; la pantalla responde igual |
| 6 | Texto demasiado largo | Se recorta por oración al máximo |
| 7 | Misma pareja y vínculo dos veces | La segunda no llama a la IA (cache) |
| 8 | Otro vínculo | Nueva llamada |
| 9 | Conectar dos personas | El rompehielos se pide una sola vez y queda como primer mensaje |
| 10 | Se registra el uso | Modelo y tokens guardados |
| 11 | Lo que recibe la IA | Trae "lo que más los une" y "lo que tienen que trabajar" ya calculados y el nivel de cada eje |
| 12 | El pedido a OpenRouter | Pide razonamiento desactivado |

## Resultado de la comparación (2026-10-12)

Ver `docs/referencias/comparacion-modelos-ia.md`. Con los datos ya interpretados por el modelo, todos los modelos eligen bien qué destacar. Costo por cada 1000 textos: qwen3.7-flash USD 0,02 · mistral-small-3.2 0,05 · gemini-2.5-flash-lite 0,06 · claude-haiku-5.5 0,12 · deepseek-v3.2 0,15. `openai/gpt-5-nano` no sirve (exige razonamiento). Mejor redacción en castellano rioplatense: claude-haiku-5.5; opción más económica con buen resultado: gemini-2.5-flash-lite.

## Fuera de alcance

- Textos del tránsito del día y de "Mi carta" (contenido fijo generado una vez y revisado por Pablo; specs aparte).
- Moderación de los mensajes que escriben los usuarios.
