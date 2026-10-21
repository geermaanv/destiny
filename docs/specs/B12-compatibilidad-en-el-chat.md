# B12-compatibilidad-en-el-chat — Compatibilidad abierta, clara y sin botones en el chat

- **Estado**: implemented
- **Módulo**: B7 (chat) + B9 (número global)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 (bocetos v1 y v2; "B": número global que resume todo; primero el número y después las barritas; tabla solo para mostrar).

## Problema

En el chat, la compatibilidad arrancaba cerrada, y los botones Pareja / Amistad / Trabajo / Casual solo movían el porcentaje de arriba (los ejes son los mismos para todos los vínculos), lo que no se entendía.

## Puntos abiertos

Ninguno. El número global sigue siendo provisorio (ADR 0014) hasta que Pablo defina los pesos entre sistemas.

## Requisitos funcionales

- El bloque de compatibilidad está **siempre abierto**.
- **Arriba, un número que resume todo**: el promedio de los globales de los cuatro vínculos (cada global, como en B9: promedio de astrología y test con los pesos de Pablo para ese vínculo). No cambia.
- **Ejes** (Química, Afecto, Comunicación, Compromiso): en cada fila, primero el total del eje (promedio de los sistemas), después cada sistema con su número y una barra de 5 tramos de 20 %. Numerología con "—" hasta que exista.
- **Tabla**, sin título y sin botones: cada vínculo con su % global y el detalle de astrología, test y numerología. Solo se muestra.
- Los ejes no dependen del vínculo; la tabla muestra cómo cambia el total según cuánto pesa cada eje.

## Contrato de datos / API

`GET /matches/{id}/compatibility/summary` (solo los dos participantes, conexión aceptada):

```json
{
  "global_pct": 59,
  "axes_global": {"atraccion": 56, "afecto": 45, "comunicacion": 64, "compromiso": 69},
  "systems": {"astrologia": {"total": 53, "axes": {...}}, "personalidad": {"total": 64, "axes": {...}} | null},
  "por_vinculo": [{"vinculo": "pareja", "global_pct": 58, "astrologia": 53, "personalidad": 64}, ...],
  "approximate": false
}
```

`systems` trae los ejes (iguales para todos los vínculos); los totales de cada vínculo van en `por_vinculo`.

## Casos de prueba (`apps/api/tests/test_b12_compatibilidad_en_el_chat.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Los cuatro vínculos | Cada uno con su global = promedio de astrología y test, como en Círculo |
| 2 | Número que resume todo | `global_pct` = promedio de los cuatro globales |
| 3 | Sin test | `personalidad` null y cada global es la astrología |
| 4 | Solo los participantes | Un tercero no lo ve |
| 5 | Conexión pendiente | 409 |
| 6 | "Fuerte en…" de la tarjeta de Círculo | Sale del eje combinado más fuerte y es igual para cualquier vínculo |

## Criterios de aceptación

- [x] Los casos pasan.
- [x] Chat con el bloque abierto, filas con número y barras de 5 tramos, tabla sin botones.

## Fuera de alcance

Pesos de Pablo entre sistemas (ADR 0014), numerología.

**Implementación**: cálculo compartido con Círculo en `app/compat_summary.py` (el motor ya calculaba los cuatro vínculos en una pasada; ahora los devuelve en `totales_por_vinculo`). Círculo usa el mismo número global (decisión de German: "en Círculo también el número global, hay que simplificar entender la compatibilidad"). La grilla de ejes (total primero, número y barra de 5 tramos por sistema) es la misma en Círculo y en el chat. El botón "Quiero pasar a WhatsApp" pasa a ser verde relleno, igual al de Invitar.

**Ajuste (2026-10-20, German)**: la tabla de vínculos va en la misma grilla que los ejes (mismas columnas y letra): Total y Global en la misma columna, y los números de cada sistema alineados.

**Ajuste (2026-10-20, German)**: en la tabla de vínculos se resaltan el **nombre y el Global** del vínculo más alto, en el mismo color (los empatados también; si todos dan igual, ninguno). Los demás Global van en el tono de los otros números. Se probaron flechas ▲/▼ y números en dorado: metían ruido y corrían la alineación. Sin barras en la tabla: las diferencias entre vínculos son chicas y el número se lee mejor.

**Ajuste (2026-10-20, German: "¿por qué cambia? no hace falta")**: el "Fuerte en…" de la tarjeta sale del eje combinado más fuerte (antes, de los ejes que más pesan en el vínculo elegido). Así, cambiar entre amistad, trabajo y casual no cambia la lista; la web solo la vuelve a pedir al entrar o salir de pareja (filtro de género) y sin parpadear.
