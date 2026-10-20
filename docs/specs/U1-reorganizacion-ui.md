# U1-reorganizacion-ui — Reorganización de la interfaz

- **Estado**: implemented
- **Módulo**: transversal (web)
- **Aprobada para implementación por**: German Villamarin, 2026-10-13 ("hacer todo", sobre la revisión de UI).

## Problema

Con todo lo que se agregó la app quedó amontonada: Mi carta (lo central del autoconocimiento) escondida en Perfil, Calendario ocupando una pestaña, Mi perfil con seis cosas en un scroll larguísimo, Inicio con bloques sin jerarquía, Mi carta con textos largos y estilos de tarjeta distintos en cada pantalla.

## Cambios

**A. Navegación (5 pestañas)**: **Hoy** (`/home`) · **Mi carta** (`/carta`) · **Descubrir** · **Conexiones** · **Perfil**. Calendario deja de ser pestaña: se abre desde Hoy ("ver el mes") y queda marcado como Hoy. `/perfil/carta` redirige a `/carta`.

**B. Perfil corto** (`/perfil`): encabezado con avatar, nombre y "☉ signo · ☽ signo · AC signo" (sin hora exacta, sin AC) y una lista de filas, cada una a su pantalla: Editar perfil (`/perfil/editar`), Datos de nacimiento (edición existente), Tu estilo (`/perfil/estilo`), Test de personalidad (`/perfil/test`), Invitar a alguien (`/invitar`), Cerrar sesión.

**C. Hoy con jerarquía**: 1) Tu día (protagonista); 2) ~~ánimo~~ (sacado el 2026-10-13, ver B4); 3) los próximos 3 días importantes con "Ver el mes →"; 4) lo social en una tarjeta: solicitudes de conexión, invitaciones y "N personas en tu frecuencia → Descubrir"; 5) acceso a Mi carta si todavía no la abrió (no se recuerda: se muestra siempre como fila corta).

**D. Mi carta** (`/carta`): Tu cielo (rueda + leyenda) arriba, las 4 dimensiones en **pestañas** (Identidad · Amor · Vocación · Emociones), síntesis con 3 líneas y "Leer más", "En qué se basa" desplegable, y el test de personalidad como fila al final.

**E. Sistema visual común** (`src/components/ui.tsx`): `Page` (contenedor + barra), `PageTitle`, `Card`, `SectionTitle`, `ListRow`. Un único estilo de tarjeta (`bg-slate-900` con borde `slate-700`; el borde dorado solo para lo destacado del día) y el mismo espaciado. Las pantallas de las pestañas lo usan.

## Sumado durante la implementación (German)

- **Fondos a elección**: la constelación por defecto y los 4 fondos (y "sin fondo") para elegir en Tu estilo; tarjetas semitransparentes con desenfoque para que el fondo se asome; "Ver fondo" oculta el contenido hasta tocar la pantalla (spec X2 v3). Se sacó la página de prueba `/fondos`.

## Fuera de alcance

Rediseño de Descubrir, Conexiones, chat y onboarding (solo pasan a usar `Page`/`PageTitle` si es directo). 

## Casos de prueba (manuales, en el navegador en tamaño celular; no hay cambios de API)

1. La barra muestra Hoy, Mi carta, Descubrir, Conexiones, Perfil; en `/calendario` queda marcada Hoy; en `/perfil/*` queda marcado Perfil.
2. `/perfil/carta` lleva a `/carta`.
3. Perfil muestra el encabezado con los signos y las 6 filas; cada fila abre su pantalla y "Cerrar sesión" sale.
4. `/perfil/editar` guarda el perfil como antes; `/perfil/estilo` cambia estilo, colores, modo y fondo como antes.
5. Hoy muestra Tu día primero, los próximos 3 días con "Ver el mes" y la tarjeta social con link a Descubrir.
6. Mi carta muestra la rueda y una dimensión por pestaña; "Leer más" despliega la síntesis completa.
7. Los tests de la API siguen en verde y la web compila sin errores de tipos.

## Ajustes de Hoy (German, 2026-10-13, con boceto)

- Encabezado: "Hoy:" + el título del día (en el color del texto, sin negrita), la fase de la Luna abajo y el texto del día debajo, sin repetir "Tu día · Luna en…" ni recuadro.
- El llamado a la lectura completa es un link "Leer más →" debajo del texto, con el mismo estilo que "Ver el mes" (German probó un botón y prefirió el link).
- Próximos días: arriba el día y la descripción ("Vie 16 oct · Día fluido"), abajo el detalle; "Ver el mes →" va al final, adentro del recuadro.

## Barra v2 (German, 2026-10-13)

**Hoy · Carta · Respuestas · Círculo · Perfil** (German: palabras cortas en la barra; para el Astrochat se compararon Guía, Claridad, Luz, Clave, Lente, Chat, Charla y Oráculo, y German eligió "Respuestas" porque lo que la persona busca es resolver sus dudas; "Oráculo" se descartó porque promete predecir y Destiny no predice; la calidez va en los títulos de cada pantalla: "Mi carta", "Consultá tu carta", "¿Con quién fluye?". Antes se probó "Vínculos" y la primera persona). Descubrir y los chats se juntaron en **Círculo**, con el gancho como título ("¿Con quién fluye?") y dos solapas (Descubrir · Mis chats), para darle su lugar en la barra a **Consultá tu carta** (Astrochat, spec X3). En Hoy, la sección se llama "Tu círculo". Los botones de la barra tienen el mismo ancho y el texto puede ir en dos líneas.

## Mi carta v2 (German, 2026-10-14, con captura)

- Solapas **Identidad · Amor · Vocación · Emociones · Cielo**: la rueda pasa a ser la pestaña **Cielo** (más chica, con Sol, Luna y Ascendente explicados), en vez de estar suelta arriba sin explicación.
- Cada área muestra el **texto completo** (sin "Leer más") y "En qué se basa →" como link discreto a la derecha (es la trazabilidad que distingue a Destiny). Se saca "Consultá sobre esto" (repetía "Preguntá sobre tu carta", que está debajo).
- **Compartir →** arriba a la derecha, junto al título, con la aclaración debajo ("se comparten solo tus signos y lecturas…") y, si ya se compartió, las vistas y "Dejar de compartir".
- **Solapas con un estilo común** (`segmentClass` en `ui.tsx`), también en Círculo: la seleccionada en un tono neutro, para no confundirse con los links de acción.

## Unificación visual (revisión nocturna, 2026-10-14)

- **Opciones seleccionadas en tono neutro** en toda la app (Tu estilo, Descubrir, panel del chat, invitar, test, perfil, franjas del registro), igual que las solapas: el color de acción queda solo para links y botones. Excepción: el ranking de respuestas del test, donde el color marca el orden de preferencia.
- **Tarjetas con el mismo radio** (`rounded-xl`) en las pantallas viejas (calendario, chat, conexiones, invitar, registro, verificación); los campos de texto y menús mantienen su radio.

**Cambio posterior (2026-10-20, spec U3)**: Círculo ya no tiene las solapas Descubrir / Mis chats: las conexiones van en una franja arriba de Descubrir y la lista completa en "Ver todas →".
