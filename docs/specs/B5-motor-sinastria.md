# B5-motor-sinastria — Motor de sinastría por ejes

- **Estado**: implemented (tablas v1-provisoria)
- **Módulo**: B5 (reemplaza el cálculo simplificado Sol-Sol de `B5-pantalla-descubrir.md`)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-08 (pidió completar las tablas y tenerlas como configuración)
- **Fuente**: cuadro "Flujo de la app — Sinastría astrológica / Arquitectura general del software" que pasó German (2026-10-08). Transcripto acá.

## Problema

Hoy la compatibilidad mira solo el aspecto Sol-Sol y devuelve un % genérico. El objetivo del cuadro: *una sinastría precisa, personalizada y equilibrada, que refleje la dinámica real de la relación desde una mirada astrológica integral* — "Dos cartas, un mismo cielo, múltiples posibilidades". Además, el resultado depende del **tipo de relación**, que encaja con el contexto que se elige en Descubrir.

## El flujo (10 niveles)

1. **Ingresa data**: Carta A vs. Carta B (fecha, hora y lugar de nacimiento de cada una).
2. **Determina los ejes a analizar**:
   - **Eje 1 — Atracción / química sexual**
   - **Eje 2 — Afecto / emoción**
   - **Eje 3 — Comunicación**
   - **Eje 4 — Compromiso**
   - **Eje 5 — Modificadores**
3. **Matriz de signos 12×12** por eje (144 combinaciones): suma puntos según la combinación de signos para cada eje.
4. **Aspectos** mayores y menores entre los planetas: suma puntos según el aspecto.
5. **Ajuste por orbe**: reajusta el impacto de cada aspecto según qué tan exacto es.
6. **Matriz de casas**: suma puntos según las casas relevantes de cada eje:
   - Eje 1: casas 8 y 5 · Eje 2: 7, 4, 5 y 8 · Eje 3: 3, 9 y 11 · Eje 4: 7, 4, 10 y 5 · Eje 5: según la lógica de modificadores.
7. **Resultado por eje (0 a 100)**: aplica **pesos de combinaciones según el tipo de relación** (ejes 1 a 4).
8. **Pasa por el Eje 5**: cada eje se ajusta según su lógica de modificadores (elementos, polaridades, modalidades, compensatorios). El Eje 5 es un **filtro final por eje**.
9. **Resultado final de cada eje**: puntaje individual de los ejes 1 a 4.
10. **Compatibilidad total**: promedio simple de los 4 ejes (ya ajustados por el Eje 5) → **0–100%**.

**Tipos de relación** (cambian los pesos por eje): relaciones sexuales ocasionales · relación de pareja formal · amistades · profesional / laboral / partnerships. Es la misma lista abierta del contexto de Descubrir (`B5-pantalla-descubrir.md`).

**Resultado que entrega**: puntaje de cada eje (0–100), ajuste por Eje 5, promedio de los 4 ejes, compatibilidad total (0–100).

## Puntos abiertos

Las tablas de contenido astrológico no están en el cuadro; sin ellas el motor no puede dar resultados reales:

- [x] **Planetas de cada eje**: qué planetas/puntos entran en cada eje (ej. Eje 1 Venus–Marte, Eje 3 Mercurio…).
- [x] **Matrices 12×12**: los puntos de cada combinación de signos, por eje (5 × 144 valores).
- [x] **Puntos por aspecto**: qué aspectos menores se usan y cuántos puntos suma o resta cada uno, por eje.
- [x] **Regla de orbe**: orbe máximo por aspecto y cómo escala el impacto (ej. lineal hasta 0 en el orbe máximo).
- [x] **Puntos por casas**: cómo se puntúa "planeta de A cae en casa relevante de B", y **sistema de casas** (Placidus, Casas Iguales, Whole Sign…).
- [x] **Lógica del Eje 5**: cómo elementos, polaridades, modalidades y compensatorios ajustan cada eje.
- [x] **Pesos por tipo de relación**: la tabla de pesos de cada eje según el tipo (los 4 tipos del cuadro).
- [x] **Normalización a 0–100** de cada eje.
- [x] **Sin hora exacta**: las casas y el ascendente dependen de la hora; con hora estimada (12:00 o franja del día, A1) definir si el nivel 6 se omite, se reduce su peso o se marca como "aproximado".
- [x] ¿La explicación de la IA (pilar "Explain") usa el detalle por eje? Propuesta: sí, la explicación cita los ejes más altos y más bajos.

## Cuadro actualizado

Versión visual del cuadro con todas las tablas completadas y un ejemplo real: https://claude.ai/artifact/137AMUTQHNx6hvnVwTtyw5 (privado de German; compartirlo desde el menú Share para que lo vea Pablo).

## Cómo se completaron las tablas (2026-10-08)

Todas en `apps/api/app/synastry/config/synastry_v1.json` (ver ADR 0010). Resumen:

| Eje | Planetas (A ↔ B) | Casas | Qué premia la matriz de signos |
|---|---|---|---|
| 1 Atracción | Venus–Marte (×3), Marte–Marte, Sol–Marte, Venus–Venus, Luna–Marte, Plutón–Venus/Marte, Asc–Venus/Marte | 8 y 5 | Polaridad y fricción (oposición, cuadratura) |
| 2 Afecto | Sol–Luna (×3), Luna–Venus, Luna–Luna, Venus–Venus, Sol–Venus, Neptuno–Venus/Luna | 7, 4, 5 y 8 | Armonía (trígono, mismo signo) |
| 3 Comunicación | Mercurio–Mercurio (×3), Mercurio–Sol, –Luna, –Júpiter, –Urano, –Asc, Sol–Sol | 3, 9 y 11 | Ida y vuelta (sextil, mismo signo) |
| 4 Compromiso | Saturno–Sol/Luna/Venus, Sol–Luna, Júpiter–Venus/Sol, Sol–Sol, Saturno–Saturno | 7, 4, 10 y 5 | Estabilidad (trígono); castiga cuadraturas |
| 5 Modificadores | Elementos, polaridades, modalidades y compensatorios de Sol, Luna, Asc, Mercurio, Venus y Marte | — | Ajusta cada eje ×0,85 a ×1,15 |

- **Aspectos**: mayores (conjunción 8°, sextil 6°, cuadratura 7°, trígono 7°, oposición 8°; +2° si interviene Sol o Luna) y menores (semisextil y semicuadratura 2°, sesquicuadratura 2°, quincuncio 3°). En atracción las tensiones suman (chispa); en afecto, comunicación y compromiso restan.
- **Orbe**: impacto lineal, 100 % exacto y 0 % en el borde.
- **Pesos por tipo** (atracción / afecto / comunicación / compromiso): ocasional 55/15/20/10 · pareja 25/30/20/25 · amistad 5/35/40/20 · laboral 0/15/45/40.
- **Normalización**: 50 = pareja promedio, calibrado solo.
- **Integración**: Descubrir ordena por la compatibilidad total del contexto elegido (selector Pareja / Amistad / Trabajo / Casual), muestra los 4 ejes y la explicación nombra el eje más fuerte y el más flojo entre los que importan para ese contexto. El rompehielos, la invitación y el calendario todavía usan el cálculo simple Sol–Sol / Luna–Sol.

## Requisitos funcionales / técnicos (propuesta)

- El motor recibe dos cartas completas y un tipo de relación, y devuelve el puntaje por eje y el total, **más el detalle** de qué sumó cada nivel (para la explicación y para poder calibrar).
- **Todas las tablas (matrices, puntos, orbes, casas, pesos) viven en archivos de configuración versionados**, no en el código: se pueden ajustar sin reprogramar y comparar versiones.
- La carta completa (posiciones de todos los planetas, ascendente y casas) se calcula una vez al cargar los datos natales y se guarda. `astronomy-engine` (ADR 0005) da las posiciones; ascendente y casas se calculan a partir de la hora sideral y la latitud.
- Mientras falten tablas, el motor puede correr con tablas de ejemplo marcadas como provisorias, para probar el flujo de punta a punta.

## Contrato de datos / API (borrador)

```
GET /discover?viewer_id=...&context=pareja|amistad|laboral|ocasional
  -> [{ ..., "compatibility_pct": 72,
        "axes": { "atraccion": 80, "afecto": 65, "comunicacion": 70, "compromiso": 73 } }]
```

## Casos de prueba

Tests automáticos en `apps/api/tests/test_b5_motor_sinastria.py` (correr: `cd apps/api && .venv/bin/pytest`).

| # | Caso | Test |
|---|---|---|
| 1 | Carta coincide con efemérides | `test_carta_coincide_con_efemerides` |
| 2 | Usa la hora local del lugar | `test_usa_la_hora_local_del_lugar` |
| 3 | Doce casas desde el ascendente | `test_doce_casas_desde_el_ascendente` |
| 4 | Sin lugar no hay casas ni ascendente | `test_sin_lugar_no_hay_casas_ni_ascendente` |
| 5 | Resultado reproducible y en rango | `test_resultado_reproducible_y_en_rango` |
| 6 | El tipo de relación cambia el total pero no los ejes | `test_el_tipo_de_relacion_cambia_el_total_pero_no_los_ejes` |
| 7 | Tipo desconocido usa el por defecto | `test_tipo_desconocido_usa_el_por_defecto` |
| 8 | Sin hora exacta no usa casas y es aproximado | `test_sin_hora_exacta_no_usa_casas_y_es_aproximado` |
| 9 | Detalle por nivel para explicar | `test_detalle_por_nivel_para_explicar` |
| 10 | Configuración completa | `test_configuracion_completa` |
| 11 | Cambiar una tabla cambia el resultado sin tocar código | `test_cambiar_una_tabla_cambia_el_resultado_sin_tocar_codigo` |

## Criterios de aceptación

- [x] Dadas dos cartas y un tipo de relación, el motor devuelve 4 puntajes por eje (0–100) y un total (0–100), reproducible.
- [x] Cambiar el tipo de relación cambia los pesos y, por lo tanto, el resultado.
- [x] Cambiar una tabla de configuración cambia el resultado sin tocar código.
- [x] El detalle por nivel queda disponible para la explicación.

## Fuera de alcance

- Definir el contenido astrológico de las tablas (lo provee el equipo; la spec solo fija su forma).
- Mostrar el detalle por eje en la interfaz (se diseña aparte, junto con el selector de contexto).
