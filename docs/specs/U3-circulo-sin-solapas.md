# U3-circulo-sin-solapas — Círculo en una pantalla: franja de conexiones arriba de Descubrir

- **Estado**: implemented
- **Módulo**: transversal (web) + B7 (conexiones y chat)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 (boceto aprobado: "sí, avanzá").

## Problema

Círculo tenía dos solapas, Descubrir y Mis chats. Había que elegir antes de ver nada, "Mis chats" no dejaba ver que ahí estaban las solicitudes por responder, y con pocas conexiones era una pantalla casi vacía.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

- Se sacan las solapas. Círculo es una sola pantalla: arriba la franja **"Tus conexiones"** y debajo Descubrir.
- La franja (solo si tenés conexiones o solicitudes):
  - Primero, si hay solicitudes recibidas: **"N quieren conectar"** resaltado, lleva a la lista para aceptar o rechazar.
  - Después, las caras de tus conexiones aceptadas (las de mensajes más nuevos primero), con un **punto** si hay mensajes nuevos de la otra persona. Tocar una abre el chat.
  - Se desliza de costado; **"Ver todas →"** abre la lista completa (chats, solicitudes, esperando respuesta).
- Sin conexiones ni solicitudes, la franja no aparece.
- **Sin leer**: un chat tiene novedades si la otra persona escribió después de la última vez que lo abriste. El rompehielos de Destiny no cuenta. Abrir el chat lo marca como leído.

## Contrato de datos / API

- `Match`: `a_read_at`, `b_read_at` (cuándo abrió el chat cada uno).
- `GET /chats/{id}/messages` marca el chat como leído para quien lo pide.
- `ConnectionOut` suma `unread: bool`.

## Casos de prueba (`apps/api/tests/test_u3_circulo_sin_solapas.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | La otra persona escribe | `unread` true para mí, false para quien escribió |
| 2 | Abro el chat | `unread` pasa a false |
| 3 | Escribe de nuevo | Vuelve a true |
| 4 | Solo el rompehielos | No cuenta como novedad |

## Criterios de aceptación

- [x] Los 4 casos pasan.
- [x] Círculo sin solapas, con la franja y "Ver todas →"; sin conexiones no aparece.

## Fuera de alcance

Notificaciones push de mensajes, contador de mensajes sin leer en la barra.
