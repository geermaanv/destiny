# B7-chat-rompehielos — Conexión mutua, chat con rompehielos y paso a WhatsApp

- **Estado**: implemented (v2 híbrida, 2026-10-08)
- **Módulo**: B7
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## v2 — Conexión mutua + chat híbrido (decidido por German, 2026-10-08)

Lo que cambia respecto de v1 (donde "Match" abría un chat unilateral):

1. **Conexión mutua**: en Descubrir el botón es **"Conectar"** y manda una solicitud. La otra persona la ve en **"Conexiones"** y la acepta o rechaza. Si las dos personas se pidieron conexión, se acepta sola. El chat solo se abre con la conexión aceptada.
2. **Chat dentro de Destiny** para el primer contacto: arranca con el rompehielos de IA (v1) y se actualiza solo cada pocos segundos.
3. **"Pasar a WhatsApp"**: cualquiera de los dos lo propone; cuando **los dos aceptan**, cada uno ve un botón "Abrir WhatsApp con <nombre>" (link `wa.me` al número del otro con un saludo). **Antes de eso nadie ve el número de nadie.** Destiny registra que pasaron a WhatsApp (outcome para la métrica de retención).
4. **Bloquear**: cualquiera de los dos puede bloquear la conexión; se cierra el chat y no se puede volver a pedir.
5. **Pantalla "Conexiones"** en la navegación (reemplaza a "Invitar", que pasa a una tarjeta en Inicio): solicitudes recibidas, chats y solicitudes enviadas. Inicio avisa si hay solicitudes nuevas.

Estados de una conexión: `pendiente` → `aceptada` | `rechazada`; `bloqueada` desde cualquier estado.

API v2 (además de lo de v1):

```
POST /matches {profile_a_id (yo), profile_b_id}   -> crea la solicitud (o acepta si la otra persona ya la había pedido)
GET  /connections?profile_id=                     -> mis conexiones (recibidas, enviadas, aceptadas) con datos públicos del otro y último mensaje
GET  /matches/{id}?profile_id=                    -> detalle para el chat (otro perfil, estado, estado de WhatsApp)
POST /matches/{id}/accept | /reject | /block
POST /matches/{id}/whatsapp                       -> "quiero pasar a WhatsApp"; con los dos de acuerdo devuelve el link
```

Implementación: `app/routers/matches.py` (estados, `/connections`, accept/reject/block/whatsapp), `Match` suma `status`, `accepted_at`, `whatsapp_a_ok`/`whatsapp_b_ok`, `whatsapp_shared_at`, `blocked_by`. Web: botón "Conectar" en Descubrir, pantalla `/conexiones`, chat con encabezado, actualización cada 4 s, panel "Pasar a WhatsApp" y "Bloquear"; aviso de solicitudes y tarjeta "Invitá a un amigo" en Inicio. Los mensajes se cortan a 1000 caracteres.

Criterios v2:

- [x] "Conectar" no abre chat hasta que la otra persona acepta.
- [x] Solo los dos participantes ven el chat y solo con la conexión aceptada se puede escribir.
- [x] El número del otro aparece solo cuando los dos aceptaron pasar a WhatsApp.
- [x] Bloquear cierra el chat para los dos.

## Problema

Al generarse resonancia mutua, eliminar el "hola, ¿cómo estás?" inyectando automáticamente un disparador de conversación personalizado, gratis, basado en los aspectos más fuertes de ambas cartas natales.

## Puntos abiertos (no bloquean v1)

- Tonos/copies finales del chat y de los rompehielos generados — `BACKLOG.md` P0. **No bloquea v1**: se implementa con guía editorial borrador (misma lógica que `B5`, reutilizando el principio "nunca caja negra"), reemplazable sin tocar la mecánica de generación.

## Requisitos funcionales

- Cuando dos perfiles generan resonancia mutua (match), se crea el chat con un primer mensaje generado por IA ya insertado — no es el usuario quien lo escribe.
- El rompehielos se basa en los aspectos astrológicos más fuertes entre ambas cartas natales (mismo dato que alimenta la explicación de `B5`).
- Es gratis y automático — no requiere acción del usuario para generarse.

## Contrato de datos / API

```
POST /matches/{match_id}/icebreaker  (llamado automáticamente al crearse el match)
  input a Claude API: { "chart_a": {...}, "chart_b": {...}, "strongest_aspects": [...] }
  output: texto del primer mensaje del chat

GET /chats/{match_id}/messages -> incluye el mensaje inicial con sender = "system_icebreaker"
```

## UX / Flujo

1. Se genera el match (resonancia mutua).
2. El chat se abre ya con el mensaje rompehielos como primer mensaje.
3. El usuario responde directamente, sin pantalla de "hola" vacía.

## Criterios de aceptación

- [ ] Todo chat nuevo arranca con un mensaje generado por IA, nunca vacío.
- [ ] El rompehielos referencia aspectos astrológicos reales de ambas cartas (no es genérico/template fijo).
- [ ] La generación no le cuesta nada al usuario (gratis, acorde a la regla de MVP sin paywall).

## Fuera de alcance

- Tono/copy editorial final (iterable sin tocar la mecánica).
