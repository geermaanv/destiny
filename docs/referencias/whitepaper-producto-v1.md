# Whitepaper de producto v1 (Destiny)

Texto extraído del PDF `Destiny_Whitepaper_Producto_y_Especificacion_v1.pdf` (13/10/2026) que pasó German como notas de la charla con Pablo. Las flechas del original se perdieron en la extracción (→ entre pasos). Estado: propuesta, a revisar.

```text
DESTINY
Whitepaper de producto y especificación funcional inicial
Perfil astrológico personalizable · Calendario de tránsitos · Astrochat IA · Memoria de evolución
Versión 1.0  |  13 de octubre de 2026  |  Documento para equipo de desarrollo
ESTADO: propuesta de producto. Los criterios, prioridades y parámetros marcados como sugeridos 
requieren validación antes de implementación.
Resumen ejecutivo
Destiny será una plataforma de autoconocimiento astrológico personalizado. Integra tres módulos 
inseparables: (1) perfil natal, (2) calendario individual de tránsitos y (3) asistente conversacional con 
IA. Una cuarta capa, Timeline, registra experiencias y reflexiones de manera opcional. El primer 
caso de uso es el autoconocimiento, no el matchmaking; los futuros productos reutilizarán el motor 
natal y de aspectos.
1. Propuesta de valor y principios
 ¿Quién soy? Perfil natal organizado por áreas de vida, no solo por posiciones planetarias.
 ¿Qué ocurre en mi cielo? Tránsitos reales calculados respecto de mi carta y filtrables por temas.
 ¿Cómo lo interpreto? Astrochat contextual con estilos conversacionales elegidos por el usuario.
 ¿Cómo evoluciono? Diario, decisiones y revisiones longitudinales opcionales.
 Separar siempre cálculo astronómico verificable de interpretación simbólica. La astrología no 
debe presentarse como diagnóstico o predictor científico validado de personalidad o resultados.
2. Flujo de usuario y navegación
Onboarding: crear cuenta  aceptar privacidad/consentimientos  nombre visible y datos de → →
nacimiento (fecha, hora exacta o desconocida, ciudad/país)  resolución de zona horaria histórica  → →
cálculo natal  selección/edición del tema visual  vista de perfil  calendario y chat.→ → →
Navegación sugerida: Inicio / Mi perfil / Mi cielo / Astrochat / Mi evolución; ajustes accesibles desde 
avatar. Si se desconoce la hora natal, ocultar o etiquetar como inciertos Ascendente, MC y casas, y 
reducir el alcance de las interpretaciones dependientes de ellos.
3. Módulo A — Perfil Destiny
3.1 Datos y cálculo natal
 Entradas: nombre o alias, fecha de nacimiento, hora, lugar normalizado, zona horaria, 
preferencias de sistema de casas y zodíaco según configuración del producto.
 Resultados estructurados: longitudes eclípticas, signos, casas, cúspides, ángulos, aspectos natales 
y orbes; conservar versión de efemérides y parámetros usados.
 El perfil interpretativo consume resultados calculados; nunca debe depender de cálculos 
inventados por el modelo de IA.


3.2 Identidad visual adaptable
Generar tema visual a partir de predominancia elemental ponderada de planetas y puntos elegidos. 
Fórmula sugerida: P(e) = suma_i [w_i × I(elemento_i = e)] / suma_i w_i. Los pesos y el conjunto de 
puntos serán configurables y versionados; no hay pesos definitivos aprobados.
Elemento Paleta orientativa Lenguaje visual
Fuego Rojo profundo / terracota / 
dorado
Expresivo, contraste cálido
Tierra Verde bosque / arena / cobre Orgánico, sobrio
Aire Azul claro / plata / lavanda Ligero, geométrico
Agua Índigo / océano / violeta Fluido, contemplativo
Sol, Luna y Ascendente pueden influir en símbolos y acentos. Mantener navegación, contrastes 
WCAG y tipografía de lectura consistentes. El usuario puede sobrescribir el tema automático, activar 
modo claro/oscuro y reducir movimiento.
3.3 Taxonomía de autoconocimiento
Dimensión Pregunta central
Identidad y propósito ¿Quién soy y qué me mueve?
Amor y vínculos ¿Cómo amo y me vinculo?
Deseo y sexualidad ¿Qué me atrae y cómo deseo?
Mente y aprendizaje ¿Cómo pienso y aprendo?
Comunicación ¿Cómo expreso mis ideas?
Seguridad emocional ¿Qué me da estabilidad?
Vocación y carrera ¿Dónde puedo desarrollarme?
Dinero y recursos ¿Cómo me relaciono con lo material?
Amistades y comunidad ¿Cómo construyo pertenencia?
Familia y raíces ¿Qué necesito de mi hogar?
Talentos y fortalezas ¿Qué puedo potenciar?
Desafíos y crecimiento ¿Qué patrones puedo trabajar?
Decisiones y autonomía ¿Cómo elijo?
Creatividad y expresión ¿Cómo expreso mi singularidad?
Servicio y contribución ¿Qué puedo aportar?
Espiritualidad y sentido ¿Cómo busco sentido?
Cada dimensión tendrá: (i) síntesis accesible, (ii) fundamentos astrológicos trazables (planetas, casas, 
aspectos, regencias) y (iii) preguntas de reflexión que el usuario puede aceptar, matizar o rechazar. 
Se requiere una matriz editorial dimensión  indicadores astrológicos, a definir y revisar por →
especialistas.


4. Módulo B — Calendario astrológico individual
Motor determinista de efemérides: posiciones planetarias por fecha/hora, aspectos mayores y 
menores, orbes, tránsitos sobre planetas/ángulos natales, ingresos, estaciones/retrogradaciones, 
fases lunares y eclipses. Tránsitos rápidos requerirán resolución temporal subdiaria. 
Almacenamiento de intervalos de activación, exactitudes, hora local y UTC.
Vista día/semana/mes; fichas de cada evento con planeta transitante, punto natal, aspecto, orbe, 
fecha de máxima exactitud, período activo y explicación. Filtros por área de vida. Progresiones, 
direcciones y revoluciones solares quedan para fases posteriores.
Índice de intensidad simbólica: puntaje interno opcional que combine cercanía del orbe, duración y 
relevancia natal; NO equivale a probabilidad de que ocurra un evento. Debe ser explicable, editable 
y sometido a pruebas.
5. Módulo C — Astrochat IA
Asistente con acceso autorizado a carta calculada, eventos de calendario, interpretaciones curadas, 
preferencias y memoria optativa. La IA debe invocar funciones internas para obtener cálculos y no 
generar efemérides sin respaldo.
Modo Comportamiento
Explorador Preguntas reflexivas; ayuda a contrastar 
hipótesis con experiencia
Mentor Ordena alternativas, riesgos y próximos pasos; 
no decide por el usuario
Astrólogo técnico Explica orbes, regencias, casas y lógica de la 
lectura
Acompañante Escucha y propone reflexión sin afirmaciones 
deterministas
Ajustes: longitud, tecnicismo, tono, frecuencia de preguntas, memoria activada/desactivada. 
Respuestas deben distinguir datos astronómicos, interpretación simbólica y datos autobiográficos 
del usuario. Admitir incertidumbre y ausencia de configuraciones relevantes.
6. Módulo D — Destiny Timeline
Registro voluntario de acontecimientos, estados de ánimo, objetivos y decisiones. Asociar cada 
entrada con fecha/hora y snapshot de tránsitos, sin atribuir causalidad. Permitir búsquedas, 
revisiones periódicas y comparación entre expectativas y resultados. Entradas 
editables/exportables/eliminables; memoria de IA granular y revocable.
7. Extensiones diferenciales
 Destiny Mirror: cuestionario de autopercepción comparado con hipótesis interpretativas del 
perfil.
 Destiny Paths: ayuda a estructurar decisiones y sus consecuencias prácticas; tránsitos como 
contexto de reflexión, no instrucciones.


 Destiny Rituals: ejercicios opcionales de escritura, revisión de objetivos y creatividad vinculados 
a ciclos elegidos.
 Matchmaking, amistades, eventos, comunidad, directorio de astrólogos y Destiny Pro como 
productos posteriores reutilizando la infraestructura natal.
8. Arquitectura de referencia
Servicio / dominio Responsabilidad
Identidad y consentimiento Cuentas, preferencias, acceso, permisos y 
borrado
Cálculo astrológico Efemérides, cartas natales, casas, aspectos y 
tránsitos
Interpretación estructurada Taxonomía, reglas, contenidos y versiones
Calendario Eventos derivados, filtros, caché y 
notificaciones
Orquestador de IA Herramientas, contexto, prompts, trazabilidad 
y seguridad
Timeline Diario, reflexiones, objetivos y recuperación 
autorizada
Diseño / temas Tokens visuales y accesibilidad
Analítica Eventos de producto, métricas agregadas y 
experimentos
Flujo de datos: entrada natal  normalización geográfica/temporal  motor de efemérides  carta → → →
estructurada  motor de perfil y eventos de tránsito  APIs de calendario/tema  orquestador → → →
Astrochat. Timeline y preferencias solo se incorporan al contexto cuando existe consentimiento.
Tecnología sugerida, no vinculante: backend con API versionada y trabajos programados; base 
relacional para usuarios/cartas/eventos; almacenamiento seguro para diarios; capa de caché para 
efemérides; frontend móvil/web con design tokens. Evaluar Swiss Ephemeris u otra librería 
astronómica validada, incluyendo licencias de uso comercial.
9. Contratos de datos mínimos
User: user_id, display_name, locale, timezone, consent_flags. BirthData: birth_date, birth_time, 
time_accuracy, birthplace_id, latitude, longitude, timezone_id. NatalChart: chart_id, user_id, 
calculation_version, zodiac, house_system, placements[], houses[], angles[], aspects[]. TransitEvent: 
event_id, chart_id, moving_body, natal_target, aspect_type, orb, exact_at_utc, active_from_utc, 
active_to_utc, topic_tags[]. ChatPreference: mode, tone, depth, memory_enabled. TimelineEntry: 
entry_id, user_id, occurred_at, text, tags, visibility, transit_snapshot_id.
Todas las entidades sensibles deben soportar control de acceso por usuario, auditoría, eliminación y 
exportación. Los contratos finales deben definirse con esquemas JSON, validación y migraciones.


10. Requisitos no funcionales y controles
 Privacidad por diseño: minimización de datos, cifrado en tránsito y reposo, controles de acceso, 
eliminación/exportación, política de retención y consentimiento separado para memoria.
 Seguridad IA: protección frente a prompt injection, herramientas con permisos acotados, filtros 
para información sensible, límites de uso y observabilidad.
 Accesibilidad: contraste suficiente, tamaños escalables, navegación por teclado/lector de 
pantalla y opción de desactivar animaciones.
 Exactitud técnica: pruebas con cartas y tránsitos de referencia, husos horarios históricos, 
horario de verano, fechas límite y hora natal desconocida.
 Explicabilidad: mostrar fuentes del cálculo, parámetros, orbe y versión de la interpretación.
 Evitar consejos categóricos en salud, finanzas o decisiones de alto impacto; ofrecer marcos de 
reflexión y derivación a profesionales cuando corresponda.
11. MVP y fases
Fase Alcance Criterio de salida
MVP 1 Cuenta, carta natal, 4 
dimensiones (identidad, amor, 
vocación, emociones), 4 temas, 
tránsitos principales, chat 4 
modos
Cálculos validados; flujo 
completo; permisos y 
seguridad básicos
Fase 2 16 dimensiones, calendario 
avanzado, Timeline, 
notificaciones, temas 
ampliados
Retención y satisfacción; 
explicabilidad y privacidad 
verificadas
Fase 3 Mirror, Paths, Rituals, 
matchmaking y servicios 
sociales
Validación de demanda y 
arquitectura reutilizable
12. Métricas de producto
Activación: % que completa datos natales y consulta perfil; % que visita calendario y envía primera 
pregunta. Engagement: WAU/MAU, sesiones útiles, retorno D7/D30, consultas al chat por usuario 
activo. Calidad: exactitud de cálculos, respuestas sin datos inventados, utilidad percibida, tasa de 
corrección. Negocio: conversión a pago, retención por cohorte, churn, costo de IA por usuario. No 
perseguir engagement a costa de bienestar o privacidad.
13. Backlog técnico priorizado
 P0: definir supuestos astrológicos, fuente de efemérides, licencia, reglas de huso horario y 
sistema de casas.
 P0: diseñar esquema natal versionado y API de cálculo con fixtures de referencia.
 P0: implementar onboarding, consentimiento, incertidumbre de hora natal y edición de datos.
 P0: motor de temas visuales y cuatro plantillas accesibles.
 P0: primeras cuatro dimensiones con trazabilidad de indicadores y contenido editorial.
 P0: servicio de tránsitos y calendario de eventos principales.


 P0: Astrochat con herramientas internas, cuatro modos, controles de contexto y límites.
 P1: ampliar taxonomía a 16 dimensiones, memoria optativa y Timeline.
 P1: notificaciones y filtros temáticos; analítica y experimentación.
 P2: módulos sociales, matchmaking y productos profesionales.
14. Decisiones pendientes para el programador / product owner
 Zodíaco tropical o sideral; sistema de casas predeterminado; cuerpos y puntos incluidos.
 Pesos de predominancia elemental, criterios de tema visual y matriz dimensión  indicadores.→
 Lista de aspectos, orbes y jerarquía de tránsitos; frecuencia de actualización.
 Reglas de interpretación, corpus editorial y proceso de revisión por astrólogos.
 Alcance de memoria, retención, edad mínima, política de datos y jurisdicciones de lanzamiento.
 Stack, presupuesto de infraestructura e IA, licencias y estrategia móvil/web.
 Límites y beneficios del plan gratuito frente a Destiny Plus.
15. Criterios de aceptación del MVP
 Un usuario puede registrarse, editar nacimiento y regenerar carta y perfil sin inconsistencias.
 Los cálculos coinciden con un conjunto documentado de casos de referencia.
 Con hora desconocida, el sistema no afirma casas ni ángulos como exactos.
 El tema automático es coherente con parámetros versionados y puede reemplazarse 
manualmente.
 Cada tránsito visible muestra geometría y fecha de cálculo; el chat utiliza exactamente esos 
datos.
 Los cuatro modos de Astrochat producen estilos diferenciados sin cambiar hechos astronómicos.
 El usuario puede ver, exportar y borrar su información personal y controlar la memoria.
 La experiencia es accesible en móvil y desktop y soporta estados de carga/error.
Conclusión
Destiny debe construir una experiencia continua: perfil natal como fundamento, calendario como 
actualización temporal, Astrochat como capa de interpretación y Timeline como memoria 
voluntaria. La prioridad de ingeniería es un núcleo de cálculo fiable, una estructura de 
conocimiento trazable y un sistema de consentimiento robusto. El matchmaking y los servicios de 
comunidad se incorporarán sobre esa base, no como dependencia del lanzamiento inicial.
```
