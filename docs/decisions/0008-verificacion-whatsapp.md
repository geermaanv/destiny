# 0008 — Verificación de identidad v1 por WhatsApp; selfie/video en vivo pasa a v2

- **Estado**: aceptada (German Villamarin, 2026-10-07).

## Contexto

`ALCANCE_MVP.md` (A.3) pide verificación de identidad mandatoria con selfie/video en vivo vía un vendor de KYC (ADR 0006). Todos los vendors candidatos cobran por verificación, y el MVP es 100% gratis: cada verificación la pagaría Destiny. No se quiere gastar en verificaciones en esta etapa.

Alternativas evaluadas:

- **Email**: descartado. Crear cuentas de email es trivial; no frena cuentas falsas ni duplicadas.
- **OTP saliente por SMS/WhatsApp** (Destiny manda el código): funciona, pero cada mensaje tiene costo.
- **WhatsApp "al revés"** (el usuario le manda el código a Destiny vía link `wa.me`): elegida.

## Decisión

Para el MVP v1, la verificación es por WhatsApp "al revés", usando la WhatsApp Cloud API de Meta: el usuario envía un código prellenado al número de Destiny y un webhook de la API lo valida y toma el número del remitente como teléfono verificado. Regla: una cuenta por número.

La selfie/video en vivo **no se descarta**: queda para próximas versiones (v2), sumada encima de WhatsApp. El adapter de KYC (ADR 0006) se conserva en el código.

Detalle funcional y contrato de API en `../specs/A3-verificacion-identidad.md`.

## Consecuencias

- Costo $0 por verificación (los mensajes iniciados por el usuario no se cobran en el esquema actual de Meta — reconfirmar antes de producción).
- Garantiza una persona con un número real y una cuenta por número; **no** garantiza que la cara de las fotos sea la del usuario (eso llega con v2).
- Encaja con Argentina (WhatsApp universal) y con el growth loop por WhatsApp de `C8`.
- Requiere cuenta de Meta Business, un número dedicado (no usado en la app común de WhatsApp) y una URL pública estable para el webhook (hoy, el túnel de ADR 0007).
- Se guarda el número de teléfono de cada usuario: dato personal, nunca expuesto a otros usuarios.
