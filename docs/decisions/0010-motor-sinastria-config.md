# 0010 — Motor de sinastría: tablas en configuración, casas iguales y calibración automática

- **Estado**: aceptada (German Villamarin, 2026-10-08). Tablas `v1-provisoria`, pendientes de validación astrológica.

## Contexto

El cuadro de German (spec `B5-motor-sinastria.md`) define el flujo de 10 niveles pero no los números: planetas por eje, matrices 12×12, puntos por aspecto, orbes, casas, lógica del Eje 5 y pesos por tipo de relación. German pidió completarlos y tenerlos como configuración.

## Decisión

- **Todas las tablas viven en `apps/api/app/synastry/config/synastry_v1.json`**, generado por `apps/api/scripts/build_synastry_config.py` a partir de reglas legibles. El motor (`app/synastry/engine.py`) no tiene contenido astrológico en el código.
- **Matrices 12×12** generadas a partir de la relación entre signos (mismo signo, semisextil, sextil, cuadratura, trígono, quincuncio, oposición) con puntos distintos por eje; quedan como 144 valores editables por eje.
- **Carta completa** con `astronomy-engine` y la hora local real del lugar de nacimiento (zona horaria del geocoding, A1). **Casas iguales desde el ascendente**: funcionan en cualquier latitud y no requieren otra librería; Placidus queda como opción a futuro.
- **Sin hora exacta** (12:00 o franja del día): no se usan las casas y el resultado se marca "aproximado".
- **Calibración automática**: el script centra cada eje para que una pareja promedio (1500 pares al azar) dé 50, con ~18 puntos de desvío. Cualquier cambio en las tablas se recalibra solo al regenerar.
- **Interpretación del nivel 10**: el cuadro dice "promedio simple de los 4 ejes" y también "pesos por eje según el tipo de relación". Se implementa un **promedio ponderado por tipo**; con pesos iguales es exactamente el promedio simple.

## Consecuencias

- Las tablas se pueden revisar y ajustar (por German, Pablo o un astrólogo) sin programar.
- El resultado es reproducible y trazable: cada cálculo devuelve el detalle por nivel.
- La calidad del resultado depende de las tablas: hasta que alguien con criterio astrológico las valide, son una propuesta razonable, no la verdad.
