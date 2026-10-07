# Decisiones técnicas (ADRs)

Architecture Decision Records. Cada decisión técnica con peso (elegir una librería core, un motor de datos, un proveedor) se registra acá: contexto, decisión, consecuencias. `CLAUDE.md` tiene el resumen operativo; esta carpeta tiene el detalle y el porqué, para que no se pierda con el tiempo.

## Índice

| ADR | Título | Estado |
|---|---|---|
| [0001](./0001-postgres.md) | Postgres como base de datos | aceptada (no definitiva — confirmar con founder) |
| [0002](./0002-nextjs-pwa.md) | Frontend web PWA antes de nativo | aceptada |
| [0003](./0003-fastapi.md) | Backend en Python + FastAPI | aceptada |
| [0004](./0004-claude-api-resonancia.md) | Claude API para explicaciones de resonancia | aceptada |
| [0005](./0005-astronomy-engine.md) | `astronomy-engine` en vez de Swiss Ephemeris | aceptada |
| [0006](./0006-kyc-adapter.md) | KYC como interfaz/adapter, sin vendor fijo | aceptada (pospuesta a v2, ver 0008) |
| [0007](./0007-hosting-local-tunel.md) | Hosting: máquina local del equipo + túnel | aceptada |
| [0008](./0008-verificacion-whatsapp.md) | Verificación v1 por WhatsApp; selfie/video en vivo pasa a v2 | aceptada |
