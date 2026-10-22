# Numerología — propuesta v0 (para que Pablo revise)

Borrador del tercer sistema de compatibilidad, pedido por German el 2026-10-22. **El modelo lo define Pablo (ADR 0011)**: esto es un punto de partida para que corrija, no está implementado en la app (en Círculo y el chat la columna "Numer." sigue en "pronto").

- **Planilla**: `Numerologia-Destiny-propuesta-v0.xlsx` (celdas amarillas editables; la hoja Calculadora recalcula al cambiar cualquier tabla). Generada con `generar_planilla.py`.
- **Solo con la fecha de nacimiento** (no se pide el nombre completo):
  - Camino de vida: día, mes y año reducidos, sumados y reducidos (se conservan 11, 22, 33).
  - Número del día: el día reducido (se conservan 11 y 22).
  - Para comparar, los maestros se leen como su base (11 → 2, 22 → 4, 33 → 6).
- **Comparación**: matriz base 9×9 simétrica (grupos clásicos 1-5-7, 3-6-9, 2-4-8; tensiones 4-5 y 1-8) → cada eje (Química, Afecto, Comunicación, Compromiso) se ajusta ±10 según la afinidad de los dos números con ese eje → 70 % camino de vida + 30 % número del día → total por vínculo con **los mismos pesos del motor Destiny 1.0**.
- **Verificación**: las fórmulas se evaluaron con la librería `formulas` contra una implementación de referencia en Python (mismos resultados en 2 ejemplos completos y en 7 fechas con maestros y reducciones múltiples).
- **Cuando Pablo lo apruebe** (o lo corrija): spec, tests con sus ejemplos, el modelo en un JSON de configuración y la columna "Numer." se enciende en Círculo, el chat y el número global.
