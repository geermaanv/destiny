# A2-ritmo-notificaciones — Selector de ritmo de notificaciones

- **Estado**: approved
- **Módulo**: A2
- **Owner de decisión de producto**: Pablo Maiztegui (los puntos abiertos abajo siguen siendo suyos)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Elección obligatoria en el onboarding entre dos ritmos de notificación, que además funciona como A/B test nativo de retención por cohorte.

## Puntos abiertos (no bloquean v1)

- Tonos/copies finales de cada notificación — `BACKLOG.md` P0. Para v1 se implementa con copy borrador (placeholder editorial), reemplazable sin tocar la lógica.
- Decisión PWA vs. mobile nativo para push en iOS (ADR `0002-nextjs-pwa.md`) — **no bloquea v1**: se implementa el selector y la lógica de envío igual; en iOS Safari la entrega de push puede ser poco confiable, documentado como limitación conocida, no como blocker de la feature.

## Requisitos funcionales

- Durante el onboarding, el usuario elige una de dos opciones, obligatorio:
  - **"Ritmo Diario"**: 1 notificación a la mañana con el pulso astrológico del día.
  - **"Pulso del Cosmos"**: notificación en tiempo real cuando hay un tránsito exacto que afecta la carta natal del usuario.
- La elección se persiste en el perfil como variable de cohorte para medir retención por grupo.
- No hay opción de "ninguna notificación" en v1 — es elección obligatoria entre las dos.

## Contrato de datos / API

```
POST /profiles/{id}/notification-preference
{ "rhythm": "ritmo_diario" | "pulso_cosmos" }
```

El valor queda disponible para analytics de cohorte (ej. `cohort = rhythm`).

## UX / Flujo

Pantalla de dos opciones con descripción corta de cada ritmo. Copy final a definir con Pablo; v1 usa copy borrador.

## Criterios de aceptación

- [ ] El onboarding no avanza sin que el usuario elija un ritmo.
- [ ] La elección queda persistida y es consultable para segmentar cohortes.
- [ ] Limitación de push en iOS Safari está documentada (no es un bug, es un trade-off conocido de la ADR 0002).

## Fuera de alcance

- Copy final de las notificaciones (iteración posterior).
- Resolver la limitación de push en iOS (evaluar mobile nativo es una decisión de negocio futura, no de esta spec).
