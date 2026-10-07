# B4-home-tu-momento — Home "Tu Momento"

- **Estado**: implemented
- **Módulo**: B4
- **Owner de decisión de producto**: Pablo Maiztegui (los puntos abiertos abajo siguen siendo suyos)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Pantalla de entrada diaria: contexto astrológico del día en lenguaje claro, mood check-in rápido, y señal social local ("N en tu frecuencia").

## Puntos abiertos (no bloquean v1)

- Estética y visuales del Hub en general — `BACKLOG.md` P0. No bloquea v1: se implementa con estilos base (Tailwind, tokens simples) reemplazables sin tocar lógica.

## Requisitos funcionales

- Clima astrológico del día en texto claro, generado a partir de los tránsitos del día (ej. "Luna llena en Libra"). No requiere personalización por usuario en v1 (es el clima general del día, no el de la carta personal — eso es `B5`/calendario).
- Mood check-in de un toque: selección simple de un estado de ánimo (set fijo de opciones), persistido con timestamp.
- Contador **"N en tu frecuencia"**: cantidad de perfiles verificados con tránsitos afines, agrupados geográficamente (radio configurable, default razonable a definir en implementación).

## Contrato de datos / API

```
GET /home/today -> { "astro_weather": "Luna llena en Libra", "date": "2026-10-07" }
POST /mood-checkins { "mood": "energico" | "tranquilo" | "reflexivo" | ... , "timestamp": "..." }
GET /home/frequency-count -> { "count": 134 }
```

## Criterios de aceptación

- [ ] El clima astrológico del día se calcula una vez por día (no por request) y se cachea.
- [ ] El mood check-in queda persistido y asociado al perfil.
- [ ] El contador de frecuencia solo cuenta perfiles con estado `verificado` (ver A3).

## Fuera de alcance

- Personalización visual/estética final del Hub (iteración posterior).
- Algoritmo fino de "afinidad de tránsitos" para agrupar usuarios (versión inicial puede ser una heurística simple: mismos aspectos mayores del día).
