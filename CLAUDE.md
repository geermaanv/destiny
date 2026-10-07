# CLAUDE.md — Destiny

Instrucciones de proyecto para Claude Code. Leer también, en este orden, antes de trabajar en producto:

1. `docs/VISION.md` — tesis, pitch deck.
2. `docs/ALCANCE_MVP.md` — los 3 módulos del MVP y espacios pendientes del founder.
3. `docs/BACKLOG.md` — qué sigue, priorizado.
4. `docs/specs/` — specs por feature (ver regla dura abajo).
5. `docs/decisions/` — ADRs, el detalle y el porqué de cada decisión técnica.
6. `docs/CHANGELOG.md` — bitácora cronológica de qué se hizo y decidió en cada sesión.

## Regla dura: spec-driven

**Ninguna feature se codifica sin una spec en estado `approved` en `docs/specs/`.** Ver `docs/specs/README.md` para el workflow y `docs/specs/TEMPLATE.md` para la plantilla. Si una spec tiene puntos abiertos marcados `[ESPACIO PARA EL FOUNDER]` o similar, no puede pasar de `draft` a `approved`.

Al terminar cualquier sesión de trabajo con cambios relevantes, actualizar `docs/CHANGELOG.md` y `docs/BACKLOG.md`.

## Idioma

Comunicación con el equipo en **español**. El founder (Pablo Maiztegui) y German Villamarin (soporte técnico/MVP) manejan el proyecto en español — mantener ese idioma en docs, commits y conversación, salvo que se pida lo contrario.

## Personas

- **Pablo Maiztegui** — founder. Dueño de las decisiones de producto marcadas `[ESPACIO PARA EL FOUNDER]` en `docs/ALCANCE_MVP.md`. No asumir defaults ahí sin confirmar con él.
- **German Villamarin** — soporte técnico, ayuda a armar el MVP.

## Arquitectura

Monorepo:

```
/apps/web   — Next.js 15 + TypeScript + Tailwind, PWA (no app nativa todavía)
/apps/api   — FastAPI (Python)
/docs       — documentación viva del producto (VISION.md, ALCANCE_MVP.md)
docker-compose.yml — Postgres local
```

## Cómo correr cada app localmente

### Postgres

```bash
docker compose up -d
```

### API (`apps/api`)

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Health check: `GET http://localhost:8000/health`

### Web (`apps/web`)

```bash
cd apps/web
npm install
cp .env.example .env.local
npm run dev
```

Corre en `http://localhost:3000`.

## Decisiones técnicas y razonamiento

> Resumen operativo. El detalle y el porqué completo de cada una está en `docs/decisions/` (ADRs 0001–0006) — actualizar ahí primero si una decisión cambia, y reflejar el resumen acá.

### Frontend: PWA primero, no nativo

Next.js + TypeScript + Tailwind, pensado para iterar rápido en Argentina sin pelear con app stores desde el día 1.

**⚠️ Pendiente de validar con Pablo antes de construir el Módulo A.2 (selector de ritmo de notificaciones, ver `docs/ALCANCE_MVP.md`):** las push notifications son débiles/poco confiables en iOS Safari incluso como PWA instalada (soporte real recién desde iOS 16.4, comportamiento inconsistente entre versiones). Esto puede justificar:
- adelantar mobile nativo específicamente para esa función, o
- aceptar la limitación y arrancar Android-first.

Esta decisión no está tomada — flaguearla a Pablo antes de implementar notificaciones push.

### Backend: Python + FastAPI

Elegido por velocidad de desarrollo y porque el ecosistema Python es natural para integrar cálculo astrológico (`astronomy-engine`) y llamadas a la API de Claude.

### Base de datos: Postgres

Sugerencia técnica, **no es definitiva** — confirmar con Pablo si prefiere otro motor antes de comprometerse en producción.

### IA para explicaciones de resonancia: Claude API (Anthropic)

Encaja con el principio de producto "nunca caja negra" (ver `docs/VISION.md`, pilar Explain). Claude es fuerte en texto explicativo con tono editorial controlado — necesario para el Módulo B.5 (pantalla "Descubrir").

### Motor astrológico: `astronomy-engine` (no Swiss Ephemeris)

`astronomy-engine` es MIT, cálculo directo de posiciones planetarias vía VSOP87/ELP2000.

Swiss Ephemeris exige licencia GPL o pago comercial a Astrodienst para uso cerrado/comercial. Para compatibilidad de consumo (signos, aspectos, tránsitos) no hace falta la precisión de sistemas de casas de nivel profesional que da Swiss Ephemeris.

Si más adelante se necesita esa precisión (ej. casas astrológicas exactas), evaluar licenciar Swiss Ephemeris aparte — es una **decisión de negocio**, no un default técnico.

### KYC / verificación biométrica: sin proveedor elegido

Candidatos con soporte de captura por cámara web: **Persona, Onfido, Veriff, Didit**. Es una decisión explícita de Pablo (Módulo A.3 en `docs/ALCANCE_MVP.md`).

Scaffoldear como **interfaz/adapter abstracto** — no atar código a un vendor específico hasta que se elija.

## Reglas del MVP

- **100% gratis, sin paywall.** Ver `docs/ALCANCE_MVP.md` — cualquier fricción de pago contamina los datos de retención de cohortes, la única métrica que importa en los primeros 6 meses.
- No implementar lógica de producto real (matching, IA, KYC) sin confirmar el diseño con Pablo primero, en particular los puntos marcados `[ESPACIO PARA EL FOUNDER]`.
- Confirmar con Pablo antes de instalar dependencias o elegir librerías adicionales no mencionadas en este documento.
