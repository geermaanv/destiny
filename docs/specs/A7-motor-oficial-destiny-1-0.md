# A7-motor-oficial-destiny-1-0 — Motor oficial de compatibilidad (Destiny 1.0, Pablo)

- **Estado**: implemented
- **Módulo**: B5 (reemplaza el motor provisorio de `B5-motor-sinastria.md`)
- **Owner de decisión de producto**: Pablo Maiztegui es la última palabra del modelo (ADR 0011); German Villamarin decide la integración.
- **Aprobada para implementación por**: German Villamarin, 2026-10-13.
- **Fuente**: paquete `DESTINY_1_0_PAQUETE_FINAL_MOTOR_UNIFICADO.zip` (13/10/2026): 8 calculadoras oficiales (`EJE1`…`E5-4 FINAL.xlsm`, ZIP SHA-256 `4a7cd3d3…09ac1e3`), motor de referencia en Python, especificación de preprogramación y auditorías de 1.500 sinastrías por modalidad. **Los Excel no entran al repo** (decisión de German): se guardan en `~/proyectos/destiny-fuentes/` y de ahí se generan las tablas.

## Problema

El motor actual (`synastry_v1.json`, "v1-provisoria") lo armamos nosotros a partir del diagrama, con tablas calibradas a mano. Pablo entregó el modelo oficial: ocho calculadoras con matrices, orbes, casas, expansiones y modificadores, más un motor de referencia que las reproduce. La app tiene que calcular **exactamente** lo mismo.

## Modelo (resumen; el detalle numérico vive en `app/synastry/config/synastry_v2.json`)

Entrada por persona: longitudes [0, 360) de Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno, Plutón, Nodo Norte Verdadero (y Medio, informativo), y **ASC y MC solo si la hora es exacta**. Nodo Sur = Nodo Norte Verdadero + 180°.

- **E1 Atracción** — 8 pares (Venus–Marte, ASC–Venus, ASC–Marte, Venus–Venus, Marte–Marte, Sol–ASC, Plutón–Venus, Plutón–Marte) en las dos direcciones; matriz de signos 12×12 + el aspecto más exacto dentro del orbe (11 aspectos), atenuado `(1 − d/orbe)^0,7`; casas por signo entero en las dos superposiciones; promedio ponderado por los pesos disponibles; expansión `centro + 1,45 × (base − centro)`.
- **E2 Afecto** — 8 pares con la Luna; orbes por grupo de aspecto y exponente por par; bonus de exactitud (orbe < 2°, impacto ≥ 20); casas.
- **E3 Comunicación** — 7 pares con Mercurio (Mercurio–Mercurio una sola vez); 5 aspectos; bonus de exactitud; casas 3, 9 y 11 contadas **desde el grado del ASC en sectores de 30°** (así está la planilla; pendiente de Pablo, ver abajo).
- **E4 Compromiso** — 9 pares con Saturno, Júpiter y Nodo Norte; bonus de exactitud (+40/−20); casas 7, 4, 10 y 5 por signo entero; expansión ×1,20.
- **E5-1…E5-4** — modificador por eje: Gran Trígono, Gran Cruz y contactos con ángulos recíprocos (solo si los dos tienen ASC/MC), con las combinaciones literales de las planillas; tope ±10. Se suma **después** de las expansiones; cada eje final se recorta a 0–100.
- **Tipos de relación** (total ponderado de E1–E4): ocasional 70/10/15/5 · pareja 25/25/25/25 · amistad 10/35/40/15 · laboral (Profesional) 10/10/40/40.
- **Modalidades**: completa+completa, completa+aproximada, aproximada+aproximada. Un solo motor: lo que no se puede calcular (ASC, MC, casas) se omite y el peso se redistribuye. **E4 en modo reducido** se neutraliza hacia 50: `50 + cobertura/100 × (E4 − 50)` (experimental de Pablo, se aplica como en su motor).
- **Visualización**: entero `floor(x + 0,5)`; internamente sin redondeos.

## Datos de nacimiento

- Franjas de Pablo (reemplazan las 4 nuestras): madrugada 00–05 (02:30), mañana 05–11 (08:00), mediodía 11–14 (12:30), tarde 14–19 (16:30), noche 19–24 (21:30). Se calcula con la hora del punto medio y **sin ASC, MC ni casas**.
- **No sabe ni la franja** (decisión de German): se calcula como franja mediodía (12:30), aproximada.
- Las posiciones se siguen calculando con `astronomy-engine` (MIT; no Swiss Ephemeris por licencia). Se agrega el **Nodo Norte Verdadero y Medio** (fórmulas de Meeus). Las posiciones tienen que coincidir con las de las auditorías de Pablo (Swiss Ephemeris/Moshier).

## Comportamiento en la app

- Descubrir, la explicación con IA, el panel del chat y la invitación usan este motor. Ejes: E1 = atracción, E2 = afecto, E3 = comunicación, E4 = compromiso. Lo que ve la persona no cambia de forma (4 ejes + total + "aproximado").
- La explicación usa los contactos más fuertes que encontró el motor (`detalle[eje].aspectos_encontrados`), como antes.
- Cambia la versión de tablas → la caché de explicaciones se regenera sola.
- El motor provisorio v1 y `scripts/build_synastry_config.py` se eliminan (quedan en el historial de git).

## Puntos abiertos (los decide Pablo; mientras tanto, como en su motor)

- E3: casas desde el grado del ASC vs. signo entero.
- E4: Juno (opcional; hoy no se informa).
- Tolerancia extra de 0,1° en los orbes y doble aspecto por par (propuestas en su especificación; no aplicadas).
- Modo reducido: la redistribución de pesos y la neutralización de E4 son experimentales.
- El porcentaje es un índice del modelo, no una probabilidad.

## Casos de prueba

En `apps/api/tests/test_a7_motor_oficial.py`. Referencias: muestra de las auditorías de Pablo en `tests/fixtures/motor_oficial_casos.json` (posiciones de entrada y resultados esperados de su motor) y los 3 resultados de demostración del paquete.

1. **Tablas completas**: `synastry_v2.json` trae los pesos de E1 (suman 100), E2 y E3 (suman 1), E4 (suman 100), las 8 matrices de E1, y las combinaciones de Gran Trígono y Gran Cruz de cada E5.
2. **E1–E4 base** coinciden con el motor de Pablo (diferencia < 1e-8) en los casos de muestra, en las 3 modalidades.
3. **E5** (Gran Trígono, Gran Cruz, angular y modificador final) coincide en las 3 modalidades, incluyendo casos donde cada patrón está activo.
4. **Ejes integrados** (base + E5, recortados) coinciden.
5. **Demo del paquete** con neutralización de E4: ejes finales, globales por tipo y visibles iguales a los de `06_EJECUCIONES_VERIFICADAS` para las 3 modalidades.
6. **Cobertura E4**: 100 / 83 / 66 según la modalidad, y la fórmula de neutralización.
7. **Simetría**: invertir A y B da los mismos ejes.
8. **Carta sin hora exacta** no tiene ASC ni MC; Nodo Sur = Nodo Norte + 180.
9. **Posiciones**: nuestra carta (fecha, hora, lugar) coincide con las posiciones de las auditorías (planetas < 0,01°; nodos < 0,05°; ASC y MC < 0,02°).
10. **Franjas**: guardar datos con una franja usa su punto medio y queda aproximado; sin hora ni franja usa 12:30 aproximado.
11. **Tipos de relación**: el total usa los pesos oficiales (ocasional 70/10/15/5, laboral 10/10/40/40).
12. **Parametrizable**: cambiar un número del JSON cambia el resultado sin tocar código.
