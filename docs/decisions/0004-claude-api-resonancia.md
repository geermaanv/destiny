# 0004 — Claude API para explicaciones de resonancia

- **Estado**: aceptada.

## Contexto

El pilar "Explain" de `../VISION.md` exige que ninguna compatibilidad se muestre como score sin explicación (módulo B.5, pantalla "Descubrir" en `../ALCANCE_MVP.md`). Esto requiere un LLM capaz de generar texto explicativo con tono editorial controlado, no solo clasificar.

## Decisión

Usar la API de Claude (Anthropic) para generar las explicaciones de resonancia, enviando datos astrológicos + intención de ambos perfiles en JSON, bajo lineamientos editoriales de Destiny.

## Consecuencias

- El contrato de datos exacto (qué JSON se manda, qué prompt/guía editorial se usa) queda definido en la spec `B5` cuando se escriba, no en este ADR.
- Costo variable por explicación generada — a monitorear cuando haya volumen real de usuarios.
