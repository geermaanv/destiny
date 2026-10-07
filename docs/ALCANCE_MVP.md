# ALCANCE_MVP.md — Destiny

> Alcance funcional del MVP v1. Basado en el borrador técnico definitivo de Pablo Maiztegui. Tratarlo como fuente de verdad del producto — no reinventar las decisiones que ya están tomadas acá.

## Regla no negociable del MVP v1

**El MVP sale 100% gratis, sin ningún paywall.** El modelo Premium (ver `VISION.md`) se pospone a la fase de tracción.

Razón: la única métrica que importa en los primeros 6 meses es **retención de cohortes**. Cualquier fricción de pago contamina esos datos de comportamiento — no se puede distinguir "no retiene" de "no quiso pagar".

---

## Módulo A — Onboarding / Anclaje de identidad

1. **Carga de datos natales** (fecha, lugar, hora).
   - Botón de escape: **"No sé mi hora exacta"** → asigna 12:00 PM internamente y marca el perfil con flag `hora_estimada: true`.
   - Esto mantiene ~95% de precisión en planetas mayores (la hora exacta afecta sobre todo Ascendente y casas, no las posiciones planetarias en sí).
   - `[ESPACIO PARA EL FOUNDER]` — UX de la pantalla de datos natales (flujo, copys, diseño).

2. **Selector de ritmo de notificaciones** — elección obligatoria en el onboarding:
   - **"Ritmo Diario"**: 1 mensaje a la mañana con el pulso astrológico del día.
   - **"Pulso del Cosmos"**: alertas en tiempo real por tránsitos exactos que afecten la carta natal del usuario.
   - Funciona como **A/B test nativo**: la elección del usuario es la cohorte, y se mide cuál retiene más.
   - `[ESPACIO PARA EL FOUNDER]` — tonos/copies de las notificaciones de cada ritmo.
   - ⚠️ **Flag técnico**: ver nota de PWA/push en `CLAUDE.md` — soporte de push en iOS Safari es débil incluso como PWA instalada. Puede justificar mobile nativo adelantado para esta función específica, o aceptar la limitación siendo Android-first al inicio.

3. **Verificación de identidad MANDATORIA** antes de acceder a descubrimiento.
   - Selfie/video en vivo + detección de duplicado de hardware.
   - A diferencia de la competencia (que lo deja opcional y posterior), en Destiny es bloqueante.
   - `[ESPACIO PARA EL FOUNDER]` — proveedor de KYC/verificación (candidatos: Persona, Onfido, Veriff, Didit). Ver `CLAUDE.md` — se scaffoldea como interfaz/adapter, sin atar código a un vendor todavía.

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
   - `[ESPACIO PARA EL FOUNDER]` — qué tipos de relación filtrar (pareja / amistad / etc.) en esta primera versión.

6. **Calendario de memoria**:
   - Vista mensual limpia, días con tránsitos clave marcados.
   - Al tocar un día: línea de tiempo de eventos astrológicos cruzada con anotaciones de vida real (propias o sugeridas por la app).
   - `[ESPACIO PARA EL FOUNDER]` — integración de actividades en el calendario.

7. **Chat con rompehielos de IA**:
   - Al generarse resonancia mutua, la IA inyecta automáticamente y gratis un disparador de conversación personalizado, basado en los aspectos más fuertes de ambas cartas natales.
   - Objetivo explícito: eliminar el "hola, ¿cómo estás?".
   - `[ESPACIO PARA EL FOUNDER]` — tonos/copies del chat y de los rompehielos generados.

---

## Módulo C — Growth loop viral

8. **Invitación por "resonancia parcial"** (WhatsApp Link Generator):
   - El usuario tipea nombre + signo solar de un amigo (sin hora/lugar — fricción mínima).
   - La IA genera un reporte parcial con los datos más jugosos bloqueados/borrosos.
   - Un botón abre WhatsApp con un mensaje pre-escrito personalizado + link con `ref_id`.
   - El link precarga el onboarding del invitado directo al paso de revelación de compatibilidad mutua.
   - **Canal principal de adquisición orgánica a costo cero** (CAC disciplinado — es la apuesta de growth del MVP).

---

## Espacios pendientes de decisión del founder

Estos puntos están explícitamente abiertos. Preguntarle a Pablo antes de asumir un default:

- [ ] UX de la pantalla de datos natales (Módulo A.1).
- [ ] Tonos/copies de notificaciones (Módulo A.2).
- [ ] Proveedor de KYC/verificación (Módulo A.3).
- [ ] Qué tipos de relación filtrar — pareja/amistad/etc. (Módulo B.5).
- [ ] Integración de actividades en el calendario (Módulo B.6).
- [ ] Tonos/copies del chat y rompehielos de IA (Módulo B.7).
- [ ] Estética y visuales del Hub en general.
