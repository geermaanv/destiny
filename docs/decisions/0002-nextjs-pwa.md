# 0002 — Frontend web PWA antes de nativo

- **Estado**: aceptada.

## Contexto

Hay que iterar rápido en Argentina en los primeros 6 meses (fase "Build" de la ronda, ver `../VISION.md`). Pelear con revisión de app stores desde el día 1 no ayuda a esa velocidad.

## Decisión

Next.js 15 + TypeScript + Tailwind, como PWA instalable. No hay app nativa todavía.

## Consecuencias

- Deploy instantáneo, sin revisión de store, un solo código para todos los navegadores modernos.
- **Riesgo conocido**: las push notifications son débiles/poco confiables en iOS Safari incluso como PWA instalada (soporte real recién desde iOS 16.4, comportamiento inconsistente entre versiones). Esto afecta directamente la spec `A2` (selector de ritmo de notificaciones) de `../ALCANCE_MVP.md`.
- Esta limitación puede justificar adelantar mobile nativo específicamente para notificaciones, o aceptarla y arrancar Android-first. **No decidido** — resolver antes de implementar el envío real de push (el selector de `A2` ya está implementado).
