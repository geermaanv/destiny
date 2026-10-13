# 0012 — Motor oficial de compatibilidad Destiny 1.0 (reemplaza las tablas provisorias)

- **Estado**: aceptada (German Villamarin, 2026-10-13). Reemplaza la [0010](./0010-motor-sinastria-config.md).

## Contexto

Pablo entregó el paquete DESTINY 1.0: las 8 calculadoras oficiales en Excel (E1–E4 y modificadores E5-1 a E5-4), un motor de referencia en Python, una especificación de preprogramación y auditorías de 1.500 sinastrías por modalidad. Por la ADR 0011, Pablo es la última palabra sobre el modelo: las tablas `v1-provisoria` que armamos a partir del diagrama quedan obsoletas.

## Decisión

- **Un solo motor y tres modalidades** (completa+completa, completa+aproximada, aproximada+aproximada), igual que el de referencia: sin hora exacta no se inventan ASC, MC ni casas, y el peso se redistribuye.
- **Las tablas se generan desde los Excel** con `apps/api/scripts/build_synastry_v2.py` → `app/synastry/config/synastry_v2.json`. Se leen los valores de las celdas en las mismas posiciones que usa el motor de referencia; no se edita el JSON a mano. Las reglas numéricas de los modificadores E5 también van en el JSON.
- **Los Excel no entran al repo** (decisión de German): viven en `~/proyectos/destiny-fuentes/` (ZIP SHA-256 `4a7cd3d3…09ac1e3`, registrado en el JSON). El JSON generado sí está en el repo público (decisión de German).
- **Fidelidad verificable**: `tests/test_a7_motor_oficial.py` compara contra 457 casos de las auditorías de Pablo y sus 3 demos (diferencia < 1e-8). Los casos se copian con `scripts/build_motor_fixtures.py`. No ejecutamos el código del paquete: su motor usa Swiss Ephemeris.
- **Posiciones con astronomy-engine** (ADR 0005, MIT), con el Nodo Norte verdadero (osculante, a partir del estado de la Luna) y medio (Meeus). Coinciden con las del paquete con menos de 0,01°.
- **Casas por signo entero**, como las planillas (la E3 usa sectores desde el grado del ASC, como su fórmula histórica).
- **Franjas de Pablo** (5) para quien no sabe la hora; sin franja, mediodía (12:30), siempre aproximado.
- **Pesos por tipo de relación** del motor: ocasional 70/10/15/5, pareja 25/25/25/25, amistad 10/35/40/15, laboral (Profesional) 10/10/40/40. Ya no se copian del test de personalidad (el test usa 60/10/25/5 en ocasional; anotado para Pablo).

## Consecuencias

- Si Pablo cambia una planilla: se copia el ZIP nuevo a `~/proyectos/destiny-fuentes/`, se corre `build_synastry_v2.py` y, si trae auditorías nuevas, `build_motor_fixtures.py`; los tests dicen si el motor sigue igual.
- Se eliminaron el motor v1, `synastry_v1.json` y `scripts/build_synastry_config.py` (quedan en git).
- Puntos abiertos que decide Pablo: E3 con casas desde el grado del ASC, Juno en E4, tolerancia extra de 0,1° y doble aspecto, y el modo reducido experimental (spec A7).
