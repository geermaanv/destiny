# A10-verificacion-opcional — Verificación por WhatsApp opcional (MVP)

- **Estado**: implemented
- **Módulo**: A (cambia A3 verificación y A5 sesión)
- **Aprobada para implementación por**: German Villamarin, 2026-10-14 ("para el MVP quiero desactivar la validación de WA para hacer más simple el onboarding"; aceptó las dos recomendaciones: Descubrir muestra no verificados con marca, y pasar a WhatsApp exige verificar).

## Problema

La verificación por WhatsApp es el último paso del registro y frena a mucha gente. Para el MVP, el registro tiene que terminar sin ella. Pero hoy la verificación también inicia la sesión, permite entrar desde otro dispositivo, da confianza en Descubrir y habilita "pasar a WhatsApp".

## Comportamiento

- **Interruptor** `VERIFICACION_OBLIGATORIA` (configuración, por defecto **apagado**). Prendido, todo vuelve a funcionar como en A3/A5.
- **Registro**: datos de nacimiento → tu carta → perfil → avisos → **listo**. Al terminar se inicia la sesión en el dispositivo, sin WhatsApp.
- **Prueba de dispositivo**: al crear el perfil, la API deja en el navegador una cookie segura (`destiny_device`, HttpOnly) con un token cuyo hash queda en el perfil. Solo ese navegador puede iniciar la sesión del perfil sin WhatsApp: saber el id del perfil no alcanza.
- **Perfil activo**: un perfil es "activo" si está verificado o si ya inició sesión al terminar el registro (`activated_at`). Un perfil activo solo lo puede tocar su dueño (sesión); antes solo los verificados estaban protegidos. Esto incluye **pedir un código de verificación**: si no, alguien podría verificar el perfil de otra persona con su propio teléfono y quedarse con la cuenta.
- **Descubrir y "en tu frecuencia"**: muestran los perfiles activos y completos (nombre y datos de nacimiento), verificados o no. Cada candidato trae `verificado` y la app muestra una marca **"Verificado"**.
- **Aceptar una invitación**: alcanza con un perfil activo.
- **Pasar a WhatsApp**: exige que quien lo pide esté verificado (hace falta su número). Si no, la app ofrece verificar.
- **Verificar después**: en Perfil, "Verificá tu WhatsApp" (si no está verificado), con sus beneficios: marca de verificado, entrar desde otro dispositivo y pasar a WhatsApp. Usa el mismo flujo de A3.
- **Aviso de respaldo**: a quien no verificó, en Perfil: "Tu cuenta vive en este dispositivo: verificá tu WhatsApp para no perderla".

## API

- `POST /profiles` también deja la cookie `destiny_device`.
- `POST /sessions/start` `{profile_id}` → 204 e inicia la sesión. 403 si `VERIFICACION_OBLIGATORIA` está prendido (`detail: "verificacion_obligatoria"`) o si el navegador no tiene la cookie del perfil; 409 si el perfil no está completo (sin nombre o sin datos de nacimiento).
- Modelo: `Profile.device_token_hash`, `Profile.activated_at` (nullables).

## Riesgos aceptados (MVP)

- Si alguien borra los datos del navegador sin haber verificado, pierde la cuenta (lo mitiga el aviso).
- Perfiles falsos o duplicados en Descubrir (grupo chico de prueba; la marca de verificado ayuda).
- Si al verificar después el número ya pertenece a otra cuenta verificada, sigue valiendo el flujo de A3 (seguir con la cuenta existente).
- **Cuentas descartables (agente breaker, 2026-10-22)**: como crear una cuenta es gratis y sin teléfono, con varias cuentas se pueden deducir las respuestas del test de otra persona, ubicarla a ~400 m y deducir su género y orientación ocultos (los límites por cuenta no frenan eso). **Decisión de German**: se acepta durante el piloto para facilitar las pruebas y la adopción; **en producción se pide la validación de WhatsApp (o algo similar)**, que deja una cuenta por teléfono y cierra el problema de raíz (interruptor `VERIFICACION_OBLIGATORIA` o verificación para usar Círculo).

## Casos de prueba (`apps/api/tests/test_a10_verificacion_opcional.py`)

1. Registro sin WhatsApp: crear perfil, datos, nombre y `POST /sessions/start` → sesión iniciada (`/me` responde).
2. Otro navegador (sin la cookie del perfil) no puede iniciar esa sesión → 403.
3. Perfil incompleto (sin nombre o sin datos) → 409.
4. Con `VERIFICACION_OBLIGATORIA` prendido → 403 `verificacion_obligatoria`.
5. Un perfil activo solo lo toca su dueño: sin sesión no se puede leer, editar ni pedir un código de verificación.
6. Descubrir muestra perfiles activos verificados y no verificados (con `verificado`), y no muestra registros abandonados.
7. Una persona activa sin verificar usa Hoy, Carta, Respuestas y Descubrir.
8. Pasar a WhatsApp sin estar verificado → 409.
9. Aceptar una invitación con un perfil activo sin verificar funciona.
10. "En tu frecuencia" cuenta los perfiles activos.

**Corrección (2026-10-14, reportado por German)**: entrar al registro (`/onboarding/datos-natales`) con una sesión iniciada creaba un perfil nuevo y volvía a pedir los datos; pasaba con el link corto de pruebas, que apunta ahí desde antes de que existiera la sesión (y TinyURL no deja cambiarlo). Ahora, con sesión, el registro lleva a Hoy.

**Cambio posterior (2026-10-22, spec R3)**: cerrar sesión borra también la marca del dispositivo; quien no verificó su WhatsApp pierde la cuenta, y la web lo avisa antes con "Verificar ahora" o "Cerrar igual".
