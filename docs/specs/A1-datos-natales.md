# A1-datos-natales — Carga de datos natales

- **Estado**: implemented
- **Módulo**: A1
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Anclar la identidad del usuario en su carta natal (fecha, lugar, hora de nacimiento), que es el input base de todo el producto (tránsitos, compatibilidad, pulso diario).

## Puntos abiertos (no bloquean v1)

- UX final de la pantalla (flujo exacto, copys, diseño visual) — `BACKLOG.md` P0. Para v1 se implementa un formulario simple y funcional; el pulido visual/de copy es iterable sin tocar el contrato de datos.

## Requisitos funcionales

- Capturar: fecha de nacimiento (obligatoria; el usuario debe ser mayor de 18), lugar de nacimiento (obligatorio, geocodificado a lat/lon + timezone), hora de nacimiento (opcional).
- Botón de escape **"No sé mi hora exacta"**: si el usuario no la sabe, se asigna `12:00` internamente y el perfil queda marcado con `hora_estimada: true`.
- Los datos natales se usan para calcular posiciones planetarias vía `astronomy-engine` (ADR 0005) — no se recalculan en cada pantalla, se persisten.

## Contrato de datos / API

```
POST /profiles/{id}/birth-data
{
  "birth_date": "1994-03-12",
  "birth_time": "14:30" | null,
  "birth_time_estimated": true | false,
  "birth_place": {
    "query": "Buenos Aires, Argentina",
    "lat": -34.6037,
    "lon": -58.3816,
    "timezone": "America/Argentina/Buenos_Aires"
  }
}
```

Si `birth_time` es `null`, el backend asigna `"12:00"` y fuerza `birth_time_estimated: true`.

## UX / Flujo

1. Fecha de nacimiento.
2. Lugar de nacimiento (autocomplete con geocoding).
3. Hora de nacimiento, con opción "No sé mi hora exacta".
4. Confirmación y cálculo inicial de carta.

(Diseño visual y copys finales: se iteran sin bloquear la implementación funcional.)

## Geocodificación (implementada 2026-10-07, ADR 0009)

- Se pide la **ciudad**, no la dirección: alcanza para el cálculo y evita datos sensibles.
- Autocomplete contra `GET /geocoding/search?q=` (Open-Meteo, Argentina primero; alias "CABA"/"Capital Federal"/"Bs As" → Buenos Aires). Hay que elegir una opción de la lista; se guarda el texto elegido + lat/lon + timezone.
- Si el geocoder no responde, se acepta el texto libre (sin coordenadas) para no bloquear el onboarding.
- Fecha en **tres desplegables (Día / Mes / Año)**, con el mes por nombre: el calendario nativo abría en el año actual y llegar al año de nacimiento era tedioso. Los días se ajustan al mes (ej. febrero 28/29).
- **Mínimo 18 años** (decisión 2026-10-07, habitual en apps de citas y exigido por las tiendas): la lista de años arranca 18 años atrás y llega a 100; el front y la API (`422`) rechazan menores.
- Al marcar "No sé mi hora exacta" se pregunta si recuerda la **franja del día** (madrugada 00–06, mañana 06–12, tarde 12–18, noche 18–24). Se usa el punto medio (03:00 / 09:00 / 15:00 / 21:00): el desvío máximo baja de 12 a 3 horas. Si no la recuerda, 12:00 (punto medio del día). En todos los casos `birth_time_estimated: true`. API: campo opcional `birth_time_period` en `POST /profiles/{id}/birth-data`; si viene la hora exacta, gana la hora exacta.
- Hora en **formato 24 h** con dos desplegables (hora 00–23 y minutos): el input de hora nativo usa AM/PM según el idioma del navegador y era fácil cargarla mal a mano.

## Casos de prueba

Tests automáticos en `apps/api/tests/test_a1_datos_natales.py` (correr: `cd apps/api && .venv/bin/pytest`).

| # | Caso | Test |
|---|---|---|
| 1 | Hora exacta se guarda tal cual | `test_hora_exacta_se_guarda_tal_cual` |
| 2 | Sin hora se usan las 12 y queda estimada | `test_sin_hora_se_usan_las_12_y_queda_estimada` |
| 3 | Franja del día usa el punto medio | `test_franja_del_dia_usa_el_punto_medio` |
| 4 | Hora exacta gana sobre la franja | `test_hora_exacta_gana_sobre_la_franja` |
| 5 | Menores de 18 se rechazan | `test_menores_de_18_se_rechazan` |
| 6 | Con 18 años se acepta | `test_con_18_anios_se_acepta` |
| 7 | Se guardan coordenadas y zona horaria | `test_se_guardan_coordenadas_y_zona_horaria` |
| 8 | Búsqueda de ciudad devuelve coordenadas y zona horaria | `test_busqueda_de_ciudad_devuelve_coordenadas_y_zona_horaria` |
| 9 | Búsqueda de ciudad pide al menos 2 letras | `test_busqueda_de_ciudad_pide_al_menos_2_letras` |
| 10 | Alias CABA se traduce a buenos aires | `test_alias_caba_se_traduce_a_buenos_aires` |

## Criterios de aceptación

- [x] Perfil sin hora exacta queda con `birth_time_estimated: true` y `birth_time: "12:00"`.
- [x] Perfil con hora exacta guarda la hora real y `birth_time_estimated: false`.
- [x] Los tres campos (fecha, lugar, hora) son suficientes para que el motor astrológico calcule posiciones planetarias.

## Fuera de alcance

- Diseño visual final / copy final de la pantalla (se itera después, no bloquea).
- Validación de calidad del geocoding.
