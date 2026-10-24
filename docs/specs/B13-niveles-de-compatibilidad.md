# B13-niveles-de-compatibilidad — Nivel y frase junto al número global

- **Estado**: implemented
- **Módulo**: B9 (Círculo) + B12 (chat)
- **Owner de decisión de producto**: German Villamarin (por ahora); rangos de Pablo (ADR 0011)
- **Aprobada para implementación por**: German Villamarin, 2026-10-24 ("aplicar textos ajustados a la app, estamos ok").

## Problema

El número global solo dice de dónde sale ("Promedio de astrología y test"). Pablo mandó una escala de cinco niveles para interpretarlo. Sus rangos se respetan tal cual; los textos de los dos niveles altos ("ya te conocías de otra vida", "almas gemelas, unión absoluta") se ajustan para no dar un veredicto (principio "herramienta, no oráculo", `docs/PROPOSITO.md`) y para que valgan también en amistad y trabajo, porque el número global es el mismo para los cuatro vínculos.

## Puntos abiertos

Ninguno. Si Pablo quiere otros textos o rangos, se cambian en `apps/api/app/content/niveles_compatibilidad_v1.json` sin tocar código.

## Requisitos funcionales

Niveles (cada límite pertenece al nivel de arriba):

| Puntos | Nivel | Frase |
|---|---|---|
| 0–29 | Baja compatibilidad | Acá hay un desafío para trabajar. |
| 30–49 | Moderada | Las dificultades aparecen, pero también hay entendimiento. |
| 50–64 | Alta compatibilidad | Fluye más de lo que se traba. |
| 65–84 | Muy alta compatibilidad | Mucho fluye solo. Es fácil sentir que ya se conocían. |
| 85–100 | Excepcional | Una afinidad poco común. Lo que construyan depende de ustedes. |

- El nivel sale del número global que se muestra (el mismo de Círculo y del chat).
- Se muestra junto al número global en Círculo, en la ficha de la persona y en el chat: el nombre del nivel y la frase. Debajo sigue la línea de dónde sale el número.
- Rangos y textos en un JSON editable.

## Contrato de datos / API

`GET /discover` (cada tarjeta) y `GET /matches/{id}/compatibility/summary` suman:

```json
"nivel": {"id": "alta", "nombre": "Alta compatibilidad", "texto": "Fluye más de lo que se traba."}
```

## Casos de prueba (`apps/api/tests/test_b13_niveles_de_compatibilidad.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Bordes de cada nivel (0, 29, 30, 49, 50, 64, 65, 84, 85, 100) | Cada número cae en el nivel de la tabla; el límite pertenece al nivel de arriba |
| 2 | Textos desde la configuración | Nombre y frase de cada nivel son los del JSON, sin "almas gemelas" ni "otra vida" |
| 3 | Tarjeta de Círculo | Trae el nivel que corresponde a su `global_pct` |
| 4 | Compatibilidad del chat | Trae el nivel que corresponde a su `global_pct` |

## Criterios de aceptación

- [x] Los casos pasan.
- [x] Círculo, la ficha y el chat muestran nivel y frase junto al número.

## Fuera de alcance

Niveles por vínculo (la tabla por vínculo sigue mostrando solo números) y niveles por sistema.
