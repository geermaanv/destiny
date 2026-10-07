# CHANGELOG

Bitácora cronológica de qué se hizo y qué se decidió en cada sesión. Para que cualquier sesión de IA futura entienda el estado del proyecto sin releer todo el historial de git.

## 2026-10-07

- Scaffold inicial del monorepo: `apps/web` (Next.js 15 + TS + Tailwind, PWA), `apps/api` (FastAPI, endpoint `/health`), `docker-compose.yml` (Postgres local).
- Docs vivos creados: `VISION.md` (síntesis del pitch deck), `ALCANCE_MVP.md` (los 3 módulos del MVP con espacios pendientes del founder marcados).
- `CLAUDE.md` con arquitectura, cómo correr cada app, y decisiones técnicas con razonamiento.
- Estructura spec-driven adoptada: `specs/` (nada se codifica sin spec `approved`) y `decisions/` (ADRs 0001–0006, migrando las decisiones técnicas ya tomadas desde `CLAUDE.md`).
- `BACKLOG.md` creado con los puntos pendientes priorizados (P0: decisiones del founder que bloquean specs; P1–P3: specs por módulo; tareas técnicas sueltas).
- Equipo: Pablo Maiztegui (founder, dueño de las decisiones de producto), German Villamarin (soporte técnico/armado del MVP).
- Commit inicial pusheado a `main`.
- `apps/api` validado end-to-end: venv + `pip install` sin errores, `uvicorn` levanta y `/health` responde `200 {"status":"ok"}`.
- `ALCANCE_MVP.md` limpiado: se sacaron los marcadores `[ESPACIO PARA EL FOUNDER]` y la sección de pendientes — ese tracking vive únicamente en `BACKLOG.md` (P0) para que Pablo los resuelva en paralelo sin bloquear el avance sobre lo ya definido.
