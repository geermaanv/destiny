# Pendientes con Pablo

`Destiny-Pendientes-con-Pablo.xlsx` junta lo que espera respuesta de Pablo:

- **Pendientes**: preguntas con opciones, qué pasa si no responde y una columna amarilla para la respuesta.
- **Tu día**, **Tu día por estilo**, **Mi carta · signos** y **Mi carta · casas**: los textos de `apps/api/app/content/transitos_v1.json` y `carta_v1.json`, con columnas OK/Corregir y Corrección.

Regenerar (necesita `openpyxl`):

```bash
python docs/referencias/pendientes-pablo/generar_planilla.py docs/referencias/pendientes-pablo/Destiny-Pendientes-con-Pablo.xlsx
```

Las correcciones de Pablo se pasan a mano a los JSON. Cuando apruebe Mi carta, hay que marcar `revisado_por_pablo: true`.
