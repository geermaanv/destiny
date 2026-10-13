# B4-home-tu-momento — Home "Tu Momento"

- **Estado**: implemented
- **Módulo**: B4
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Pantalla de entrada diaria: contexto astrológico del día en lenguaje claro, mood check-in rápido, y señal social local ("N en tu frecuencia").

## Puntos abiertos (no bloquean v1)

- Estética y visuales del Hub en general — `BACKLOG.md` P0. No bloquea v1: se implementa con estilos base (Tailwind, tokens simples) reemplazables sin tocar lógica.

## Requisitos funcionales

- Clima astrológico del día en texto claro, generado a partir de los tránsitos del día (ej. "Luna llena en Libra"). No requiere personalización por usuario en v1 (es el clima general del día, no el de la carta personal — eso es `B5`/calendario).
- ~~Mood check-in de un toque~~ — **sacado de la pantalla** (German, 2026-10-13): se guardaba pero no se usaba en nada ni le devolvía algo a la persona. El endpoint `POST /mood-checkins` y la tabla quedan sin uso, para retomarlos con el Diario cósmico (ánimo + tránsito del día, con una devolución).
- Contador **"N en tu frecuencia"**: cantidad de perfiles verificados con tránsitos afines, agrupados geográficamente (radio configurable, default razonable a definir en implementación).

## v2 — "Tu día": tránsito personal en Inicio (aprobado por German, 2026-10-12, implementado)

- Inicio muestra una tarjeta **"Tu día"** con el tránsito personal de hoy: la Luna del día respecto de **tu** Sol natal (con la hora local de nacimiento, ver corrección en A1). Título + 1 o 2 oraciones en lenguaje simple, y link "Ver tu calendario".
- **El modelo calcula, el texto sale de una biblioteca fija** (ADR 0011 / spec X1): `apps/api/app/content/transitos_v1.json`, con un texto por **tipo de tránsito** (conjunción, sextil, cuadratura, trígono, oposición, o "sin tránsito fuerte") × **signo por el que pasa la Luna** (12) = 72 textos. Se generan **una sola vez** con la IA (`scripts/generate_transit_texts.py`) y quedan marcados "pendiente de revisión de Pablo"; se pueden editar a mano. **Abrir Inicio no llama a la IA.**
- "Hoy" es la fecha local del usuario (la manda la app).
- Si falta un texto en la biblioteca, se usa el texto genérico del tipo de tránsito (el del calendario).

```
GET /home/my-day?profile_id=&date=YYYY-MM-DD
  -> { "date", "aspect", "moon_sign", "title", "text", "is_major", "reviewed": false }
```

### Casos de prueba v2 (`apps/api/tests/test_b4_tu_dia.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | La biblioteca está completa | 6 tipos × 12 signos, todos con título y texto (máx. 280 caracteres) |
| 2 | "Tu día" para una fecha | Tránsito y signo lunar calculados con el Sol natal en hora local; título y texto de la biblioteca para esa combinación |
| 3 | Es el mismo tránsito que el calendario ese día | Mismo aspecto que `GET /calendar/day/{fecha}` |
| 4 | Sin sesión o con el perfil de otro | 401 / 403 |
| 5 | Abrir "Tu día" | No llama a la IA |
| 6 | Falta un texto en la biblioteca | Usa el texto genérico del tipo de tránsito |

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

## v3 — Tu día completo (German, 2026-10-13: "poder ir a un análisis más completo, más extenso")

Desde Hoy, el link **"Leer más →"** abre **Tu día completo** (`/dia`). Es la primera versión de "Mi cielo" del whitepaper. Todo lo astrológico lo **calcula el motor** (determinístico, ADR 0011); la IA solo **redacta** la lectura, en el estilo de la persona (X2), una vez por día.

**Contenido**
1. **El clima del día**: signo y fase de la Luna, y por qué **casa de tu carta** pasa (casas por signo entero; solo con hora exacta), con el tema de esa casa.
2. **Tus tránsitos activos**: los 3 más fuertes de hoy de los planetas del día (Sol a Plutón) sobre tus puntos natales (Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, y Ascendente y Medio Cielo si hay hora exacta). Aspectos mayores con orbe por planeta; fuerza = peso del planeta × peso del punto × cercanía al exacto. Cuando el aspecto se hace exacto dentro de ±15 días, se dice el día ("exacto el 16/10").
3. **Tu día por área**: amor, trabajo, emociones y energía, cada una "fluye", "pide cuidado" o "tranquilo", según los tránsitos que tocan sus puntos (armónicos suman, tensos restan).
4. **La lectura**: 3 a 5 oraciones en tu estilo que integran lo anterior, y una **pregunta para el día** (fija en la configuración, según el área más activa).

Configuración en `app/day/config/dia_v1.json` (orbes, pesos, áreas y sus puntos, temas de las casas, preguntas). Posiciones del día a las 12:00 UTC, como "Tu día".

**API**: `GET /home/my-day/detail?profile_id&date` (solo la propia persona) → `{date, luna: {signo, fase, casa?, tema_casa?}, transitos: [{planeta, punto, aspecto, orbe, exacto?, texto}], areas: [{clave, nombre, estado, motivo?}], lectura: {texto, ia}, pregunta, aproximado}`. La lectura se cachea por persona + día + datos natales + estilo + modelo (`ai_texts`, tipo `dia`); sin key, plantilla.

### Casos de prueba v3 (`apps/api/tests/test_b4_dia_completo.py`)

1. Solo la propia persona (otra → 403, sin sesión → 401).
2. Signo y fase de la Luna iguales a los calculados para esa fecha.
3. La casa de la Luna es la de la carta (signo entero desde el Ascendente); sin hora exacta no hay casa y `aproximado` es true.
4. Hasta 3 tránsitos, ordenados por fuerza, cada uno con un aspecto real dentro de su orbe; sin hora exacta no aparecen Ascendente ni Medio Cielo.
5. Las 4 áreas, cada una con un estado válido.
6. Sin key, la lectura es la plantilla (sin llamar a la red); con IA, el prompt lleva el estilo de la persona, no lleva datos personales y la segunda vez sale de la cache.
7. Cambiar los orbes en la configuración cambia los tránsitos sin tocar código.
