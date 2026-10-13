# BACKLOG

Backlog priorizado de lo que sigue. Se actualiza en cada sesión — ver `CHANGELOG.md` para el historial de qué ya se hizo.

Regla del proyecto: **nada de esto se codifica sin pasar primero por una spec `approved` en `specs/`** (ver `specs/README.md`). Las 8 specs de abajo ya están `approved` (aprobadas por German Villamarin, 2026-10-07) — cada spec documenta explícitamente qué quedó fuera de alcance de v1.

## P0 — Decisiones de producto y pendientes operativos

Ya **no bloquean** la implementación (las specs correspondientes las dejaron fuera de alcance de v1 con un default o un stub). Por ahora decide German Villamarin: al resolver cada punto se actualiza la spec afectada y se ajusta la implementación si corresponde.

- [ ] UX de la pantalla de datos natales (spec `A1-datos-natales.md`).
- [x] Verificación por WhatsApp para v1, con selfie/video en vivo pospuesta a v2 — decidido (spec `A3-verificacion-identidad.md` / ADR 0008).
- [x] Número dedicado de WhatsApp para Destiny — definido por German (línea aparte; configurado solo en `apps/api/.env` local, no en el repo). Se pasa de la app WhatsApp Business a la Cloud API borrando la cuenta de la app (opción elegida: número dedicado solo a verificación, sin coexistencia).
- [ ] Cuenta comercial de Meta ("portfolio comercial"): **todavía no existe la empresa Destiny**, así que se crea a nombre de German. Sumar a Pablo como administrador desde el inicio; cuando exista la empresa, se completa ahí.
- [ ] Página web simple de Destiny (qué es + contacto + **política de privacidad**): ayuda a que Meta apruebe el nombre visible "Destiny", la pide para pasar la app a modo en vivo, y la política hace falta igual por guardar teléfonos (Ley 25.326).
- [ ] Pasar de número de prueba a la **línea real** de Destiny: borrar la cuenta de la app WhatsApp Business en esa línea, registrarla en Meta (Paso 2 → Registra tu número), esperar la aprobación del nombre visible y cambiar `WHATSAPP_BUSINESS_NUMBER` en `apps/api/.env`. Repetir la suscripción `subscribed_apps` si la cuenta de WhatsApp Business cambia (runbook en la spec A3).
- [ ] Comprar un dominio propio para Destiny (ej. `destiny.com.ar` si está libre; confirmar precio actual en NIC Argentina) y pasar el túnel de `ngrok` a **Cloudflare Tunnel** (gratis con dominio propio, URL fija y prolija tipo `app.destiny.com.ar`). Sirve también para la página con política de privacidad. Al migrar: actualizar la URL del webhook en Meta y el runbook de la ADR 0007; el código no cambia. Hasta entonces se usa el dominio fijo gratis de `ngrok` (Cloudflare sin dominio propio solo da URLs que cambian en cada reinicio).
- [ ] Verificación del negocio en Meta (CUIT/documentación) — cuando exista la empresa. No bloquea la verificación por WhatsApp: los mensajes los inicia el usuario.
- [ ] Proveedor de KYC/verificación para **v2** — Persona, Onfido, Veriff o Didit (spec `A3-verificacion-identidad.md` / ADR 0006). Ya no bloquea v1.
- [ ] Tonos/copies de notificaciones — "Ritmo Diario" vs. "Pulso del Cosmos" (spec `A2-ritmo-notificaciones.md`).
- [ ] Decisión PWA vs. nativo para push notifications en iOS (ver ADR 0002 — afecta a `A2-ritmo-notificaciones.md`).
- [x] **Motor de sinastría por ejes** (cuadro de German): implementado con tablas `v1-provisoria` en configuración (ADR 0010). Integrado a Descubrir con selector de contexto.
- [ ] **Validar las tablas de sinastría** con alguien con criterio astrológico (German, Pablo o un astrólogo): `apps/api/app/synastry/config/synastry_v1.json`.
- [x] (Hecho 2026-10-12) Pasar el rompehielos, la invitación (C8) y el calendario (B6) a la carta completa: hoy usan Sol–Sol / Luna–Sol y además toman la hora de nacimiento como si fuera UTC (`app/compatibility.py::sun_longitude`). El motor nuevo ya usa la zona horaria real.
- [x] Contexto de relación en Descubrir — **implementado** (selector Pareja / Amistad / Trabajo / Casual, cambia los pesos del motor). Antes: **decidido el enfoque**: no va en el perfil, se elige en Descubrir y la lista queda abierta (pareja, amistad, trabajo/jefe, socio…). Falta la spec del selector y de cómo cambia la explicación (`B5-pantalla-descubrir.md`).
- [ ] Integración de actividades en el calendario de memoria (spec `B6-calendario-memoria.md`, v1 no las incluye).
- [ ] Tonos/copies del chat y de los rompehielos de IA (spec `B7-chat-rompehielos.md`, v1 usa copy borrador).
- [ ] Estética y visuales del Hub en general (transversal, no bloquea ninguna spec).

## P1 — Implementar Módulo A (onboarding — gatea todo lo demás)

Specs approved, listas para codear:

- [x] `A1-datos-natales.md` — implementado (modelo `Profile`, endpoints `POST /profiles`, `POST /profiles/{id}/birth-data`, `GET /profiles/{id}`, pantalla `/onboarding/datos-natales`).
- [x] `A2-ritmo-notificaciones.md` — implementado (`notification_rhythm` en `Profile`, endpoint `POST /profiles/{id}/notification-preference`, pantalla `/onboarding/ritmo-notificaciones`).
- [x] `A3-verificacion-identidad.md` **v1 WhatsApp** — implementado en modo mock (`app/whatsapp.py`, `app/routers/whatsapp.py`): `phone_e164` + `verification_method` en `Profile`, tabla `phone_verification_codes`, `POST /profiles/{id}/verification/whatsapp`, webhook `GET`/`POST /webhooks/whatsapp` (con modo mock en desarrollo), pantalla `/onboarding/verificacion` con link `wa.me` + polling + botón "Simular envío (dev)". Para salir del mock: cuenta de Meta Business, `WHATSAPP_VERIFY_TOKEN`/`WHATSAPP_APP_SECRET` en `apps/api/.env` y registrar el webhook (`/api/webhooks/whatsapp` vía túnel, ADR 0007).
- [x] `A3-verificacion-identidad.md` (versión original, selfie/video) — implementado con mock (adapter mock de KYC en `app/adapters/kyc.py`, endpoints `POST`/`GET /profiles/{id}/verification`, pantalla `/onboarding/verificacion`). Onboarding completo A1→A2→A3 encadenado y validado end-to-end.

## P2 — Implementar Módulo B (core loop diario)

- [x] `B4-home-tu-momento.md` — implementado (`app/astro.py` con `astronomy-engine` real para fase lunar + signo, `MoodCheckin`, endpoints `/home/today`, `/home/frequency-count`, `/mood-checkins`, pantalla `/home`).
- [x] `B5-pantalla-descubrir.md` — implementado. `app/compatibility.py` (aspecto Sol-Sol real vía `astronomy-engine`, simplificación v1 — ver nota abajo), `app/explainer.py` (adapter: `ClaudeResonanceExplainer` si hay `ANTHROPIC_API_KEY`, si no `MockResonanceExplainer` con copy borrador), endpoints `GET /discover` y `GET /discover/{id}/explanation`, pantalla `/discover`. Gating por verificación ya aplicado (ver abajo).
- [x] `B6-calendario-memoria.md` — implementado. `app/aspects.py` extrae la clasificación de aspectos compartida con `B5`; `app/transits.py` calcula Luna del día vs. Sol natal del usuario (simplificación v1, mismo criterio que `B5`). Modelo `CalendarAnnotation`. Endpoints `GET /calendar/{year}/{month}`, `GET /calendar/day/{day}`, `POST /calendar/day/{day}/annotations`. Pantalla `/calendario` (grilla mensual + anotaciones).
- [x] `B7-chat-rompehielos.md` — implementado. `app/icebreaker.py`: tercer adapter con el mismo patrón que KYC/explainer (mock sin `ANTHROPIC_API_KEY`, Claude real con ella). Modelos `Match`/`ChatMessage`. Endpoints `POST /matches` (crea el match + genera e inserta el icebreaker automáticamente), `GET`/`POST /chats/{match_id}/messages`. Pantalla `/chat/[matchId]`, con botón "Match" agregado a `/discover` para completar el flujo.

## P3 — Implementar Módulo C (growth loop)

- [x] `C8-invitacion-whatsapp.md` — implementado. Modelo `Invitation`. `POST /invitations` (teaser aproximado por signo solar únicamente — `approximate_longitude_for_sign`, punto medio del signo; `locked_fields` explícitos), `GET /invitations/{ref_id}` (preload del invitado), `GET /invitations/{ref_id}/reveal` (compatibilidad real una vez que el invitado completa su carta). Pantallas `/invitar` y `/onboarding/invitacion`; `ref` se encadena por todo el onboarding (A1→A2→A3) y la revelación real se muestra al verificarse. **Con esto, los 8 módulos del MVP están implementados.**

## Refinamiento del MVP (recorrido completo, 2026-10-07)

Encontrado recorriendo la app en tamaño celular como usuario nuevo. Para decidir qué se encara primero.

**Bugs**
- [x] `/discover` da 500 si el perfil verificado no tiene datos natales (se puede llegar a la verificación entrando directo por URL). Responder un error claro y pedir completar los datos. **Hecho**: 409 + mensaje en la pantalla, y la verificación por WhatsApp no arranca sin datos natales.
- [x] Textos rotos cuando no hay aspecto mayor entre los soles: "Hay un sin aspecto mayor…" (explicación B5) y "nuestros soles están en sin aspecto mayor" (icebreaker B7).
- [x] Home dice "En tu frecuencia: N personas" pero Descubrir puede decir "Todavía no hay nadie": cuentan cosas distintas (el contador incluye perfiles sin datos natales). **Hecho**: el contador usa el mismo universo que Descubrir y no se cuenta a uno mismo.

**Gaps de producto (los más importantes)**
- [x] Los perfiles no tienen **nombre, foto, edad** (spec en borrador: `A4-perfil-liviano.md`, perfil liviano sin tipo de relación ni género): en Descubrir solo se ve "Sin aspecto mayor solar · 60%". Para una app de citas es lo primero que falta.
- [x] **Chat — decidido el enfoque híbrido** (German, 2026-10-08): el primer contacto (rompehielos y unos mensajes) va dentro de Destiny, y cuando **los dos aceptan** un botón "Pasar a WhatsApp" revela los números. Así se aprovecha WhatsApp sin exponer números antes de tiempo, y Destiny registra que conectaron y que pasaron a WhatsApp (outcome para retención). Descartados: pasar directo a WhatsApp (expone números, se pierden los datos) y usar el número de Destiny de intermediario (confuso y con costo por mensaje). **Implementado** (spec B7 v2).
- [x] **Match unilateral** (resuelto con la conexión mutua de B7 v2): tocar "Match" crea el chat al instante; la otra persona no se entera y no hay lista de chats/matches para encontrarlo.
- [x] **Sin sesión** (implementado, `A5-sesion.md`): el perfil viaja en la URL (`?profileId=`). Si se cierra el navegador se pierde el acceso. La verificación por WhatsApp + "Seguir con mi cuenta" ya sirve como login: falta guardarlo (cookie) y una entrada de "Ya tengo cuenta".

- [x] Idea de German para el perfil: **momento del día en que la persona tiene más energía** (ya está en el perfil; falta usarlo como señal de matching) (madrugador / nocturno). Mucha gente lo asocia a cuándo nació; puede ser un dato de color del perfil y una señal más para el matching. Va con el diseño del perfil básico.

- [x] El signo Géminis figuraba como "Gemini" (en inglés): corregido en la API y la web; las invitaciones viejas con "Gemini" siguen funcionando.
- [x] `GET /profiles/{id}` devolvía datos natales completos a cualquiera con el id: con la sesión (A5), un perfil verificado solo lo ve su dueño.

**Navegación / fricción**
- [x] No hay barra de navegación ni botón "atrás": Home tiene links sueltos y desde chat, calendario o invitar no se vuelve. **Hecho**: barra inferior (Inicio / Descubrir / Calendario / Invitar) en todas las pantallas post-onboarding.
- [ ] Idea de German: el onboarding como **una sola pantalla con secciones** (datos natales, ritmo, verificación) en vez de pasos separados, para poder volver y cambiar algo fácil.
- [x] Ritmo de notificaciones: no explica que es para notificaciones ni que todavía no se envían; sin indicador de paso del onboarding.

**Calendario**
- [x] Sin mes/año, sin días de la semana, no se puede cambiar de mes, no marca hoy, no explica qué son los días violetas, y la grilla no arranca en el día de la semana correcto. **Hecho** junto con la lista de próximos eventos (idea de German).

**Textos y apariencia**
- [x] Alinear la paleta de la app con el logo (azul noche `#25225b`, coral de las manos, dorado de los astros); **Hecho**: `tailwind.config.ts` redefine `slate` (azul noche), `violet` (coral) y suma `gold`.
- [x] Jerga astrológica sin traducir ("Sin aspecto mayor solar", "cuadratura"): pasar a lenguaje simple. **Hecho**: `app/aspects.py` tiene etiquetas y frases simples ("Energía parecida", "Polos opuestos", "Por descubrir"…) usadas en Descubrir, la explicación, el rompehielos y la invitación.
- [x] Invitar: "Generar reporte" no es claro y falta explicar qué recibe el amigo.

## Top 5 de mejoras (revisión de pantallas, 2026-10-08)

- [x] **Onboarding sin progreso ni "atrás"** (hecho: indicador "Paso N de 4", "Volver" que recupera lo cargado, texto de Avisos): 4 pasos (datos natales → perfil → ritmo → verificación) sin indicador de cuánto falta ni forma de volver. Ritmo no explica que es para notificaciones (y que todavía no se envían). Va de la mano con la idea de pantalla única con secciones.
- [x] **Home con poco valor diario** (hecho: tarjeta "Tu día" con el tránsito personal, spec B4 v2): "Luna menguante en Virgo" sin explicar qué significa para el usuario, y el check-in de ánimo no devuelve nada. Usar el tránsito personal del día (ya calculado para el calendario) como frase del día.
- [x] **Descubrir da casi todo igual** ("Por descubrir · 60%") porque mira solo el Sol, y no tiene selector de contexto. Se resuelve con el motor de sinastría (`B5-motor-sinastria.md`) + selector de contexto.
- [x] **Invitar es una pantalla pelada** (hecho: explicación, vista previa del mensaje, "Enviar por WhatsApp", Géminis): "Generar reporte" no se entiende, no explica qué recibe el amigo ni muestra el mensaje antes de mandarlo; el selector dice "Gemini".
- [x] **Falta feedback en las acciones** (hecho: "Guardado ✓", confirmación del check-in, hora en el chat, "Enviando solicitud…", ícono de Next oculto): "Perfil guardado" queda fuera de la vista, el check-in no confirma, el chat no muestra la hora de los mensajes, "Conectar" no muestra que está enviando. Además el ícono "N" de Next.js (solo en modo desarrollo, pero Pablo lo ve por el túnel) tapa "Inicio" en la barra.


## Roadmap de producto (Pablo, octubre 2026)

Fuente: `docs/referencias/backlog-pablo-2026-10.md` (8 líneas de Pablo + ampliación de 37 iniciativas). Clasificación (2026-10-12):

**Ya hecho (total o en parte)**
- [x] Matchmaking por afinidad en los 5 ejes (motor de sinastría, B5).
- [x] Cuestionario de compatibilidad por eje (test de Pablo, A6).
- [x] Tres sistemas numéricos separados (astrología, test, tránsitos sin porcentaje — ADR 0011).
- [x] Invitaciones virales (C8 v1 y v2).
- [ ] Calendario astrológico / Destiny Today — **en parte**: calendario + "Tu día" (Luna vs. Sol natal). Falta: tránsitos de todos los planetas y casas activadas.
- [ ] Destiny Duo — **base hecha** (conexión, chat, panel de compatibilidad). Falta: historial, fechas significativas, cuestionarios de pareja.

**Candidatos para la próxima tanda (MVP: retención y viralidad, sin cobrar)**
- [ ] AstroRadar: pronóstico personal de 7 y 30 días (extiende el calendario).
- [ ] Diario cósmico: unir check-in de ánimo y notas con el tránsito del día.
- [ ] "Mi carta" / autoconocimiento (ya anotado más abajo).
- [ ] Destiny Passport: tarjeta compartible del perfil con QR.
- [ ] Informe de vínculo descargable (PDF con ejes y sugerencias de conversación).

**Post-MVP**
- [ ] AstroChat IA (consultando el motor matemático; memoria, privacidad y costos a definir).
- [ ] Marketplace de astrólogos por zona + Destiny Studio (software para astrólogos) + AstroAcademy.
- [ ] Eventos tipo "Time left" (Cosmic Tables, speed dating, tribus, hosts).
- [ ] Destiny Pro (cofounder, mentores, networking).
- [ ] Monetización (Premium, Duo, informes, comisiones) — **después de los 6 meses gratis** (`ALCANCE_MVP.md`).

**Hiperpersonalización (idea de German y Pablo, 2026-10-13)** — aprovechar lo que Destiny sabe de cada persona para hablarle y mostrarse a su manera. Los estilos salen de **la astrología**, cada dimensión de un punto de la carta (parametrizable para que Pablo lo ajuste; la persona siempre puede cambiarlo y se le explica por qué):
- Cómo procesa la información (registro) → **Mercurio**: fuego directo, tierra práctico, aire analítico, agua intuitivo.
- Cuánta contención necesita (tono) → **Luna**.
- Qué formato le sirve → **modalidad dominante**: cardinal acciones, fija profundidad, mutable opciones.
- Estética → **Venus**; color principal del tema → **Ascendente** (o Sol sin hora exacta).
- [ ] **v1 — estilo de redacción** (spec X2). Backend hecho: estilo por carta, `GET/PUT /profiles/{id}/style`, explicaciones y 288 textos de "Tu día" por registro. Falta: tarjeta "Cómo te hablamos" en Mi perfil (esperando alinear nombres con los 4 modos del whitepaper) y que Pablo revise el mapeo y los textos.
- [ ] v2 — tema visual: paleta por Ascendente/elemento y acento por Venus, con opción manual.
- [ ] v3 — fondo con el cielo de nacimiento y tipografías.
- [ ] v4 — aprender del uso (👍/👎 en cada texto).

**Créditos en vez de Premium (idea de German y Pablo, 2026-10-13)** — una moneda propia (nombre de marca, no "tokens") para pagar por uso lo que tiene costo variable (AstroChat, informes, consultas, eventos), con el núcleo siempre gratis, créditos que se ganan con acciones (test, invitar, rachas de check-in) y paquetes para comprar (Mercado Pago, sin la comisión de las tiendas mientras sea app web). Libro de movimientos por usuario, todo parametrizable.
- [ ] Decidir con Pablo: créditos como modelo principal; nombre de la moneda; qué cuesta y qué es siempre gratis.
- [ ] Propuesta para respetar los 6 meses gratis: lanzar primero solo **ganar y gastar** créditos (sin venta) para aprender qué valora la gente.
- [ ] Revisión legal del saldo prepago (Defensa del Consumidor: vencimiento, devoluciones, información de precios).

**Decisiones pendientes para Pablo**
- [ ] Confirmar que la monetización queda para después del MVP 100 % gratis (regla de `ALCANCE_MVP.md`).
- [ ] **RRHH con la carta natal**: usar la carta para seleccionar o descartar candidatos tiene riesgo legal (discriminación, datos personales sensibles; sin evidencia de que prediga desempeño). Propuesta: Destiny Pro como networking y autoconocimiento voluntario, no selección de personal. Validar con un abogado.
- [ ] Privacidad en comparaciones con terceros (Circle, constelación de amigos): siempre con consentimiento de la otra persona.



- [x] Test de personalidad de Pablo dentro del perfil (spec A6), fiel a su código (verificado contra 18 parejas de referencia).
- [x] Pesos por tipo de relación de la sinastría alineados con los de Pablo.
- [x] Invitación a comparar el test de personalidad (C8 v2) + panel "Compatibilidad" en todos los chats (B7): astrología y personalidad por separado, con selector de vínculo.
- [ ] **"Mi carta"**: pantalla para que cada usuario vea su carta natal (rueda zodiacal con planetas, ascendente y casas, más una lista en lenguaje simple: "Sol en Tauro", "Luna en Aries", etc.) y, opcional, la descargue en PDF. Ya se calcula todo en la API (`app/synastry/chart.py`); falta exponerla y dibujarla. Requiere spec + casos de prueba antes del código.
- [ ] Pantalla de administración para editar pesos y matrices sin tocar el JSON (hoy: editar `config/*.json` + commit).
- [ ] Que Pablo revise los 72 textos de "Tu día" (`apps/api/app/content/transitos_v1.json`, hoy `revisado_por_pablo: false`).
- [ ] Que Pablo revise las tablas de sinastría (`synastry_v1.json`) con el mismo criterio que su test.

## Tests

- [x] Batería de tests automáticos de la API (`apps/api/tests/`, 77 casos, pytest, base `destiny_test`). Cubre A1, A3, A4, A5, B5 (motor y Descubrir), B6, B7 y C8.
- [ ] Tests de punta a punta en el navegador (Playwright): registro → verificación → Descubrir → conexión → chat.
- [ ] Tests de la web (componentes): hoy solo se chequean tipos con `tsc`.
- [ ] Correr los tests automáticamente en cada push (GitHub Actions con un Postgres de servicio).

## Tareas técnicas sueltas

- [ ] Confirmar si Postgres es el motor definitivo (ADR 0001) antes de producción.
- [x] Esquema de datos: `profiles` (A1-A3), `MoodCheckin`/`CalendarAnnotation` (B4/B6), `Match`/`ChatMessage` (B7). Falta modelar invitaciones (C8).
- [x] Gating real de `/discover` según `verification_status` — implementado en `B5-pantalla-descubrir.md` (`_require_verified_profile`, 403 si no verificado).
- [ ] Hoy las tablas se crean con `Base.metadata.create_all` al levantar la API (sin migraciones). Evaluar sumar Alembic antes de tocar esquema en un entorno con datos reales — no es necesario mientras solo haya datos de desarrollo.
- [x] Redacción con IA: ahora vía OpenRouter (spec X1). Key cargada por German; modelo elegido: `google/gemini-2.5-flash-lite` (el más rápido y de los más económicos, ver `docs/referencias/comparacion-modelos-ia.md`).
- [x] (Reemplazado por el motor de sinastría para Descubrir y el chat; lo que queda está en "Pasar el rompehielos, la invitación y el calendario a la carta completa".) `app/compatibility.py` calcula compatibilidad solo con el aspecto Sol-Sol (simplificación v1, documentada en el código). Una carta completa (Luna, Venus, Marte, ascendente) da una señal más rica — evaluar si vale la pena antes de sumar más signos al cálculo.
- [x] Hosting para que Pablo vea el avance — resuelto por ahora: MacBook Air de German + túnel `ngrok`, con proxy de `apps/web` a la API para que un solo túnel alcance (ver ADR `0007-hosting-local-tunel.md`, incluye el runbook). Ejecutarlo requiere una sesión de Claude Code **local** en esa Mac (esta sesión cloud no tiene acceso a esa máquina). No reemplaza una decisión de hosting real para usuarios fuera del equipo.
- [ ] Las dependencias de `apps/api/requirements.txt` están fijadas a versiones que no soportan Python 3.14 (hoy se usa 3.12). Evaluar actualizarlas o fijar la versión de Python en el repo (`.python-version`).
- [ ] Las tablas se crean con `create_all`, que **no agrega columnas nuevas** a tablas existentes: una base local anterior a la verificación por WhatsApp necesita recrearse (o `ALTER TABLE profiles ADD COLUMN verification_method varchar, ADD COLUMN phone_e164 varchar UNIQUE, ADD COLUMN duplicate_of_id uuid` las de C8 v2 (`invitations`: `friend_sun_sign` nullable, `kind`, `relationship`, `invitee_profile_id`, `accepted_at`; `matches`: `relationship`, `source`), las de sesión en `phone_verification_codes` (`profile_id` nullable, `purpose`, `claim_token_hash`, `claimed_at`, `result_profile_id`, `outcome`) las de conexión en `matches` (`status` default `aceptada` para filas viejas, `accepted_at`, `whatsapp_a_ok`, `whatsapp_b_ok`, `whatsapp_shared_at`, `blocked_by`) y las columnas del perfil liviano: `display_name`, `bio`, `neighborhood`, `energy_period`, `avatar`, `photo_path` varchar e `interests varchar[] NOT NULL DEFAULT '{}'`); X2: `style_registro varchar`. Otro argumento para sumar Alembic.
- [ ] Rate limiting de `POST /profiles/{id}/verification/whatsapp` antes de abrir a usuarios fuera del equipo (fuera de alcance de A3 v1).
- [x] Cuando se corra el runbook de la ADR 0007, setear `WEB_BASE_URL` en `apps/api/.env` a la URL de `ngrok` del momento, para que el link de invitación de `C8-invitacion-whatsapp.md` sea válido desde afuera (si no, sigue apuntando a `localhost:3000`).
