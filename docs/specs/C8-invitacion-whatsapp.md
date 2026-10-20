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

## v2 — Invitación a comparar el test de personalidad (aprobada por German, 2026-10-12, implementada)

Segundo tipo de invitación, para **alguien que ya conocés** (pareja, amigo, socio, jefe).

Decisiones:
1. Al registrarse y verificarse por esta invitación, **quedan conectados automáticamente** (conexión aceptada; el invitado ya aceptó al entrar por el link).
2. Solo se puede mandar con **tu test de personalidad completo** (32/32): el mensaje dice "ya completé mi test".
3. El panel "Compatibilidad" está **en todos los chats** (ver `B7-chat-rompehielos.md`).

Flujo:
1. En Invitar se elige el tipo: **"Adelanto astrológico"** (v1, con su signo) o **"Comparar test de personalidad"** (sin signo).
2. Para el test se elige el **vínculo a mirar**: pareja, amistad, trabajo o casual (define los pesos de la comparación y queda guardado en la conexión).
3. Mensaje: "¡Hola Juan! Ya completé mi test de personalidad en Destiny ✨ Hacelo vos (son 32 preguntas) y vemos qué tan compatibles somos en atracción, afecto, comunicación y compromiso: <link>".
4. El invitado entra, se registra y se verifica → queda conectado con quien invitó → se le propone completar su test.
5. Quien invitó ve en Inicio el estado de sus invitaciones: enviada → se sumó (N/32) → completó el test (link al chat).

API v2:

```
POST /invitations { inviter_id, friend_name, kind: "astro" | "test", relationship?: pareja|amistad|laboral|ocasional, friend_sun_sign? }
     kind=test: 409 si mi test no está completo; no pide signo.
GET  /invitations/{ref}                -> suma kind, inviter_name, relationship
POST /invitations/{ref}/accept         -> (sesión del invitado) crea la conexión aceptada con quien invitó; idempotente
GET  /invitations/mine?profile_id=     -> mis invitaciones con estado: enviada | registrado | test_completo (+ match_id)
```

Modelo: `Invitation` suma `kind`, `relationship`, `invitee_profile_id`, `accepted_at`; `friend_sun_sign` pasa a opcional. `Match` suma `relationship` y `source` (`descubrir` | `invitacion`).

### Casos de prueba v2

Tests en `apps/api/tests/test_c8_invitacion_test.py` (todos en verde).

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Invitar a comparar el test sin tener el test completo | 409 |
| 2 | Invitar a comparar el test con el test completo | 201, mensaje "Ya completé mi test…", sin pedir signo |
| 3 | Invitación astrológica sin signo | 422 (el signo sigue siendo obligatorio para ese tipo) |
| 4 | Vínculo inválido | 422 |
| 5 | El link muestra quién invita, el tipo y el vínculo | `kind`, `inviter_name`, `relationship` |
| 6 | El invitado verificado acepta | Conexión aceptada entre los dos con el vínculo elegido; repetir no duplica |
| 7 | Aceptar sin sesión, o aceptar la propia invitación | 401 / 409 |
| 8 | Estado de mis invitaciones | enviada → registrado → test_completo, con el id del chat |

## Corrección 2026-10-12

- El adelanto usa el Sol natal con la hora local real de quien invita (antes la tomaba como UTC).
- La **revelación** usa el motor de sinastría (el mismo total que Descubrir, con el vínculo de la invitación o Pareja), en vez del cálculo simple Sol–Sol.

## Actualización 2026-10-08

- La pantalla explica qué recibe el amigo y muestra **el mensaje exacto** antes de mandarlo ("Así le va a llegar a…"); botón "Enviar por WhatsApp" e "Invitar a otra persona".
- El mensaje habla en primera persona (lo manda quien invita desde su WhatsApp): "¡Hola Juan! Te invito a Destiny…". La API devuelve `message` además de `whatsapp_url`.
- El link usa `WEB_BASE_URL` (en `apps/api/.env`): con el túnel, tiene que ser la URL pública.

## Casos de prueba

Tests automáticos en `apps/api/tests/test_c8_invitacion.py` (correr: `cd apps/api && .venv/bin/pytest`).

| # | Caso | Test |
|---|---|---|
| 1 | Invitación arma mensaje en primera persona | `test_invitacion_arma_mensaje_en_primera_persona` |
| 2 | Invitar en nombre de otro está prohibido | `test_invitar_en_nombre_de_otro_esta_prohibido` |
| 3 | Invitado ve el adelanto y despues la revelación | `test_invitado_ve_el_adelanto_y_despues_la_revelacion` |
| 4 | Invitaciones viejas con gemini siguen funcionando | `test_invitaciones_viejas_con_gemini_siguen_funcionando` |

## Criterios de aceptación

- [ ] Generar una invitación no requiere hora/lugar de nacimiento del amigo, solo nombre + signo solar.
- [ ] El link con `ref_id` precarga el onboarding del invitado (no arranca desde cero).
- [ ] Cada invitación es trackeable a su `ref_id` para medir el canal de adquisición.

## Fuera de alcance

- Diseño visual final del reporte parcial (hereda el punto general de estética del Hub, iterable).

## v3 — Gancho en el mensaje (German, 2026-10-13)

Los dos mensajes de invitación arrancan con el gancho de Destiny después del saludo: "¡Hola {nombre}! ¿Por qué con algunas personas fluye y con otras no? …" (ver `VISION.md`). Caso de prueba: los dos mensajes empiezan con el saludo y el gancho, y mantienen el resto (signo o test, y el link).

**Corrección (revisión nocturna, 2026-10-14)**: un link de invitación vencido o mal copiado mostraba "Cargando..." para siempre; ahora dice que no es válido y ofrece "Conocer Destiny".

**Cambio posterior (2026-10-20, spec C12)**: invitar pasa a ser un solo formulario (nombre y signo opcional) con el mensaje en vivo. Ya no se elige el tipo ni el vínculo, ni hace falta tener el test completo: el mensaje suma el adelanto si hay signo y la comparación del test si quien invita lo completó; el vínculo sale de su "¿Qué buscás?".
