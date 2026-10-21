# 0014 — Número global de compatibilidad provisorio: promedio simple de los sistemas

- **Estado**: aceptada como provisoria (German Villamarin, 2026-10-20). Pendiente de Pablo.

## Contexto

En la reunión de check del 2026-10-20 se decidió mostrar en Círculo un número global que combine astrología, test de personalidad y numerología, con un ponderador por defecto de Pablo que cada persona pueda ajustar. El ADR 0011 mostraba los sistemas solo por separado. Pablo todavía no definió cuánto pesa cada sistema en el global.

## Decisión

- Cada sistema se sigue calculando con el modelo de Pablo y sus pesos por tipo de vínculo (motor Destiny 1.0 y test v4): **no cambia ningún cálculo**.
- Hasta que Pablo defina los pesos entre sistemas, el **número global** es el promedio simple de los totales de los sistemas con dato. Para la grilla de ejes, cada eje combinado es el promedio simple de los sistemas con dato en ese eje.
- La tarjeta de Círculo muestra el global; el detalle de cada sistema se sigue viendo por separado (ADR 0011).

## Consecuencias

- Cuando Pablo defina el ponderador, se reemplaza el promedio simple por sus pesos sin cambiar la pantalla. Después se suma el ajuste por persona (reunión del 2026-10-20).

**Actualización (2026-10-20, German)**: el número que se muestra (Círculo y chat) es el promedio de los globales de los cuatro vínculos, así no cambia según lo que se busca ("simplificar al usuario entender la compatibilidad; si quiere el detalle, lo ve"). El detalle por vínculo se muestra en la tabla del chat (spec B12).
