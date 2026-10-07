# B5-pantalla-descubrir — Pantalla "Descubrir"

- **Estado**: implemented
- **Módulo**: B5
- **Owner de decisión de producto**: Pablo Maiztegui (los puntos abiertos abajo siguen siendo suyos)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Lista curada y chica de perfiles (menos opciones, mejor señal), con compatibilidad explicada en texto por IA — nunca un score sin explicación (pilar "Explain", `VISION.md`).

## Puntos abiertos (no bloquean v1)

- Qué tipos de relación filtrar (pareja/amistad/etc.) — `BACKLOG.md` P0. **Default de v1**: un solo contexto de relación (pareja/dating), sin selector de tipo. El filtro por tipo de relación queda fuera de alcance hasta que Pablo defina cuáles soportar (alineado con la visión de `VISION.md` de extender el Identity Graph a otros contextos más adelante, no en el MVP).

## Requisitos funcionales

- Lista corta de perfiles candidatos (no scroll infinito) con % de compatibilidad visible.
- Al abrir un perfil: la IA genera una explicación en texto que responde "¿Por qué esta persona? ¿Por qué ahora? ¿Qué parte de nosotros resuena?".
- La explicación nunca se muestra sin el texto — el % solo no es suficiente.
- Solo perfiles con estado `verificado` (A3) entran a la lista.

## Contrato de datos / API

Input al LLM (Claude API, ADR 0004):

```json
{
  "viewer": { "natal_chart": {...}, "intent": "pareja" },
  "candidate": { "natal_chart": {...}, "intent": "pareja" },
  "compatibility_signals": { "aspects": [...], "percentage": 78 }
}
```

Output esperado del LLM: texto editorial (no JSON estructurado) con la explicación, bajo guía editorial de Destiny (prompt/sistema a definir en implementación, iterable sin cambiar el contrato de arriba).

```
GET /discover -> [{ "profile_id": "...", "compatibility_pct": 78, "preview": "..." }]
GET /discover/{profile_id}/explanation -> { "text": "..." }
```

## UX / Flujo

1. Lista chica de candidatos con % destacado.
2. Tap en un perfil → carga la explicación de IA (puede ser async/loading corto).
3. Nunca se renderiza el % sin posibilidad de ver la explicación.

## Criterios de aceptación

- [ ] Ningún perfil en la lista muestra % sin que exista una explicación de texto asociada.
- [ ] El cálculo de `compatibility_signals` es determinístico (basado en aspectos astrológicos), el texto editorial es lo único generado por LLM.
- [ ] La lista excluye perfiles no verificados.

## Fuera de alcance

- Selector de tipo de relación (pareja/amistad/etc.) — v1 asume un solo contexto (dating).
- Guía editorial final/tono definitivo del prompt a Claude (iterable sin romper el contrato de datos).
