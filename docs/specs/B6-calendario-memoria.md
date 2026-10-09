# B6-calendario-memoria — Calendario de memoria

- **Estado**: implemented
- **Módulo**: B6
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Vista mensual con tránsitos clave marcados; al tocar un día, cruzar la línea de tiempo astrológica con anotaciones de vida real del usuario.

## Puntos abiertos (no bloquean v1)

- Integración de actividades en el calendario (qué tipo de actividades sugiere la app, de dónde vienen) — `BACKLOG.md` P0. **Fuera de alcance de v1**: se implementa el calendario con tránsitos + anotaciones propias del usuario (texto libre). Las anotaciones "sugeridas por la app" (actividades) se agregan en una iteración posterior, cuando esté definida la fuente de esas sugerencias.

## Requisitos funcionales

- Vista mensual con los días que tienen tránsitos clave marcados visualmente.
- Al tocar un día: timeline de los eventos astrológicos de ese día (basado en la carta natal del usuario) + anotaciones propias que el usuario haya agregado.
- El usuario puede agregar una anotación de texto libre a cualquier día.

## Contrato de datos / API

```
GET /calendar/{year}/{month} -> [{ "date": "2026-10-12", "has_key_transit": true }]
GET /calendar/day/{date} -> {
  "transits": [{ "aspect": "Luna llena en Libra", "time": "14:22" }],
  "annotations": [{ "text": "...", "created_at": "..." }]
}
POST /calendar/day/{date}/annotations { "text": "..." }
```

## UX / Flujo

1. Vista mensual, días con tránsito clave destacados.
2. Tap en un día → timeline de tránsitos + anotaciones propias, con opción de agregar una nueva.

## Actualización 2026-10-08 (idea de German)

- Debajo del calendario, **"Próximos eventos"**: los próximos 10 tránsitos importantes desde hoy, sin tener que tocar cada día. Los días seguidos con el mismo tránsito se agrupan en un evento. Cada evento tiene un título y una frase en lenguaje simple (ej. "Día armónico — Todo fluye más fácil…") y marca si el usuario tiene notas. Tocarlo abre el día.
- Calendario con mes y año, flechas para cambiar de mes, días de la semana (arranca en lunes), hoy destacado y leyenda.
- API: `GET /calendar/upcoming?profile_id=&from=&limit=10`; el detalle del día suma `title` y `text` del tránsito.

## Casos de prueba

Tests automáticos en `apps/api/tests/test_b6_calendario.py` (correr: `cd apps/api && .venv/bin/pytest`).

| # | Caso | Test |
|---|---|---|
| 1 | Mes completo | `test_mes_completo` |
| 2 | Próximos 10 eventos desde la fecha | `test_proximos_10_eventos_desde_la_fecha` |
| 3 | Notas del día y marca en eventos | `test_notas_del_dia_y_marca_en_eventos` |
| 4 | Calendario de otro está prohibido | `test_calendario_de_otro_esta_prohibido` |

## Criterios de aceptación

- [ ] Los tránsitos mostrados se calculan a partir de la carta natal real del usuario (A1), no son genéricos.
- [ ] El usuario puede crear, ver y (al menos) listar sus anotaciones por día.
- [ ] No hay anotaciones "sugeridas por la app" en v1 (ver fuera de alcance).

## Fuera de alcance

- Anotaciones/actividades sugeridas por la app (integración de actividades, pendiente de definición).
