# A3-verificacion-identidad — Verificación de identidad mandatoria

- **Estado**: implemented (v1 — verificación por WhatsApp, en modo mock hasta tener cuenta de Meta; v2 selfie/video pospuesta)
- **Módulo**: A3
- **Owner de decisión de producto**: Pablo Maiztegui (los puntos abiertos abajo siguen siendo suyos)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Historial

- **2026-10-07 (versión original)**: selfie/video en vivo vía vendor de KYC (Persona, Onfido, Veriff, Didit) + detección de duplicado de hardware. Implementada con un adapter mock (`app/adapters/kyc.py`, ADR 0006), sin vendor real.
- **2026-10-07 (esta versión)**: para el MVP v1 la verificación pasa a ser **por WhatsApp**, sin costo. Motivo: no gastar en verificaciones mientras el MVP es 100% gratis y la métrica es retención. **La idea de selfie/video en vivo se mantiene para próximas versiones** (ver "v2" abajo) — no se descarta, se pospone. Ver ADR `0008-verificacion-whatsapp.md`.

## Problema

Bloquear el acceso a descubrimiento hasta que el usuario demuestre que es una persona real con un número de teléfono propio, y que ese número no tiene ya otra cuenta. Sigue siendo mandatorio y previo (no opcional y posterior como en la competencia).

Lo que v1 **sí** garantiza: una cuenta por número de WhatsApp real.
Lo que v1 **no** garantiza: que la persona de las fotos sea quien usa la cuenta — eso lo resuelve la selfie/video en vivo de v2.

## Puntos abiertos (no bloquean v1)

- Pablo confirma el cambio de selfie/video a WhatsApp para v1 — `BACKLOG.md` P0.
- Número de teléfono dedicado para Destiny y titular de la cuenta de Meta Business (persona o empresa) — operativo, no bloquea código: se desarrolla con el modo mock.
- Copy de la pantalla y del mensaje prellenado — v1 usa copy borrador.
- Proveedor de KYC para v2 (Persona, Onfido, Veriff, Didit) — sigue abierto en `BACKLOG.md` P0 / ADR `0006-kyc-adapter.md`.

## v1 — Verificación por WhatsApp ("al revés")

El usuario le escribe a Destiny, en vez de que Destiny le mande un código. Los mensajes que inicia el usuario no tienen costo en la WhatsApp Cloud API de Meta (confirmar en la página de precios de Meta antes de salir a producción, el esquema cambia seguido).

### Flujo

1. En `/onboarding/verificacion` el usuario ve "Verificar con WhatsApp" + aviso de consentimiento (usamos su número para verificar que es una persona real; no se muestra a otros usuarios).
2. Al tocar el botón, el front pide un código a la API y abre `https://wa.me/<numero_destiny>?text=Mi%20código%20Destiny%3A%20<codigo>` (mismo mecanismo de link que `C8-invitacion-whatsapp.md`).
3. El usuario envía el mensaje desde su WhatsApp.
4. Meta llama al webhook de la API con el mensaje. La API extrae el código, lo asocia al perfil y toma el número del remitente (`from` / `wa_id`) como el teléfono verificado.
5. El front consulta el estado cada pocos segundos (polling) mientras espera. Al resolver:
   - `verificado` → Home (`/home`), o la revelación de compatibilidad si el onboarding viene con `ref` (C8), igual que hoy.
   - `duplicado_detectado` → pantalla de error: ese número ya está asociado a otra cuenta.
   - Código vencido → botón para generar uno nuevo.
   - Pedir un código nuevo después de `duplicado_detectado` (ej. "Probar con otro número") vuelve el perfil a `pendiente`.

### Requisitos funcionales

- Estados de verificación: se reutilizan los existentes. v1 usa `pendiente` → `verificado` | `duplicado_detectado`. (`en_revision` y `rechazado` quedan para v2.)
- Código: 6 dígitos, de un solo uso, vence a los 15 minutos. Generar uno nuevo invalida el anterior del mismo perfil.
- Un número de teléfono solo puede estar verificado en **un** perfil. Si llega un código válido desde un número ya verificado en otro perfil → `duplicado_detectado`.
- Mensajes que no contienen un código válido y vigente se ignoran (no cambian ningún estado).
- El teléfono se guarda normalizado (formato E.164) y **nunca** se expone en endpoints que vean otros usuarios (`/discover`, chats, invitaciones).
- Acceso a `/discover` bloqueado mientras el estado no sea `verificado` (sin cambios respecto de hoy).

### Contrato de datos / API

Modelo:

- `Profile`: suma `phone_e164` (único, nullable) y `verification_method` (`whatsapp` en v1; `kyc_video` en v2).
- Nueva tabla `phone_verification_codes`: `profile_id`, `code`, `expires_at`, `used_at`.

Endpoints:

```
POST /profiles/{id}/verification/whatsapp
  -> { "code": "482913", "wa_link": "https://wa.me/...", "expires_at": "..." }

GET  /profiles/{id}/verification
  -> { "status": "pendiente|verificado|duplicado_detectado", "method": "whatsapp" }   (ya existe; suma "method")

GET  /webhooks/whatsapp    -> handshake de Meta (hub.mode, hub.verify_token, hub.challenge)
POST /webhooks/whatsapp    -> mensajes entrantes; valida la firma X-Hub-Signature-256 con el app secret
```

Configuración (`apps/api/.env`):

```
WHATSAPP_BUSINESS_NUMBER=   # número de Destiny, para armar el link wa.me
WHATSAPP_VERIFY_TOKEN=      # token propio para el handshake del webhook
WHATSAPP_APP_SECRET=        # para validar la firma de Meta
```

### Modo desarrollo (mock)

Mismo patrón que los otros adapters (KYC, explainer, icebreaker): **sin credenciales de WhatsApp configuradas** y con `ENVIRONMENT=development`, el webhook acepta payloads sin firma y la pantalla muestra un botón "Simular envío (dev)" que le pega al webhook con un payload de prueba. Así el flujo completo se prueba sin cuenta de Meta.

### Requisitos externos (para salir del mock)

- Cuenta de Meta Business + app con el producto WhatsApp (alta gratuita; la verificación del negocio puede tardar días).
- Un número dedicado que **no** esté usado en la app común de WhatsApp.
- URL pública para el webhook. En el setup actual (ADR 0007) es el túnel `ngrok`; conviene un dominio fijo para no reconfigurar el webhook en Meta cada vez que cambia la URL.

### Runbook de alta en Meta (probado 2026-10-07)

1. developers.facebook.com → Crear app → caso de uso "Conectarte con los clientes a través de WhatsApp" → portfolio comercial (sin verificar alcanza). Una cuenta de Facebook recién creada tiene que esperar ~1 h antes de poder crear el portfolio.
2. Paso 2 → Configurar webhooks: URL `https://<dominio>/api/webhooks/whatsapp` + `WHATSAPP_VERIFY_TOKEN`; confirmar que el campo `messages` quede suscrito.
3. Configuración de la app → Básica → Clave secreta → `WHATSAPP_APP_SECRET` en `apps/api/.env` (desde ahí el webhook exige firma y se apaga el mock).
4. **Suscribir la cuenta de WhatsApp Business a la app** — el dashboard no lo hace solo, y sin esto solo llegan los "Probar" del dashboard, no los mensajes reales: `POST https://graph.facebook.com/v25.0/<WABA_ID>/subscribed_apps` con un token de acceso (el temporal del Paso 1 alcanza). Verificar con `GET` del mismo endpoint que aparezca la app propia.
5. No hace falta: medio de pago (es para mensajes iniciados por la empresa), verificación del negocio, ni publicar la app.

Particularidad del **número de prueba** de Meta (+1 555…): un usuario no puede iniciar el chat con él (WhatsApp dice que "no está en WhatsApp"). Para probar, primero se manda desde el dashboard (Paso 1) un mensaje de plantilla al celular de prueba, y después se responde en ese chat con el código. Con la línea real no pasa.

### Criterios de aceptación

- [x] Un perfil no `verificado` no puede acceder a `/discover`.
- [x] Enviar un código válido y vigente verifica el perfil y guarda su teléfono.
- [x] Un código vencido, ya usado o inexistente no cambia ningún estado.
- [x] Un número ya verificado en otro perfil termina en `duplicado_detectado`.
- [x] El webhook rechaza payloads con firma inválida cuando `WHATSAPP_APP_SECRET` está configurado.
- [x] El teléfono no aparece en ninguna respuesta de `/discover`, chats ni invitaciones.
- [x] El flujo completo (A1 → A2 → A3 → Home, y con `ref` de C8) funciona en modo mock.

### Fuera de alcance de v1

- Responderle al usuario por WhatsApp ("¡Listo, verificado!") — posible a futuro, se evalúa costo/beneficio.
- Mandar códigos desde Destiny al usuario (OTP saliente): tiene costo por mensaje.
- Verificación por email (descartada: no frena cuentas falsas).
- Rate limiting de generación de códigos — sumar antes de abrir a usuarios fuera del equipo.
- Cambio de número de teléfono de un perfil ya verificado.

## v2 — Selfie/video en vivo (próximas versiones)

Se mantiene la idea original. Se suma **encima** de WhatsApp, no lo reemplaza:

- Captura de selfie/video en vivo vía vendor de KYC (detección de vida pasiva como punto de partida, para minimizar fricción).
- Detección de duplicado de hardware.
- Estados `en_revision` y `rechazado`, políticas de reintento/apelación.
- `verification_method` pasa a `kyc_video` (o se combinan ambos métodos).

El código ya está preparado: la interfaz `IdentityVerificationAdapter` y el `MockKYCAdapter` (`app/adapters/kyc.py`, ADR 0006) **se conservan** aunque v1 no los use en el flujo de onboarding. Activar v2 es enchufar un adapter real y volver a sumar el paso de captura en la pantalla.

Antes de v2: elegir vendor (decisión de Pablo), confirmar costos por verificación y revisar el tratamiento de datos biométricos (Ley 25.326 — consentimiento explícito; preferir que el vendor guarde la imagen y Destiny solo el resultado).
