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
- [x] ~~Validar las tablas de sinastría provisorias~~ → reemplazadas por el **motor oficial Destiny 1.0 de Pablo** (spec A7, ADR 0012, 2026-10-13): coincide con su motor de referencia en 457 casos de sus auditorías y sus 3 demos.
- [x] **Decisiones sobre el motor 1.0** — decidido por German (2026-10-13): **se toma lo de Pablo como bueno**, tal como está en su motor: E3 con casas desde el grado del ASC, Juno sin informar, orbes sin tolerancia extra ni doble aspecto, y el modo reducido (redistribución de pesos y E4 neutralizado hacia 50). La sinastría usa los pesos del motor (ocasional 70/10/15/5) y el test de personalidad los suyos (60/10/25/5): son dos modelos de Pablo y se muestran separados.
- [ ] Si Pablo cambia una planilla: copiar el ZIP nuevo a `~/proyectos/destiny-fuentes/`, correr `apps/api/scripts/build_synastry_v2.py` (y `build_motor_fixtures.py` si trae auditorías nuevas) y correr los tests.
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


## Autoconocimiento primero, matchmaking después (decisión de German, 2026-10-13)

Estrategia en `VISION.md`: el autoconocimiento da valor mientras la base de usuarios crece; el matchmaking sigue. Prioridad tomada del MVP 1 del whitepaper (`docs/referencias/whitepaper-producto-v1.md`), sobre lo que ya existe:
- [x] **Mi carta por dimensiones** (spec A8): identidad, amor, vocación y emociones, con síntesis en el estilo de la persona, fundamentos trazables y preguntas para pensar. Pantalla `/perfil/carta`, acceso desde Mi perfil.
- [ ] Que Pablo revise la matriz de indicadores de Mi carta (`apps/api/app/natal/config/dimensiones_v1.json`) y los 144 textos (`apps/api/app/content/carta_v1.json`, `revisado_por_pablo: false`). Los textos, y los de Tu día, van en la planilla de pendientes para Pablo.
- [ ] Mi carta v2: las otras 12 dimensiones del whitepaper, guardar respuestas a las preguntas (Destiny Mirror), regentes de casas.
- [x] **Astrochat** (spec X3): "Preguntale a Destiny" desde Hoy y Mi carta, 4 modos, en el estilo de la persona, con la carta y Tu día ya calculados (sin datos personales), límite diario, respuesta fija ante palabras de crisis (135 / 911) y borrar conversación.
- [ ] **Decisiones del Astrochat a revisar (German)**: el modo sale del estilo (directo → Explorador, práctico → Mentor, analítico → Técnico, intuitivo → Acompañante) y ya no se elige en la pantalla; límite de 10 preguntas por día; sin datos de conexiones; sin memoria a largo plazo. Todo se cambia en `app/astrochat/config/astrochat_v1.json`.
- [x] Astrochat v2 (más contexto): carta completa con aspectos natales, tránsitos de los próximos 30 días y test de personalidad (sin el eje E1, sensible).
- [ ] Astrochat v3: compatibilidad con tus conexiones (con consentimiento), memoria opcional, varias conversaciones, respuestas en streaming. Con créditos: preguntas extra con tokens. Decidir si se suma el eje E1 del test.
- [x] **Tu día completo** (spec B4 v3), primera versión de "Mi cielo": clima del día (Luna, fase y casa), los 3 tránsitos más fuertes de todos los planetas sobre la carta (con cuándo son exactos), estado por área y lectura con IA en el estilo de la persona.
- [ ] Mi cielo v2: "hoy fluye con…" (tránsitos cruzados con tus conexiones), filtros por área en el calendario, tránsitos de varios meses.
- [ ] Notas del día en el calendario (se sacan el 2026-10-20 para simplificar; volver a evaluar en otra versión).
- [ ] **Consentimientos y datos**: aceptar privacidad al empezar, ver/exportar/borrar mis datos, memoria del chat opcional.
- [ ] Timeline / Diario cósmico (fase 2 del whitepaper). Incluye volver a pedir el ánimo del día **con devolución** (una línea en "Tu día" según ánimo y tránsito, y patrones con el tiempo); el check-in se sacó de Hoy el 2026-10-13 porque no devolvía nada (endpoint y tabla quedan).
- [x] Navegación reorganizada (spec U1): Hoy · Mi carta · Descubrir · Conexiones · Perfil; Perfil corto; Hoy con jerarquía; Mi carta en pestañas; sistema visual común. Cuando lleguen Astrochat y Mi cielo, se suman a esta estructura.

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

**Ideas del análisis de competencia (NeoHumanCode, 2026-10-13; `docs/referencias/Analisis-NeoHumanCode.pdf`)**
- [x] **Compartir mi carta con un link** (spec A9): botón en Mi carta, link `/c/{token}` con vista previa para WhatsApp, Destiny filtra los datos, contador de vistas y "Dejar de compartir".
- [ ] Compartir mi carta v2: que quien se registra desde el link quede conectado con quien lo compartió; imagen de vista previa generada (rueda y nombre); informe de vínculo compartible (con consentimiento de las dos personas).
- [x] Mensaje de entrada que arranca por el problema: **"¿Por qué con algunas personas fluye y con otras no?"** (elegido por German, **aprobado por Pablo**) en la pantalla de entrada y en los mensajes de invitación por WhatsApp (C8 v3). Falta un video.
- [x] "Tu carta" en el registro (spec A8 v2): la rueda y la lectura de Identidad apenas se cargan los datos de nacimiento, antes de perfil y verificación.
- [ ] Canal de profesionales (Destiny Studio): referencia de precios de la competencia (~$11.100 por informe en suscripción). Post-MVP. **En pausa**: German decidió no planteárselo a Pablo por ahora.
- [ ] Cobrar con tokens un informe (de Mi carta o de vínculo). **En pausa**, mismo motivo; hoy compartir la carta es gratis (spec A9).

**Post-MVP**
- [ ] ~~AstroChat IA~~ → sube a prioridad en "Autoconocimiento primero" (arriba).
- [ ] Marketplace de astrólogos por zona + Destiny Studio (software para astrólogos) + AstroAcademy.
- [ ] Eventos tipo "Time left" (Cosmic Tables, speed dating, tribus, hosts).
- [ ] Destiny Pro (cofounder, mentores, networking).
- [ ] Monetización (Premium, Duo, informes, comisiones) — **después de los 6 meses gratis** (`ALCANCE_MVP.md`).

**Hiperpersonalización (idea de German y Pablo, 2026-10-13)** — aprovechar lo que Destiny sabe de cada persona para hablarle y mostrarse a su manera. Los estilos salen de **la astrología**, cada dimensión de un punto de la carta (parametrizable para que Pablo lo ajuste; la persona siempre puede cambiarlo y se le explica por qué):
- Cómo procesa la información (registro) → **Mercurio**: fuego directo, tierra práctico, aire analítico, agua intuitivo.
- Cuánta contención necesita (tono) → **Luna**.
- Qué formato le sirve → **modalidad dominante**: cardinal acciones, fija profundidad, mutable opciones.
- Estética → **Venus**; color principal del tema → **Ascendente** (o Sol sin hora exacta).
- [x] **v1 — estilo de redacción** (spec X2): estilo por carta, `GET/PUT /profiles/{id}/style`, explicaciones y 288 textos de "Tu día" por registro, tarjeta "Cómo te hablamos" en Mi perfil. Se queda con los 4 registros definidos (no los modos del whitepaper; decisión de German).
- [ ] Ok de Pablo a la hiperpersonalización cuando la vea en la app (mapeo y textos).
- [x] v2 — tema visual (spec X2 v2): paleta por elemento predominante de la carta (Fuego, Tierra, Aire, Agua o Clásico), con opción manual en "Tu estilo" de Mi perfil. Pendiente: ok de Pablo y modo claro / acento por Venus (v3).
- [x] v3 (spec X2 v3): acento por Venus, modo claro/oscuro (contraste WCAG medido en los 5 temas × 2 modos), tipografía de títulos por tema y fondo con el cielo de nacimiento (se puede apagar). Pendiente: ok de Pablo.
- [x] Fondo de la app: German eligió la constelación por defecto y que la persona pueda elegir entre los 4 (o ninguno) en Tu estilo.
- [ ] v4 — aprender del uso (👍/👎 en cada texto).

**Créditos en vez de Premium (idea de German y Pablo, 2026-10-13)** — una moneda propia (nombre de marca, no "tokens") para pagar por uso lo que tiene costo variable (AstroChat, informes, consultas, eventos), con el núcleo siempre gratis, créditos que se ganan con acciones (test, invitar, rachas de check-in) y paquetes para comprar (Mercado Pago, sin la comisión de las tiendas mientras sea app web). Libro de movimientos por usuario, todo parametrizable.
- [ ] Créditos: por ahora la moneda se llama **"token"** (decisión de German, 2026-10-13). **No es prioridad.** Falta definir qué cuesta y qué es siempre gratis.
- [ ] Propuesta para respetar los 6 meses gratis: lanzar primero solo **ganar y gastar** créditos (sin venta) para aprender qué valora la gente.
- [ ] Revisión legal del saldo prepago (Defensa del Consumidor: vencimiento, devoluciones, información de precios).

**Reunión de check con Pablo (2026-10-20)** — acta: `docs/reuniones/2026-10-20-check-pablo.html` (y PDF).
- [x] Pestaña "Respuestas" → **Indagar**; la caja para preguntar se titula "¿En qué necesitás claridad hoy?" en todos lados (spec U2).
- [x] Calendario: "Indagar sobre este día →" abre Indagar con la pregunta precargada y la IA recibe los datos de ese día (spec U2).
- [x] Se sacaron las notas del calendario de todos lados, incluidas las ya escritas (spec U2; había 1). El registro de ánimo queda.
- [x] Aviso de privacidad aceptado al registrarse (casilla obligatoria) y al empezar el test; se guarda versión y fecha (spec A12). Falta revisar si otros lugares lo necesitan.
- [x] Test ordenado según lo que busca la persona ("¿Qué buscás?" de Círculo se guarda en el perfil), pantalla de entrada a Atracción y "Responder más tarde"; aviso en Círculo para completarla (spec A12).
- [x] Tokens por invitar: +1 pregunta diaria en Indagar por cada amigo que se registra con tu invitación y la acepta, tope 20 (spec C11).
- [x] Círculo: foto de 128 px, número global y una columna de barras por sistema con el promedio por eje (spec B9, boceto de German).
- [x] Distancia: "¿Dónde vivís?" con el buscador de ciudades y filtro "a menos de X km" (spec B9).
- [x] Círculo: filtro de intereses (tiene que tener todos), "N intereses en común" en la tarjeta y desempate por intereses; filtros activos con ✕ (spec B10).
- [x] Número global en las tarjetas, provisorio con promedio simple de los sistemas (cada uno con los pesos de Pablo por vínculo), y filtro para apagar sistemas con aviso de precisión (spec B9, ADR 0014).
- [x] Ponderador entre sistemas: Pablo aprobó el promedio simple (2026-10-23, ADR 0014).
- [ ] Ajuste del ponderador por persona en el perfil (idea de la reunión; sin fecha).
- [ ] Ideas de viralización: "¿Cuánto fluimos?" (Compartir v2), imagen para historias, @ y QR.
- [ ] Pablo: qué pasa sin test, título "Química y atracción", modelo de numerología, Atracción en Indagar, fotos por elemento, gratis 6 meses y nombre del dominio. Todo junto, con los textos a revisar, en la planilla `docs/referencias/pendientes-pablo/Destiny-Pendientes-con-Pablo.xlsx` (2026-10-23).

**Propósito y principios (`docs/PROPOSITO.md`, 2026-10-23)**
- [ ] Revisar el documento con Pablo; la dirección "el vínculo como centro" cambia la tesis del pitch y se decide con él.
- [x] Niveles de compatibilidad con frase junto al número global (spec B13, rangos de Pablo, textos ajustados).
- [ ] Antes de la salida (decidir esta semana): número de compatibilidad con su origen y qué tan seguro es, aviso visible, mostrar también la invitación floja, rompehielos como sugerencia, textos que proponen ("¿te pasa?").
- [ ] Después de la salida: "esto no me representa", mandar hacia afuera, filtrar lo que engancha, usar Destiny sin astrología.
- [ ] En paralelo: sumar a un profesional de la psicología y diseñar el circuito del vínculo (sociograma como mapa, registro por vínculo, radar, pregunta para conversar).

**Hallazgos del agente breaker (2026-10-22)**
- [x] Robustez y validaciones: datos de nacimiento inválidos, Descubrir tolerante, fechas extremas, textos con nulos/invisibles, fotos por contenido, doble toque, webhook (spec R1).
- [x] Privacidad: deducir respuestas del test, triangular la distancia, bloqueo que no oculta (spec P2).
- [ ] Analizar si se puede deducir el género oculto con los filtros mutuos de pareja.
- [x] Concurrencia y flujos: conexiones duplicadas, límite de Indagar en paralelo, aviso de privacidad por WhatsApp, invitación con conexión previa, rechazo trabado (spec R2).
- [x] Segunda corrida del breaker y sus arreglos claros (spec R3): bloqueo por invitaciones y ficha, explicación con test completo, Círculo con cache por par, límites con pedidos simultáneos, "seguir con mi cuenta", cierre de sesión real.
- [ ] Probar a fondo el login "Ya tengo cuenta" (quedó sin probar contra la API en la segunda corrida).
- [ ] Antes de hosting real: `ENVIRONMENT=production` para que la cookie de sesión sea `Secure` (hallazgo 19).
- [ ] Email opcional (registro o Perfil) para poder contactar a usuarios: hoy no hay forma de escribirle a quien no verificó su WhatsApp (pasó con Iñaki, Miguel W. y Carla tras el bug de C13). Es un dato personal más: sumarlo al aviso de privacidad. Decidir junto con la validación de WhatsApp de producción (German, 2026-10-22).
- [ ] **Antes de producción: pedir validación de WhatsApp (o similar)** — decisión de German (2026-10-22). Cierra las cuentas descartables que permiten deducir el test, la ubicación y el género de otros (segunda corrida del breaker). Riesgo aceptado durante el piloto (spec A10).

**Fotos y búsqueda (pedido de Pablo, 2026-10-15)**
- [x] Fotos: hasta 4 con chequeo automático (spec A11, ADR 0013).
- [x] Descubrir: lupa por nombre, filtros por sistema, compatibilidad mínima y edad, género y "Mostrame" (spec B8).
- [ ] Reportar fotos y revisar a mano las "sin revisar".
- [ ] Fotos en almacenamiento en la nube (hoy disco de la Mac), junto con el hosting.
- [ ] Política de privacidad: avisar que las fotos se chequean con un proveedor externo (ADR 0013).
- [ ] Filtro por distancia (hace falta pedir ciudad o ubicación aproximada).
- [ ] Numerología como sistema de compatibilidad (modelo a definir por Pablo). **Propuesta v0 enviada para que corrija** (2026-10-22): `docs/referencias/numerologia/` (planilla con fórmulas y README).
- [ ] @ usuario y QR para compartir el perfil (spec C9).
- [ ] Qué compartir con cada conexión (idea de Pablo: fotos, carta, test, valores, metas; spec C10).
- [ ] Propuesta a Pablo: 4 fotos por elemento y Destiny elige cuál mostrar según el día (enviada por WhatsApp, sin respuesta).

**Decisiones pendientes para Pablo**
- [ ] Confirmar que la monetización queda para después del MVP 100 % gratis (regla de `ALCANCE_MVP.md`).
- [x] **RRHH con la carta natal** — **queda afuera por ahora** (decisión de German, 2026-10-13). Contexto: usar la carta para seleccionar o descartar candidatos tiene riesgo legal (discriminación, datos personales sensibles; sin evidencia de que prediga desempeño). Propuesta: Destiny Pro como networking y autoconocimiento voluntario, no selección de personal. Validar con un abogado.
- [x] Privacidad en comparaciones con terceros — **decidido: se pide consentimiento** de la otra persona (German, 2026-10-13).
- [ ] Implementar ese consentimiento: hoy la invitación astrológica (C8) calcula un adelanto con el signo que carga quien invita, antes de que el invitado acepte. Definir en la spec C8 cómo se pide el consentimiento (ej. mostrar el adelanto recién cuando el invitado acepta) y aplicarlo también a futuras comparaciones (Circle, constelación).



- [x] Test de personalidad de Pablo dentro del perfil (spec A6), fiel a su código (verificado contra 18 parejas de referencia).
- [x] Pesos por tipo de relación de la sinastría alineados con los de Pablo.
- [x] Invitación a comparar el test de personalidad (C8 v2) + panel "Compatibilidad" en todos los chats (B7): astrología y personalidad por separado, con selector de vínculo.
- [ ] **"Mi carta"**: pantalla para que cada usuario vea su carta natal (rueda zodiacal con planetas, ascendente y casas, más una lista en lenguaje simple: "Sol en Tauro", "Luna en Aries", etc.) y, opcional, la descargue en PDF. Ya se calcula todo en la API (`app/synastry/chart.py`); falta exponerla y dibujarla. Requiere spec + casos de prueba antes del código.
- [ ] Pantalla de administración para editar pesos y matrices sin tocar el JSON (hoy: editar `config/*.json` + commit).
- [ ] Que Pablo revise los textos de "Tu día" (`apps/api/app/content/transitos_v1.json`: 72 generales + 288 por estilo, hoy `revisado_por_pablo: false`). Pedido por WhatsApp el 2026-10-13.
- [x] ~~Que Pablo revise las tablas de sinastría provisorias~~ → reemplazadas por su motor oficial 1.0 (spec A7).

## Tests

- [x] Batería de tests automáticos de la API (`apps/api/tests/`, 77 casos, pytest, base `destiny_test`). Cubre A1, A3, A4, A5, B5 (motor y Descubrir), B6, B7 y C8.
- [ ] Tests de punta a punta en el navegador (Playwright): registro → verificación → Descubrir → conexión → chat.
- [ ] Tests de la web (componentes): hoy solo se chequean tipos con `tsc`.
- [ ] Correr los tests automáticamente en cada push (GitHub Actions con un Postgres de servicio).

## Tareas técnicas sueltas

**Verificación opcional (spec A10, 2026-10-14)**
- [x] Registro sin WhatsApp (sesión en el dispositivo), verificación desde Perfil, marca "Verificado" en Descubrir y pasar a WhatsApp solo verificado. Interruptor `VERIFICACION_OBLIGATORIA` para volver atrás.
- [ ] Antes de abrir a más gente: decidir si se pide verificar para algo más (ej. conectar) según cuántos perfiles falsos aparezcan.
- [ ] Recuperar una cuenta no verificada perdida no es posible: evaluar un recordatorio más fuerte después de unos días de uso.

**Revisión nocturna 2026-10-14: lo que quedó anotado (no es urgente o requiere decisión)**
- [ ] **Escala de Descubrir**: una sinastría del motor oficial tarda ~13 ms; Descubrir calcula una por candidato. Con miles de usuarios, precalcular o cachear (por pareja + versión de tablas).
- [ ] La lista de años del registro se arma con el año del build: si no se recompila, en enero falta el año nuevo y React avisa un desajuste. Generarla en el navegador.
- [ ] Decidir: las pantallas del registro son más angostas (`max-w-sm`) que las de la app (`max-w-md`).
- [ ] Decidir: el chat entre personas tiene un botón naranja "Enviar", mientras que Respuestas usa el link "Preguntar →".
- [ ] Si la sesión vence sin "Cerrar sesión", el estilo visual de la persona queda guardado en el dispositivo hasta que alguien inicie sesión.
- [ ] Algunas acciones (aceptar o rechazar una conexión, bloquear) no muestran aviso si falla la API.
- [ ] Aceptado por diseño, para tener presente: un perfil todavía sin verificar se puede leer sin sesión con su id (UUID imposible de adivinar), incluida la síntesis de Mi carta, que puede llamar a la IA.

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
