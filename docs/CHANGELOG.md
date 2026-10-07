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
- Las 8 specs del MVP (`A1`-`A3`, `B4`-`B7`, `C8`) escritas y marcadas `approved`, aprobadas para implementación por German Villamarin (no por Pablo). Cada punto de `BACKLOG.md` P0 todavía abierto queda explícitamente fuera de alcance de v1 en la spec que afecta (con un default razonable o un adapter/stub), para no bloquear código mientras Pablo decide en paralelo.
- `BACKLOG.md` reorganizado: P0 son decisiones de producto pendientes que ya no bloquean (quedaron fuera de alcance en las specs); P1-P3 pasan de "specs a escribir" a "implementar" (specs ya aprobadas).
