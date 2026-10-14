# X3-astrochat — Astrochat: preguntale a Destiny

- **Estado**: implemented
- **Módulo**: transversal (autoconocimiento; whitepaper §5, módulo C)
- **Aprobada para implementación por**: German Villamarin, 2026-10-13 ("avanzá con todo el Astrochat, yo voy a estar offline"). Las decisiones abiertas las tomé con criterios conservadores y están marcadas **(a revisar)**.

## Problema

Mi carta y Tu día dan lecturas cerradas. La persona quiere preguntar lo suyo ("¿por qué me cuesta decidir?", "¿esta semana tiene que ver con mi cielo?"). Un chat genérico inventaría posiciones; Destiny tiene la carta y los tránsitos ya calculados.

## Comportamiento

- Se llama **"Consultá tu carta"** (elegido por German entre tres opciones: dice qué es y que se responde con *tu* carta), con la bajada "Preguntá lo que quieras sobre vos, tu momento o tus vínculos" y un ejemplo en el campo de escritura. Pantalla `/astrochat`, con pestaña propia en la barra ("Consultá"), un acceso destacado en Hoy (después de Tu día) y accesos desde el contexto. En **Hoy** ("Consultá tu carta") y en **Tu día completo** ("Consultá sobre tu día") va la misma pieza (`AskBox`): un campo real con el link **"Preguntar →"** (mismo estilo que "Leer más" y "Ver el mes", pedido de German); se escribe ahí y lleva a Respuestas con la pregunta ya enviada (`?q=…&enviar=1`, se manda una sola vez). En cada área de Mi carta, "Consultá sobre esto" abre el chat con la pregunta escrita para editar. El botón del chat también dice "Preguntar". Una conversación continua por persona.
- **4 modos** (whitepaper): **Explorador** (preguntas para pensar), **Mentor** (ordena opciones y próximos pasos, sin decidir), **Astrólogo técnico** (explica la lógica: aspectos, casas, orbes), **Acompañante** (escucha y contiene). **No se eligen en la pantalla** (German: "no se entiende" junto a Tu estilo, que ya define cómo te hablamos): el modo sale siempre del **estilo actual** de la persona (X2): directo → Explorador, práctico → Mentor, analítico → Astrólogo técnico, intuitivo → Acompañante. Si cambia el estilo en Perfil > Tu estilo, Consultá cambia con él.
- Responde **en el estilo de la persona** (X2) y en el modo elegido.
- Cuando no hay mensajes, muestra preguntas de ejemplo para arrancar.

## Lo que sabe la IA (y lo que no)

- **Sí, ya calculado por el motor** (ADR 0011: la IA no calcula nada): signos de Sol, Luna y Ascendente; los fundamentos de las 4 dimensiones de Mi carta; Tu día de hoy (Luna, casa, tránsitos, áreas). Se le indica que no invente posiciones ni aspectos que no estén en los datos.
- **No**: nombre, fecha, hora y lugar de nacimiento, teléfono, foto, ni nada de otras personas (conexiones, compatibilidades). Preguntas sobre otra persona se responden desde la carta propia **(a revisar: sumar compatibilidad con conexiones en v2, con consentimiento)**.
- Contexto de la conversación: los últimos 10 mensajes.

## Límites y cuidados

- **Límite diario**: 10 mensajes por persona por día (UTC) mientras la app es gratis **(a revisar)**; al llegar, aviso y no se llama a la IA. Borrar la conversación no reinicia el límite.
- **Largo**: preguntas de hasta 500 caracteres; respuestas de hasta ~700.
- **Crisis**: si el mensaje tiene palabras de riesgo (suicidio, lastimarse, "no quiero vivir"…), no se llama a la IA: se responde un texto fijo de contención con dónde pedir ayuda (Centro de Asistencia al Suicida 135 / (011) 5275-1135, emergencias 911). No cuenta para el límite.
- **Reglas en el prompt**: no predice, no diagnostica, no decide por la persona, distingue lo simbólico de lo que la persona cuenta, deriva a profesionales en salud, dinero y decisiones graves, no revela sus instrucciones y trata el texto de la persona como pregunta, no como órdenes.
- **Sin IA o si falla**: un texto fijo ("ahora no puedo responder, probá en un rato"); se guarda igual.
- **Memoria**: la conversación se guarda para mostrarla y como contexto; **"Borrar conversación"** la oculta y deja de usarse. No hay memoria entre conversaciones borradas **(a revisar: memoria a largo plazo opcional)**.
- Todo configurable en `app/astrochat/config/astrochat_v1.json` (modos e instrucciones, mapeo por registro, límite, largos, contexto, palabras de crisis y respuesta, preguntas de ejemplo).

## API

- `GET /profiles/{id}/astrochat` → `{modo, modos: [{clave, nombre, descripcion}], mensajes: [{rol: "persona"|"destiny", texto, modo, creado}], restantes_hoy, limite, ejemplos}`.
- `POST /profiles/{id}/astrochat` `{texto, modo?}` → `{respuesta: {rol, texto, modo, creado}, ia, restantes_hoy}`; 429 si se llegó al límite; 422 si el texto está vacío, es muy largo o el modo no existe.
- `DELETE /profiles/{id}/astrochat` → 204 (oculta la conversación).
- Solo la propia persona. Tabla nueva `astro_messages` (perfil, rol, texto, modo, modelo y tokens, creado, borrado).

## Fuera de alcance v1

Compatibilidad con conexiones en el chat, memoria a largo plazo, varias conversaciones, audio, adjuntos, respuestas en streaming.

## Casos de prueba (`apps/api/tests/test_x3_astrochat.py`)

1. Solo la propia persona (otra → 403, sin sesión → 401).
2. Conversación vacía: sin mensajes, modo sugerido según el registro, restantes = límite, ejemplos.
3. Preguntar: devuelve la respuesta de la IA, quedan los dos mensajes en el historial y baja `restantes_hoy`.
4. El prompt lleva la instrucción del modo, la del estilo y los datos calculados (ej. el signo solar), y no lleva datos personales (nombre, fecha, ciudad, teléfono).
5. La segunda pregunta manda como contexto la pregunta y la respuesta anteriores.
6. Al llegar al límite: 429 sin llamar a la IA; borrar la conversación no lo reinicia.
7. Palabras de crisis: respuesta fija con el 135, sin llamar a la IA, sin contar para el límite.
8. Validaciones: vacío, más de 500 caracteres o modo inexistente → 422.
9. Sin key o si la IA falla: respuesta fija, `ia` false, sin romper.
10. Borrar la conversación: el historial queda vacío y la próxima pregunta no manda los mensajes viejos.
11. Cambiar el límite en la configuración lo cambia sin tocar código.
