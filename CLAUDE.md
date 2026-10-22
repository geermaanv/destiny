# CLAUDE.md — Destiny

Instrucciones de proyecto para Claude Code. Leer también, en este orden, antes de trabajar en producto:

1. `docs/VISION.md` — tesis, pitch deck.
2. `docs/ALCANCE_MVP.md` — los 3 módulos del MVP, lo que ya está definido.
3. `docs/BACKLOG.md` — qué sigue, priorizado.
4. `docs/specs/` — specs por feature (ver regla dura abajo).
5. `docs/decisions/` — ADRs, el detalle y el porqué de cada decisión técnica.
6. `docs/CHANGELOG.md` — bitácora cronológica de qué se hizo y decidió en cada sesión.

## Regla dura: spec → casos de prueba → código

**Orden obligatorio para todo cambio de comportamiento** (decisión de German, 2026-10-09):

1. **Spec** en estado `approved` en `docs/specs/` (ver `docs/specs/README.md` y `docs/specs/TEMPLATE.md`). Por ahora las aprueba German Villamarin; los puntos abiertos que no bloquean se dejan fuera de alcance con un default.
2. **Casos de prueba** escritos **antes** del código: la sección "Casos de prueba" de la spec los lista en lenguaje simple, y se implementan como tests automáticos en `apps/api/tests/` (un archivo por spec, ej. `test_a3_verificacion_whatsapp.py`). Primero se ven fallar.
3. **Recién ahí el código**, hasta que los tests pasen. Un cambio no se commitea con tests en rojo.

Correr los tests (usa la base `destiny_test`, no toca los datos de desarrollo):

```bash
cd apps/api && .venv/bin/pytest
```

## Regla dura: cada commit actualiza la documentación

**Todo commit debe incluir, en el mismo commit, la actualización de la documentación afectada.** Como mínimo:

- `docs/CHANGELOG.md` — entrada con qué se hizo y por qué.
- `docs/BACKLOG.md` — marcar lo completado / agregar lo nuevo que surja.
- La spec en `docs/specs/` si el cambio toca una feature, el ADR en `docs/decisions/` si cambia una decisión técnica, y este `CLAUDE.md` si cambia cómo se corre o se trabaja en el proyecto.

No se hacen commits "de código" y después otro "de docs": van juntos.

## Idioma

Comunicación con el equipo en **español**. El founder (Pablo Maiztegui) y German Villamarin (soporte técnico/MVP) manejan el proyecto en español — mantener ese idioma en docs, commits y conversación, salvo que se pida lo contrario.

## Personas

- **Pablo Maiztegui** — founder.
- **German Villamarin** — soporte técnico, arma el MVP. **Por ahora toma las decisiones de producto y técnicas** (aprueba specs y ADRs); no hay que frenar el avance esperando confirmación de nadie más.

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

Alternativa sin Docker (recomendada en Macs con poca RAM — Docker en Mac corre una VM): Postgres nativo con Homebrew, con el mismo usuario/base que espera `.env.example`:

```bash
brew install postgresql@16 && brew services start postgresql@16
psql -d postgres -c "CREATE ROLE destiny LOGIN PASSWORD 'destiny';" -c "CREATE DATABASE destiny OWNER destiny;"
```

### API (`apps/api`)

Requiere **Python 3.12**: las versiones fijadas en `requirements.txt` (ej. `psycopg-binary==3.2.3`, `pydantic==2.9.2`) no instalan en Python 3.14. En Mac: `brew install python@3.12`.

```bash
cd apps/api
python3.12 -m venv .venv && source .venv/bin/activate
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

Para probar desde el celular (túnel), la web corre en **modo producción**, que abre cada pantalla en milisegundos: `npm run build && npm run start`. Después de cada cambio en `apps/web` hay que recompilar y reiniciar. `next dev` compila cada pantalla al abrirla (2 a 20 s) y en una Mac de 8 GB se reinicia por memoria: usarlo solo mientras se programa.

## Decisiones técnicas y razonamiento

> Resumen operativo. El detalle y el porqué completo de cada una está en `docs/decisions/` (ADRs 0001–0013) — actualizar ahí primero si una decisión cambia, y reflejar el resumen acá.

### Frontend: PWA primero, no nativo

Next.js + TypeScript + Tailwind, pensado para iterar rápido en Argentina sin pelear con app stores desde el día 1.

**⚠️ Decisión abierta para cuando se implementen push reales (el selector de ritmo `A2` ya está hecho):** las push notifications son débiles/poco confiables en iOS Safari incluso como PWA instalada (soporte real recién desde iOS 16.4, comportamiento inconsistente entre versiones). Esto puede justificar:
- adelantar mobile nativo específicamente para esa función, o
- aceptar la limitación y arrancar Android-first.

Esta decisión no está tomada — resolverla antes de implementar el envío real de notificaciones push.

### Backend: Python + FastAPI

Elegido por velocidad de desarrollo y porque el ecosistema Python es natural para integrar cálculo astrológico (`astronomy-engine`) y llamadas a la API de Claude.

### Base de datos: Postgres

Sugerencia técnica, **no es definitiva** — revisar antes de comprometerse en producción.

### IA para redactar explicaciones y rompehielos: OpenRouter (spec X1)

La IA **solo redacta** a partir del resultado ya calculado (ADR 0011): el modelo matemático decide qué los une y qué tienen que trabajar. También redacta Mi carta, Tu día completo y conversa en el **Astrochat** (spec X3), siempre con los datos ya calculados por el motor y sin datos personales (`app/llm.py`: `complete` para un texto, `converse` para el chat). Va por **OpenRouter** (`OPENROUTER_API_KEY` y `OPENROUTER_MODEL` en `apps/api/.env`; el modelo se cambia sin tocar código). Sin key o si falla, textos de plantilla. Nunca se mandan datos personales, con una excepción acotada: el chequeo de fotos (spec A11, ADR 0013) manda solo la imagen, sin ningún otro dato y pidiendo que el proveedor no la guarde. Comparación de modelos: `docs/referencias/comparacion-modelos-ia.md` (`apps/api/scripts/compare_llm_models.py`).

### Motor astrológico: `astronomy-engine` (no Swiss Ephemeris)

`astronomy-engine` es MIT, cálculo directo de posiciones planetarias vía VSOP87/ELP2000.

Swiss Ephemeris exige licencia GPL o pago comercial a Astrodienst para uso cerrado/comercial. Para compatibilidad de consumo (signos, aspectos, tránsitos) no hace falta la precisión de sistemas de casas de nivel profesional que da Swiss Ephemeris.

Si más adelante se necesita esa precisión (ej. casas astrológicas exactas), evaluar licenciar Swiss Ephemeris aparte — es una **decisión de negocio**, no un default técnico.

### Compatibilidad: modelo matemático, Pablo es la última palabra (ADR 0011)

- **Sinastría**: motor oficial Destiny 1.0 de Pablo (`app/synastry/`, spec A7, ADR 0012). Tablas en `config/synastry_v2.json`, generadas con `scripts/build_synastry_v2.py` desde los Excel de Pablo, que **no van al repo** (`~/proyectos/destiny-fuentes/`). Los tests comparan contra las auditorías de Pablo (`tests/fixtures/motor_oficial_casos.json`, generado con `scripts/build_motor_fixtures.py`).
- **Test de personalidad de Pablo** (`app/personality/`, `config/test_v4.json`, spec A6). Sinastría y test se calculan con fórmulas y tablas, no con IA, y se muestran **separados**.
- Todo es parametrizable en esos JSON. El test se importa del HTML de Pablo (`docs/referencias/pablo_test_express_v4.html`) con `node apps/api/scripts/import_pablo_test.mjs`; si Pablo lo cambia, se reimporta y se regeneran las referencias con `node apps/api/scripts/pablo_golden.mjs`.
- La IA solo redacta explicaciones y rompehielos a partir del resultado ya calculado.

### Geocodificación: Open-Meteo

Autocomplete de ciudad de nacimiento → lat/lon + timezone, detrás de un adapter (`app/geocoding.py`). Gratis para uso no comercial: revisar términos antes de abrir a usuarios reales (ADR 0009).

### Verificación de identidad: WhatsApp en v1, KYC (selfie/video) en v2

MVP v1: verificación por WhatsApp "al revés" — el usuario envía un código al número de Destiny, sin costo (ADR 0008, spec `A3`). **Desde 2026-10-14 es opcional** (spec `A10`, `VERIFICACION_OBLIGATORIA=false`): el registro termina sin WhatsApp, la sesión se inicia en el dispositivo y la verificación se ofrece desde Perfil (marca de verificado, entrar desde otro celular, pasar a WhatsApp). La selfie/video en vivo vía vendor de KYC se mantiene como plan para próximas versiones.

KYC (v2) — candidatos con soporte de captura por cámara web: **Persona, Onfido, Veriff, Didit**. Vendor a elegir cuando se encare v2 (Módulo A.3 en `docs/ALCANCE_MVP.md`).

Scaffoldear como **interfaz/adapter abstracto** — no atar código a un vendor específico hasta que se elija.

## Agente breaker

`.claude/agents/breaker.md`: agente que intenta romper la app (permisos, privacidad, validaciones, flujos) y devuelve un informe priorizado, sin arreglar nada. Trabaja **solo** contra una API propia en el puerto 8001 con la base `destiny_breaker` (nunca la base `destiny`, que tiene usuarios reales). Los hallazgos se triagean con German antes de arreglarlos (spec → tests → código).

## Reglas del MVP

- **100% gratis, sin paywall.** Ver `docs/ALCANCE_MVP.md` — cualquier fricción de pago contamina los datos de retención de cohortes, la única métrica que importa en los primeros 6 meses.
- Cada decisión de producto o técnica nueva (incluidas dependencias, librerías o servicios externos) se documenta en su spec o en un ADR, en el mismo commit.
