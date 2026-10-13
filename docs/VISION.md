# VISION.md — Destiny

> Síntesis del pitch deck pre-seed. Fuente de verdad del producto a nivel de tesis/narrativa (Pablo Maiztegui, founder). Los cambios se documentan acá.

## Tesis

Dating es la puerta de entrada ("wedge"), no el techo del producto. Una vez validado el core loop de dating, el mismo **Identity Graph** soporta otros contextos: amistad, profesional, espiritual, actividades.

## Estrategia de lanzamiento: autoconocimiento + matchmaking (German, 2026-10-13)

Alineados 100% con el whitepaper de producto (`docs/referencias/whitepaper-producto-v1.md`): **el autoconocimiento da valor desde el primer día**, aunque todavía haya pocos usuarios. El matchmaking **sigue** siendo parte del producto, pero un match necesita masa crítica de gente cerca y compatible; hasta tener una base amplia, lo que retiene es lo que Destiny le dice a cada persona sobre sí misma (su carta, su cielo, su día, cómo le hablamos). Las dos cosas usan el mismo motor natal: cada usuario que llega por autoconocimiento suma a la base para el matchmaking.

## Gancho de comunicación (German, 2026-10-13; aprobado por Pablo)

**"¿Por qué con algunas personas fluye y con otras no?"** — arranca por el problema (no por la técnica) y une autoconocimiento y vínculos. Se acompaña de lo que no somos: "no predice el futuro ni decide por vos". Surgió del análisis de competencia (`docs/referencias/Analisis-NeoHumanCode.pdf`).

## Orden de experiencia (invertido vs. Tinder/Bumble)

```
Identidad -> Contexto -> Resonancia (explicada por IA) -> Descubrimiento (menos, mejores señales) -> Conexión
```

Principio de producto: **ralentizar la primera decisión, subir la calidad de cada interacción después.** Tinder/Bumble optimizan para volumen de swipes; Destiny optimiza para señal por interacción.

## Rol de la astrología

La astrología es la **interfaz cultural legible** para hablar de identidad, timing y compatibilidad. Es el lenguaje de la UI, no el moat.

El moat real es:
1. El **motor de IA de resonancia explicable** (nunca un score sin explicación).
2. El **grafo de compatibilidad** — comportamiento, verificación, contexto emocional, outcomes reales — que compone con el tiempo y no es replicable copiando la UI.

## Trust y verificación como producto (no compliance)

- **Verify**: selfie/video en vivo + señales de duplicado de hardware.
- **Explain**: nunca caja negra; toda compatibilidad viene con una explicación en texto.
- **Protect**: reportes, moderación, detección de bots.
- **Consent**: uso de datos claro y explícito.

Diferencial declarado vs. competencia: estos cuatro pilares son núcleo del producto desde el día 1, no una capa de compliance agregada después.

## La ronda

- **US$200k pre-seed.**
- Horizonte de 18 meses, dividido en tres fases de 6 meses:
  - **0–6: Build** — construir el MVP (ver `ALCANCE_MVP.md`).
  - **6–12: Learn** — iterar sobre retención de cohortes real.
  - **12–18: Prove** — demostrar tracción suficiente para la siguiente ronda.
- **Argentina** como mercado de lanzamiento.

## Modelo de negocio (futuro — NO aplica al MVP)

> Pospuesto a fase de tracción. El MVP v1 es 100% gratis, sin paywall. Ver `ALCANCE_MVP.md` para el razonamiento de por qué monetizar temprano ensucia los datos de retención.

- **FREE**: perfil, descubrimiento, resonancia básica, chat, local pulse, ads nativos.
- **PREMIUM US$9.99/mes**: explicaciones avanzadas, historial emocional, insights globales, recomendaciones prioritarias, sin ads.
