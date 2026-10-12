# 0011 — Compatibilidad con modelo matemático determinístico; Pablo es la última palabra del modelo

- **Estado**: aceptada (German Villamarin, 2026-10-12).

## Contexto

Pablo armó un test de personalidad (`docs/referencias/pablo_test_express_v4.html`) con su propio modelo de puntuación. El objetivo del producto es **no depender de una IA para calcular cada compatibilidad**, sino tener un modelo matemático explícito.

## Decisión

- **Pablo es la última palabra sobre el modelo de compatibilidad**: preguntas, tablas, pesos, topes y pesos por tipo de relación. Lo que él define se implementa tal cual; si algo propuesto antes lo contradice, gana lo de Pablo (por ejemplo, los pesos por tipo de relación del motor de sinastría se alinean con los de su test).
- **Todos los puntajes son determinísticos** (mismas entradas → mismo resultado), salen de tablas y fórmulas, y son explicables nivel por nivel.
- **Todo es parametrizable**: los modelos viven en archivos de configuración versionados (`app/synastry/config/`, `app/personality/config/`), no en el código.
- **La IA solo redacta** (explicaciones y rompehielos), a partir del resultado ya calculado; nunca decide un puntaje.
- **Fidelidad verificable**: el test de personalidad se importa ejecutando el código del HTML de Pablo y los tests comparan contra resultados generados por ese mismo código.

## Consecuencias

- Si Pablo cambia su HTML, se reimporta (`node scripts/import_pablo_test.mjs`), se regeneran los resultados de referencia (`node scripts/pablo_golden.mjs`) y los tests dicen si la API sigue igual.
- Cambiar un número no requiere programar, pero sí pasar por un commit (queda historial de cada cambio del modelo).
