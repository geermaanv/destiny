# Decisiones técnicas (ADRs)

Architecture Decision Records. Cada decisión técnica con peso (elegir una librería core, un motor de datos, un proveedor) se registra acá: contexto, decisión, consecuencias. `CLAUDE.md` tiene el resumen operativo; esta carpeta tiene el detalle y el porqué, para que no se pierda con el tiempo.

## Índice

| ADR | Título | Estado |
|---|---|---|
| [0001](./0001-postgres.md) | Postgres como base de datos | aceptada (no definitiva) |
| [0002](./0002-nextjs-pwa.md) | Frontend web PWA antes de nativo | aceptada |
| [0003](./0003-fastapi.md) | Backend en Python + FastAPI | aceptada |
| [0004](./0004-claude-api-resonancia.md) | Claude API para explicaciones de resonancia | reemplazada por spec X1 (OpenRouter) |
| [0005](./0005-astronomy-engine.md) | `astronomy-engine` en vez de Swiss Ephemeris | aceptada |
| [0006](./0006-kyc-adapter.md) | KYC como interfaz/adapter, sin vendor fijo | aceptada (pospuesta a v2, ver 0008) |
| [0007](./0007-hosting-local-tunel.md) | Hosting: máquina local del equipo + túnel | aceptada |
| [0008](./0008-verificacion-whatsapp.md) | Verificación v1 por WhatsApp; selfie/video en vivo pasa a v2 | aceptada |
| [0009](./0009-geocoding-open-meteo.md) | Geocodificación del lugar de nacimiento con Open-Meteo | aceptada |
| [0010](./0010-motor-sinastria-config.md) | Motor de sinastría: tablas en configuración, casas iguales y calibración | reemplazada por 0012 |
| [0011](./0011-modelo-matematico-pablo.md) | Compatibilidad con modelo matemático; Pablo es la última palabra del modelo | aceptada |
| [0012](./0012-motor-oficial-destiny-1-0.md) | Motor oficial Destiny 1.0 (calculadoras de Pablo), tablas generadas desde los Excel | aceptada |
| [0013](./0013-chequeo-fotos-con-ia.md) | Chequeo de fotos con IA (excepción acotada a "la IA no recibe datos personales") | aceptada |
| [0014](./0014-numero-global-provisorio.md) | Número global de compatibilidad provisorio: promedio simple de los sistemas | aceptada (Pablo dio el ok, 2026-10-23) |
