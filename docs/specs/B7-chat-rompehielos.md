# B7-chat-rompehielos — Chat con rompehielos de IA

- **Estado**: implemented
- **Módulo**: B7
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Al generarse resonancia mutua, eliminar el "hola, ¿cómo estás?" inyectando automáticamente un disparador de conversación personalizado, gratis, basado en los aspectos más fuertes de ambas cartas natales.

## Puntos abiertos (no bloquean v1)

- Tonos/copies finales del chat y de los rompehielos generados — `BACKLOG.md` P0. **No bloquea v1**: se implementa con guía editorial borrador (misma lógica que `B5`, reutilizando el principio "nunca caja negra"), reemplazable sin tocar la mecánica de generación.

## Requisitos funcionales

- Cuando dos perfiles generan resonancia mutua (match), se crea el chat con un primer mensaje generado por IA ya insertado — no es el usuario quien lo escribe.
- El rompehielos se basa en los aspectos astrológicos más fuertes entre ambas cartas natales (mismo dato que alimenta la explicación de `B5`).
- Es gratis y automático — no requiere acción del usuario para generarse.

## Contrato de datos / API

```
POST /matches/{match_id}/icebreaker  (llamado automáticamente al crearse el match)
  input a Claude API: { "chart_a": {...}, "chart_b": {...}, "strongest_aspects": [...] }
  output: texto del primer mensaje del chat

GET /chats/{match_id}/messages -> incluye el mensaje inicial con sender = "system_icebreaker"
```

## UX / Flujo

1. Se genera el match (resonancia mutua).
2. El chat se abre ya con el mensaje rompehielos como primer mensaje.
3. El usuario responde directamente, sin pantalla de "hola" vacía.

## Criterios de aceptación

- [ ] Todo chat nuevo arranca con un mensaje generado por IA, nunca vacío.
- [ ] El rompehielos referencia aspectos astrológicos reales de ambas cartas (no es genérico/template fijo).
- [ ] La generación no le cuesta nada al usuario (gratis, acorde a la regla de MVP sin paywall).

## Fuera de alcance

- Tono/copy editorial final (iterable sin tocar la mecánica).
