# C8-invitacion-whatsapp — Invitación por "resonancia parcial" (WhatsApp Link Generator)

- **Estado**: implemented
- **Módulo**: C8
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Canal principal de adquisición orgánica a costo cero: el usuario invita a un amigo con fricción mínima (solo nombre + signo solar), generando curiosidad con un reporte parcial bloqueado/borroso.

## Puntos abiertos

Ninguno bloqueante identificado. (La estética visual del reporte parcial hereda el punto general de "estética del Hub" en `BACKLOG.md` P0, pero no bloquea la mecánica.)

## Requisitos funcionales

- El usuario tipea nombre + signo solar de un amigo (sin hora/lugar — fricción mínima deliberada).
- La IA genera un reporte parcial de compatibilidad, con los datos más "jugosos" bloqueados/borrosos visualmente.
- Se genera un link único con `ref_id` que identifica la invitación.
- Un botón abre WhatsApp con mensaje pre-escrito personalizado + el link.
- Al abrir el link, el invitado entra directo al onboarding, pre-cargado para llegar al paso de revelación de compatibilidad mutua (sin pasar por todo el onboarding estándar desde cero).

## Contrato de datos / API

```
POST /invitations
{ "friend_name": "Flor", "friend_sun_sign": "Escorpio" }
-> { "ref_id": "abc123", "whatsapp_url": "https://wa.me/?text=...", "partial_report": { "teaser": "...", "locked_fields": [...] } }

GET /invitations/{ref_id} -> datos para precargar el onboarding del invitado
```

`ref_id` queda asociado al perfil que invita, para medir CAC orgánico por canal.

## UX / Flujo

1. Formulario mínimo: nombre + signo solar del amigo.
2. Preview del reporte parcial (con datos bloqueados/borrosos).
3. Botón "Compartir por WhatsApp" → abre WhatsApp con mensaje + link pre-armado.
4. El amigo abre el link → onboarding pre-cargado, directo a revelación de compatibilidad mutua al completar sus propios datos mínimos.

## Actualización 2026-10-08

- La pantalla explica qué recibe el amigo y muestra **el mensaje exacto** antes de mandarlo ("Así le va a llegar a…"); botón "Enviar por WhatsApp" e "Invitar a otra persona".
- El mensaje habla en primera persona (lo manda quien invita desde su WhatsApp): "¡Hola Juan! Te invito a Destiny…". La API devuelve `message` además de `whatsapp_url`.
- El link usa `WEB_BASE_URL` (en `apps/api/.env`): con el túnel, tiene que ser la URL pública.

## Criterios de aceptación

- [ ] Generar una invitación no requiere hora/lugar de nacimiento del amigo, solo nombre + signo solar.
- [ ] El link con `ref_id` precarga el onboarding del invitado (no arranca desde cero).
- [ ] Cada invitación es trackeable a su `ref_id` para medir el canal de adquisición.

## Fuera de alcance

- Diseño visual final del reporte parcial (hereda el punto general de estética del Hub, iterable).
