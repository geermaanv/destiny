# A5-sesion — Sesión con WhatsApp

- **Estado**: draft
- **Módulo**: A5 (nuevo, Módulo A)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: —

## Problema

Hoy el perfil viaja en la URL (`?profileId=`): si se cierra el navegador se pierde el acceso, cualquiera con el link entra como esa persona, y no hay forma de "volver a entrar". La verificación por WhatsApp ya prueba quién es el usuario: se usa como login, sin contraseñas.

## Requisitos funcionales

1. **Al verificarse** (A3) el navegador queda con la sesión iniciada: cookie segura (`HttpOnly`, `SameSite=Lax`, `Secure` en https) que dura **90 días**.
2. **"Ya tengo cuenta"**: desde la pantalla de inicio, mismo mecanismo que la verificación (link `wa.me` con código). Si el número tiene cuenta, entra; si no, ofrece crear una.
3. **Duplicado → "Seguir con mi cuenta"** (A3) también deja la sesión iniciada en la cuenta existente.
4. **Solo el navegador que pidió el código puede tomar la sesión**: al pedir el código se le entrega un "comprobante" secreto de un solo uso; la sesión se entrega a quien presente ese comprobante una vez que llegó el mensaje de WhatsApp. Saber el `profileId` no alcanza.
5. **Las pantallas de la app** (Home, Descubrir, Chat, Calendario, Invitar, Perfil) usan la sesión; se saca `?profileId=` de sus links. Sin sesión → pantalla de inicio.
6. **Protección en la API**: una vez que un perfil está verificado, editarlo o ver sus datos completos requiere su sesión. Otros usuarios solo ven los datos públicos (A4). El onboarding (antes de verificar) sigue funcionando sin sesión.
7. **Cerrar sesión** desde "Mi perfil".
8. **Pantalla de inicio** (`/`): con sesión → Home; sin sesión → logo + "Empezar" + "Ya tengo cuenta".

## Contrato de datos / API (borrador)

```
POST /profiles/{id}/verification/whatsapp  -> suma "claim_token" (solo lo ve el navegador que lo pidió)
POST /sessions/claim       { claim_token }   -> Set-Cookie (si el código ya fue verificado)
POST /sessions/login       -> { login_id, code, wa_link, claim_token }   ("Ya tengo cuenta")
GET  /sessions/login/{id}  -> { status: pendiente|listo|sin_cuenta }
GET  /me                   -> perfil propio (o 401)
POST /sessions/logout      -> borra la sesión
```

Modelo: tabla `sessions` (token guardado como hash, `profile_id`, vence a los 90 días). Los códigos de WhatsApp pasan a servir para "verificar" o "entrar".

## Criterios de aceptación

- [ ] Después de verificarse, cerrar y abrir el navegador mantiene la sesión.
- [ ] "Ya tengo cuenta" con un número verificado entra a esa cuenta; con un número sin cuenta ofrece registrarse.
- [ ] Conocer el `profileId` de otro no permite entrar ni editar su perfil.
- [ ] Cerrar sesión vuelve a la pantalla de inicio.
- [ ] Ningún link de la app lleva `profileId` en la URL.

## Fuera de alcance

- Varias sesiones administrables ("cerrar sesión en otros dispositivos").
- Login con email, contraseña o redes sociales.
