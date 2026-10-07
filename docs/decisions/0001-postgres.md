# 0001 — Postgres como base de datos

- **Estado**: aceptada, no definitiva — confirmar con Pablo si prefiere otro motor antes de comprometerse en producción.

## Contexto

El MVP necesita un motor relacional para perfiles, cartas natales, resonancias y chat. No hubo una elección deliberada del founder todavía; es una sugerencia técnica de partida.

## Decisión

Usar Postgres (vía `docker-compose.yml` en local, SQLAlchemy + `psycopg` en `apps/api`).

## Consecuencias

- Relacional, maduro, buen soporte de JSON (`jsonb`) para datos semi-estructurados como el JSON de carta natal que se manda al LLM.
- Reversible con bajo costo mientras no haya datos de producción reales.
