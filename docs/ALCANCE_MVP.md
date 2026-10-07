# ALCANCE_MVP.md — Destiny

> Alcance funcional del MVP v1. Basado en el borrador técnico definitivo de Pablo Maiztegui. Tratarlo como fuente de verdad del producto — no reinventar las decisiones que ya están tomadas acá.
>
> Los puntos que todavía dependen de una decisión del founder (UX, copies, proveedor de KYC, etc.) no están acá — se trackean en `BACKLOG.md` (sección P0) y se van resolviendo en paralelo.

## Regla no negociable del MVP v1

**El MVP sale 100% gratis, sin ningún paywall.** El modelo Premium (ver `VISION.md`) se pospone a la fase de tracción.

Razón: la única métrica que importa en los primeros 6 meses es **retención de cohortes**. Cualquier fricción de pago contamina esos datos de comportamiento — no se puede distinguir "no retiene" de "no quiso pagar".

---

## Módulo A — Onboarding / Anclaje de identidad

1. **Carga de datos natales** (fecha, lugar, hora).
   - Botón de escape: **"No sé mi hora exacta"** → asigna 12:00 PM internamente y marca el perfil con flag `hora_estimada: true`.
   - Esto mantiene ~95% de precisión en planetas mayores (la hora exacta afecta sobre todo Ascendente y casas, no las posiciones planetarias en sí).

2. **Selector de ritmo de notificaciones** — elección obligatoria en el onboarding:
   - **"Ritmo Diario"**: 1 mensaje a la mañana con el pulso astrológico del día.
   - **"Pulso del Cosmos"**: alertas en tiempo real por tránsitos exactos que afecten la carta natal del usuario.
   - Funciona como **A/B test nativo**: la elección del usuario es la cohorte, y se mide cuál retiene más.
   - ⚠️ **Flag técnico**: ver nota de PWA/push en `CLAUDE.md` — soporte de push en iOS Safari es débil incluso como PWA instalada. Puede justificar mobile nativo adelantado para esta función específica, o aceptar la limitación siendo Android-first al inicio.

3. **Verificación de identidad MANDATORIA** antes de acceder a descubrimiento.
   - Selfie/video en vivo + detección de duplicado de hardware.
   - A diferencia de la competencia (que lo deja opcional y posterior), en Destiny es bloqueante.
   - Proveedor de KYC sin elegir todavía (ver ADR `0006-kyc-adapter.md`) — se scaffoldea como interfaz/adapter, sin atar código a un vendor.
   - **Actualización 2026-10-07**: para v1 la verificación es **por WhatsApp** (sin costo); la selfie/video en vivo pasa a próximas versiones. Pendiente de confirmación de Pablo. Ver spec `A3-verificacion-identidad.md` y ADR `0008-verificacion-whatsapp.md`.

---

## Módulo B — Experiencia diaria / Core loop

4. **Home "Tu Momento"**:
   - Clima astrológico del día en texto claro (ej. "Luna llena en Libra").
   - Mood check-in de un toque.
   - Contador de **"N en tu frecuencia"**: personas con tránsitos afines, agrupadas geográficamente.

5. **Pantalla "Descubrir"**:
   - Lista curada y chica de perfiles (menos opciones, mejor señal) con % de compatibilidad destacado.
   - Al abrir un perfil, la IA explica en texto: *"¿Por qué esta persona? ¿Por qué ahora? ¿Qué parte de nosotros resuena?"* — nunca un score sin explicación.
   - Implementación: se envían datos astrológicos + intención de ambos perfiles en JSON a un LLM (Claude API), bajo lineamientos editoriales de Destiny.

6. **Calendario de memoria**:
   - Vista mensual limpia, días con tránsitos clave marcados.
   - Al tocar un día: línea de tiempo de eventos astrológicos cruzada con anotaciones de vida real (propias o sugeridas por la app).

7. **Chat con rompehielos de IA**:
   - Al generarse resonancia mutua, la IA inyecta automáticamente y gratis un disparador de conversación personalizado, basado en los aspectos más fuertes de ambas cartas natales.
   - Objetivo explícito: eliminar el "hola, ¿cómo estás?".

---

## Módulo C — Growth loop viral

8. **Invitación por "resonancia parcial"** (WhatsApp Link Generator):
   - El usuario tipea nombre + signo solar de un amigo (sin hora/lugar — fricción mínima).
   - La IA genera un reporte parcial con los datos más jugosos bloqueados/borrosos.
   - Un botón abre WhatsApp con un mensaje pre-escrito personalizado + link con `ref_id`.
   - El link precarga el onboarding del invitado directo al paso de revelación de compatibilidad mutua.
   - **Canal principal de adquisición orgánica a costo cero** (CAC disciplinado — es la apuesta de growth del MVP).
