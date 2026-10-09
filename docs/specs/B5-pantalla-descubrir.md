# B5-pantalla-descubrir — Pantalla "Descubrir"

- **Estado**: implemented
- **Módulo**: B5
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Lista curada y chica de perfiles (menos opciones, mejor señal), con compatibilidad explicada en texto por IA — nunca un score sin explicación (pilar "Explain", `VISION.md`).

## Puntos abiertos (no bloquean v1)

- Qué tipos de relación filtrar (pareja/amistad/etc.) — `BACKLOG.md` P0. **Default de v1**: un solo contexto de relación (pareja/dating), sin selector de tipo.
- **Decisión de dirección (German, 2026-10-07)**: el tipo de relación **no** va en el perfil (ver `A4-perfil-liviano.md`): se elige **en Descubrir**, como "contexto" de la búsqueda, y la lista queda **abierta** a crecer: pareja, amistad, trabajo (evaluar un jefe o un compañero), socio, y otros que surjan. El contexto cambia el enfoque de la explicación de resonancia (no es lo mismo leer una carta como pareja que como socios). Diseño detallado pendiente: spec a escribir antes de implementarlo.

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

## Casos de prueba

Tests automáticos en `apps/api/tests/test_b5_descubrir.py` (correr: `cd apps/api && .venv/bin/pytest`).

| # | Caso | Test |
|---|---|---|
| 1 | Descubrir exige estar verificado | `test_descubrir_exige_estar_verificado` |
| 2 | Lista ordenada por compatibilidad con ejes | `test_lista_ordenada_por_compatibilidad_con_ejes` |
| 3 | Contexto invalido se rechaza | `test_contexto_invalido_se_rechaza` |
| 4 | No se ve uno mismo | `test_no_se_ve_uno_mismo` |
| 5 | Explicación nombra los ejes relevantes del contexto | `test_explicacion_nombra_los_ejes_relevantes_del_contexto` |

## Criterios de aceptación

- [ ] Ningún perfil en la lista muestra % sin que exista una explicación de texto asociada.
- [ ] El cálculo de `compatibility_signals` es determinístico (basado en aspectos astrológicos), el texto editorial es lo único generado por LLM.
- [ ] La lista excluye perfiles no verificados.

## Fuera de alcance

- Selector de tipo de relación (pareja/amistad/etc.) — v1 asume un solo contexto (dating).
- Guía editorial final/tono definitivo del prompt a Claude (iterable sin romper el contrato de datos).
