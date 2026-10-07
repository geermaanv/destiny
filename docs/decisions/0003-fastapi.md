# 0003 — Backend en Python + FastAPI

- **Estado**: aceptada.

## Contexto

El backend necesita integrar cálculo astrológico (`astronomy-engine`, ver ADR 0005) y llamadas a la API de Claude (ver ADR 0004). Ambos ecosistemas son naturales en Python.

## Decisión

FastAPI como framework de API (`apps/api`).

## Consecuencias

- Tipado con Pydantic, documentación OpenAPI automática, buen fit para integrar librerías científicas/de IA en Python.
- Async nativo, útil para llamadas a APIs externas (Claude, proveedor de KYC) sin bloquear.
