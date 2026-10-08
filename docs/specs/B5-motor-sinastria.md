# B5-motor-sinastria — Motor de sinastría por ejes

- **Estado**: draft
- **Módulo**: B5 (reemplaza el cálculo simplificado Sol-Sol de `B5-pantalla-descubrir.md`)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: —
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

- [ ] **Planetas de cada eje**: qué planetas/puntos entran en cada eje (ej. Eje 1 Venus–Marte, Eje 3 Mercurio…).
- [ ] **Matrices 12×12**: los puntos de cada combinación de signos, por eje (5 × 144 valores).
- [ ] **Puntos por aspecto**: qué aspectos menores se usan y cuántos puntos suma o resta cada uno, por eje.
- [ ] **Regla de orbe**: orbe máximo por aspecto y cómo escala el impacto (ej. lineal hasta 0 en el orbe máximo).
- [ ] **Puntos por casas**: cómo se puntúa "planeta de A cae en casa relevante de B", y **sistema de casas** (Placidus, Casas Iguales, Whole Sign…).
- [ ] **Lógica del Eje 5**: cómo elementos, polaridades, modalidades y compensatorios ajustan cada eje.
- [ ] **Pesos por tipo de relación**: la tabla de pesos de cada eje según el tipo (los 4 tipos del cuadro).
- [ ] **Normalización a 0–100** de cada eje.
- [ ] **Sin hora exacta**: las casas y el ascendente dependen de la hora; con hora estimada (12:00 o franja del día, A1) definir si el nivel 6 se omite, se reduce su peso o se marca como "aproximado".
- [ ] ¿La explicación de la IA (pilar "Explain") usa el detalle por eje? Propuesta: sí, la explicación cita los ejes más altos y más bajos.

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

## Criterios de aceptación

- [ ] Dadas dos cartas y un tipo de relación, el motor devuelve 4 puntajes por eje (0–100) y un total (0–100), reproducible.
- [ ] Cambiar el tipo de relación cambia los pesos y, por lo tanto, el resultado.
- [ ] Cambiar una tabla de configuración cambia el resultado sin tocar código.
- [ ] El detalle por nivel queda disponible para la explicación.

## Fuera de alcance

- Definir el contenido astrológico de las tablas (lo provee el equipo; la spec solo fija su forma).
- Mostrar el detalle por eje en la interfaz (se diseña aparte, junto con el selector de contexto).
