# A1-datos-natales — Carga de datos natales

- **Estado**: implemented
- **Módulo**: A1
- **Owner de decisión de producto**: Pablo Maiztegui (los puntos abiertos abajo siguen siendo suyos)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Anclar la identidad del usuario en su carta natal (fecha, lugar, hora de nacimiento), que es el input base de todo el producto (tránsitos, compatibilidad, pulso diario).

## Puntos abiertos (no bloquean v1)

- UX final de la pantalla (flujo exacto, copys, diseño visual) — `BACKLOG.md` P0. Para v1 se implementa un formulario simple y funcional; el pulido visual/de copy es iterable sin tocar el contrato de datos.

## Requisitos funcionales

- Capturar: fecha de nacimiento (obligatoria), lugar de nacimiento (obligatorio, geocodificado a lat/lon + timezone), hora de nacimiento (opcional).
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

(Diseño visual y copys finales: iterar con Pablo en paralelo, sin bloquear la implementación funcional.)

## Criterios de aceptación

- [ ] Perfil sin hora exacta queda con `birth_time_estimated: true` y `birth_time: "12:00"`.
- [ ] Perfil con hora exacta guarda la hora real y `birth_time_estimated: false`.
- [ ] Los tres campos (fecha, lugar, hora) son suficientes para que el motor astrológico calcule posiciones planetarias.

## Fuera de alcance

- Diseño visual final / copy final de la pantalla (se itera después, no bloquea).
- Validación de calidad del geocoding (proveedor de geocoding se define al implementar, no requiere decisión del founder).
