# A3-verificacion-identidad — Verificación de identidad mandatoria

- **Estado**: implemented
- **Módulo**: A3
- **Owner de decisión de producto**: Pablo Maiztegui (los puntos abiertos abajo siguen siendo suyos)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Bloquear el acceso a descubrimiento hasta verificar identidad (selfie/video en vivo + detección de duplicado de hardware). A diferencia de la competencia, es mandatorio y previo, no opcional y posterior.

## Puntos abiertos (no bloquean v1)

- Proveedor de KYC (Persona, Onfido, Veriff, Didit) — `BACKLOG.md` P0 / ADR `0006-kyc-adapter.md`. **No bloquea v1**: se implementa la interfaz/adapter y un adapter mock/stub para desarrollo local; el adapter real se enchufa cuando Pablo elija vendor, sin rediseñar el flujo.

## Requisitos funcionales

- Estado de verificación por perfil: `pendiente` → `en_revision` → `verificado` | `rechazado` | `duplicado_detectado`.
- Acceso a `/discover` bloqueado mientras el estado no sea `verificado`.
- Captura de selfie/video en vivo vía cámara web (todos los candidatos a vendor la soportan).
- Señal de duplicado de hardware (fingerprint de dispositivo) — el adapter mock simula esta señal para poder probar el flujo completo sin vendor real.

## Contrato de datos / API (interfaz/adapter, ADR 0006)

```python
class IdentityVerificationAdapter(Protocol):
    def start_verification(self, profile_id: str, media: bytes) -> VerificationResult: ...
    def get_status(self, verification_id: str) -> VerificationStatus: ...
```

```
POST /profiles/{id}/verification  -> inicia verificación, devuelve verification_id
GET  /profiles/{id}/verification  -> { "status": "pendiente|en_revision|verificado|rechazado|duplicado_detectado" }
```

El adapter concreto (mock en desarrollo, vendor real en producción) se inyecta por configuración — no hay lógica de negocio atada al vendor.

## UX / Flujo

1. Captura de selfie/video en vivo.
2. Pantalla de "verificación en proceso".
3. Al resolver: acceso a descubrimiento (si `verificado`) o pantalla de error/reintento (si `rechazado` o `duplicado_detectado`).

## Criterios de aceptación

- [ ] Un perfil no `verificado` no puede acceder a `/discover`.
- [ ] El adapter mock permite simular los 4 estados finales para testing.
- [ ] Cambiar de adapter mock a un vendor real no requiere cambios en las pantallas ni en el contrato de API.

## Fuera de alcance

- Integración real con un vendor de KYC (se hace cuando Pablo elija uno — ver ADR 0006).
- Políticas de reintento / apelación de rechazos (definir cuando haya vendor real).
