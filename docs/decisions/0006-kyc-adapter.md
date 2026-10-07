# 0006 — KYC como interfaz/adapter, sin vendor fijo

- **Estado**: aceptada (el adapter); **pendiente** la elección de vendor.

## Contexto

El módulo A.3 de `../ALCANCE_MVP.md` (verificación de identidad mandatoria) necesita selfie/video en vivo + detección de duplicado de hardware, antes de acceder a descubrimiento. El proveedor concreto es una decisión explícita de Pablo, todavía no tomada. Candidatos con soporte de captura por cámara web: Persona, Onfido, Veriff, Didit.

## Decisión

Scaffoldear la verificación como una interfaz/adapter abstracta en `apps/api` (puerto de dominio + implementación concreta intercambiable), sin atar código a un vendor específico hasta que Pablo elija uno.

## Consecuencias

- Permite empezar a modelar el flujo de verificación (estados: pendiente, en revisión, verificado, rechazado, duplicado detectado) sin bloquear por la elección de vendor.
- Cuando se elija vendor, el trabajo es implementar un adapter concreto, no rediseñar el flujo.
- La spec `A3` queda en `draft` hasta que este punto se resuelva.
