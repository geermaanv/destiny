# B9-circulo-v2 — Tarjeta con número global, columnas por sistema y distancia

- **Estado**: implemented
- **Módulo**: B5 (Descubrir / Círculo)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20, a partir de la reunión de check con Pablo (`docs/reuniones/2026-10-20-check-pablo.html`) y del boceto de German (una columna de barras por sistema y el promedio por eje a la derecha).

## Problema

En la reunión con Pablo se vio que la tarjeta de Círculo parece de app de citas (foto enorme), que para elegir a alguien hace falta ver el detalle de cada eje y que conviene un solo número que junte los sistemas. Además falta la distancia, que es un filtro importante.

## Puntos abiertos

Ninguno que bloquee. Default provisorio: el número global es un **promedio simple** hasta que Pablo defina los pesos de cada sistema (ADR 0014).

## Requisitos funcionales

### Número global (provisorio)
- **Cada sistema se calcula como hoy, con los pesos de Pablo según lo que buscás** (pareja, amistad, trabajo, casual): astrología = motor Destiny 1.0; test = total del test de Pablo (solo con los dos tests completos, como en su HTML).
- **Número global** = promedio simple de los totales de los sistemas que tienen dato. Ej.: para trabajo, astrología 58 y test 71 → global 64. Si cambiás lo que buscás, cambia, porque cambian los totales de cada sistema.
- La tarjeta muestra el global sin aclarar el vínculo: ya está elegido arriba en "¿Qué buscás?".
- **Ejes**: una columna por sistema con su puntaje por eje (Química ↔ Atracción E1, Afecto ↔ Emoción E2, Comunicación E3, Compromiso E4) y, a la derecha, el promedio simple de los sistemas con dato en ese eje. Es para mirar el punto que necesitás.
- Si la persona o quien mira no completó el test, el global es solo astrología ("Solo astrología"). Numerología no existe todavía: aparece como "pronto".
- Descubrir ordena por número global y la "compatibilidad mínima" se aplica sobre él.

### Sistemas en los filtros
- "Según qué sistema" (B8) pasa a ser **qué sistemas incluir**: astrología y test, los dos prendidos por defecto.
- Al apagar uno: aviso "Sin este sistema el resultado pierde precisión".
- Solo test: aparecen solo quienes lo hicieron; si quien busca no lo hizo → 409 (como en B8). Ninguno prendido → 422.
- "¿Qué buscás?" sigue definiendo los pesos de cada sistema y filtrando a quién ves (género en pareja, B8).

### Distancia
- "¿Dónde vivís?" con el mismo buscador de ciudades de los datos natales (ciudad con coordenadas). Se pide en Descubrir junto con la pregunta de género y se edita en Editar perfil.
- Filtro "a menos de X km": 5, 10, 25, 50, 100 o cualquier distancia.
- La tarjeta muestra "a N km" (redondeado; menos de 1 km se muestra como 1). **Nunca** se expone la ciudad ni las coordenadas de otra persona.
- Con el filtro de distancia puesto, quien no cargó dónde vive no aparece; sin filtro, aparece sin distancia. Si quien busca no cargó dónde vive y pone el filtro → 409.

### Tarjeta (web)
- Foto de 128 px a la izquierda; "Nombre, edad · signo · a N km"; "Fuerte en …"; número global grande con "Promedio de astrología y test" (o "Solo astrología").
- Grilla de ejes: una columna de barras por sistema (astrología, test, numerología "pronto") y el eje combinado a la derecha.
- El perfil de la persona muestra la misma grilla más grande, con la explicación.

## Contrato de datos / API

```
GET /discover?...&sistemas=astrologia,personalidad&max_km=25
POST /profiles/{id}/residence {query, lat, lon} → ProfileOut (sin lat/lon → 422)
```

Por candidato, además de lo de B8:

```json
{
  "compatibility_pct": 64,                 // = global_pct (compatibilidad hacia atrás)
  "global_pct": 64,
  "axes_global": {"atraccion": 55, "afecto": 48, "comunicacion": 70, "compromiso": 66},
  "systems": {
    "astrologia": {"total": 58, "axes": {"atraccion": 52, ...}},
    "personalidad": {"total": 71, "axes": {...}} | null
  },
  "distance_km": 4 | null
}
```

- `Profile`: `residence_label`, `residence_lat`, `residence_lon`. `ProfileOut` devuelve los propios.
- `sistema` (B8) se reemplaza por `sistemas`.

## Casos de prueba (`apps/api/tests/test_b9_circulo_v2.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Global con los dos sistemas | Global = promedio del total de astrología y del total del test; cada eje combinado, el promedio de los dos |
| 2 | Sin test | Global = total de astrología; `personalidad` es null |
| 3 | Los pesos de Pablo siguen valiendo | En cada vínculo, el total de cada sistema es el de su motor para ese vínculo y el global su promedio |
| 4 | Orden y mínimo por global | Ordenados por `global_pct`; `min_pct` filtra sobre él |
| 5 | Elegir sistemas | Solo astrología ignora el test; solo test excluye a quien no lo hizo; sin test propio → 409; ninguno → 422 |
| 6 | Guardar dónde vivo | Se guarda con coordenadas; sin coordenadas → 422 |
| 7 | Distancia | Muestra los km; `max_km` deja afuera a los lejanos y a quien no cargó dónde vive; sin filtro aparece sin distancia; sin ubicación propia + filtro → 409 |
| 8 | Privacidad | La respuesta de Descubrir no trae ciudad ni coordenadas de otros |

## Criterios de aceptación

- [x] Los 8 casos pasan; los tests de B8 se ajustan a `sistemas`.
- [x] Tarjeta y perfil como el boceto, en el celular.

## Fuera de alcance

Ponderador ajustable por persona y pesos de Pablo (cuando los defina), numerología, filtrar por intereses, ubicación por GPS o por barrio.

## Implementación (2026-10-20)

- API: `GET /discover` con `sistemas`, `max_km`, `global_pct`, `axes_global`, `systems` y `distance_km` (haversine); `POST /profiles/{id}/residence`. Columnas `residence_*` en `profiles` (base de desarrollo migrada a mano).
- Web: `components/SystemsGrid.tsx` (grilla por sistema, en la tarjeta y en el perfil), `components/PlaceField.tsx` (buscador de ciudades compartido con los datos natales), tarjeta con foto de 128 px, "¿Dónde vivís?" en Descubrir y en Editar perfil, filtros de sistemas (con aviso de precisión) y distancia.
- Colores de los sistemas: los de la app (dorado para astrología, violeta para el test), que cambian con el tema de cada persona.

**Cambio posterior (2026-10-20, spec B12, decisión de German)**: el número global ya **no depende de lo que buscás**: es el promedio de los globales de los cuatro vínculos (cada uno, promedio de los sistemas con los pesos de Pablo para ese vínculo), el mismo número en Círculo y en el chat. El total de cada sistema en la tarjeta también es su promedio de los cuatro vínculos. "¿Qué buscás?" sigue filtrando (género en pareja) y ordenando el test. Caso 3 reemplazado por "el global no depende del vínculo". Cálculo compartido en `app/compat_summary.py`.
