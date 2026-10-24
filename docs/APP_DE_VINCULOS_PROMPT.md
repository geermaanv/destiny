# App de vínculos: prompt de diseño (v1)

> Prompt para pedirle a Claude el documento funcional de la app de vínculos (`docs/APP_DE_VINCULOS.md`). Conviene correrlo en dos pasos: primero la fase 1 (conceptos); elegir o combinar; después pedir la fase 2 (documento) sobre el concepto elegido.

```markdown
Actuá como Principal Product Designer con foco en psicología conductual y en productos de mínima fricción, junto con un psicólogo clínico especializado en vínculos. Tu trabajo no es escribir un documento correcto: es encontrar una solución que no exista todavía y que sea mucho mejor que lo obvio.

## El desafío

Diseñar la mejor forma de ayudar a las personas a mejorar sus vínculos (pareja, amistad, familia, trabajo) con el menor esfuerzo personal posible.

Qué significa "increíble" acá:
- Requiere casi nada: la persona siente que la ayuda sin tener que hacer el trabajo.
- Cambia algo real afuera de la pantalla: una conversación, un reencuentro, un vínculo reparado.
- Tiene momentos que la gente cuenta a otros sin que se lo pidan.
- Se siente humano, no una herramienta de gestión de contactos.

## Lo único que no se negocia

- Herramienta, no oráculo: ofrece una mirada, no la verdad; la decisión siempre es de la persona.
- Nunca la única voz: manda hacia afuera (la persona, alguien de confianza, un profesional).
- Pensamiento propio: más preguntas que respuestas; la persona puede decir "esto no me representa".
- Transparencia: de dónde sale cada cosa y qué tan segura es.
- Éxito no es dependencia: si la persona cuida mejor sus vínculos y usa menos la app, ganamos. Nada de rachas, premios para engancharte, métricas de vanidad ni avisos que generen culpa.
- Nunca etiqueta personas ("tu amigo es tóxico") y nunca puntúa a nadie.
- No lee mensajes ni chats de nadie, ni sigue la ubicación de nadie.
- Ante señales de violencia o control, no analiza: deriva a recursos (en Argentina, Línea 144).
- Consentimiento: nada sobre otra persona se comparte sin que esa persona lo acepte.

Todo lo demás está abierto, incluso que sea una app.

## Ideas de partida (no son límites: superalas, combinalas o descartalas)

- El vínculo entre dos personas como centro, en lugar del perfil.
- Dos miradas sobre el mismo vínculo, si las dos personas quieren participar.
- Un mapa de tus vínculos en círculos (íntimo, cercano, amplio), donde ubicás a cada uno vos.
- Un radar por vínculo con pilares de la investigación: reciprocidad, seguridad, reparación, energía, cercanía y crecimiento, más la ecología de la red (no depender de una sola persona ni descuidar el círculo íntimo).
- Recordatorios con motivo y no con culpa, al ritmo que elige cada uno, que aprenden y a veces sugieren una pausa.
- Ayuda para reparar un vínculo o preparar una conversación difícil, sin ser terapia.

## Saber cómo está un vínculo preguntando lo mínimo

Nadie va a cargar todo a mano. La app tiene que saber lo suficiente con muy pocas preguntas. No busca medir con exactitud, sino tener la información suficiente para hacer una buena pregunta, aceptando equivocarse y que la persona la corrija. Algunas direcciones posibles, para tomar como punto de partida, no como lista cerrada:

- Preguntar menos y mejor: una pregunta por vez, rotando personas y pilares (muestreo de experiencias); en el momento justo; de un toque; por voz.
- Repartir las preguntas entre las dos personas del vínculo.
- Aprender de lo que la persona ya hace: si actúa o ignora un recordatorio, si mueve a alguien de círculo.
- Valores por defecto por tipo de vínculo, que la persona solo corrige si quiere.
- Señales del celular, con permiso explícito: calendario, contactos y favoritos, registro de llamadas (solo Android), fotos, exportar un chat de WhatsApp de forma voluntaria.
- Hablar por un canal que la persona ya usa, como WhatsApp.

Buscá formas mejores que estas. Para cada fuente que propongas: qué mide, cuánto esfuerzo pide, qué tan invasiva es y si involucra datos de terceros.

## Contexto

- Mercado inicial: Argentina y Latinoamérica, en español rioplatense.
- Antecedentes:
  - Paired, Gottman Connect, Relish y Wefeel cubren solo pareja.
  - Co-Star y The Pattern son compatibilidad astrológica con tono de oráculo.
  - Timeleft y Bumble BFF sirven para conocer gente nueva, no para cuidar a la que ya tenés.
  - Dex, Clay, Bond y Orbits son agendas o mapas de contactos que se quedan en "acordate de escribirle".
  - Nadie junta autoconocimiento, todos los vínculos, las dos miradas y el mapa de la red.

## Cómo trabajar

### Fase 1: explorar (antes de escribir el documento)

1. **La solución obvia.** Describí en un párrafo lo que haría cualquiera (probablemente: una app con recordatorios, un mapa y un radar) y explicá por qué no alcanza para ser increíble.
2. **Las personas.** Imaginá tres personas concretas de Argentina, con vidas distintas, y qué les pasa con sus vínculos. Diseñá para ellas.
3. **Romper el marco.** Pensá desde preguntas como:
   - ¿Qué hacen las personas que cuidan muy bien sus vínculos, sin ninguna app?
   - ¿Y si casi nunca hubiera que abrir la app? ¿Y si no fuera una app?
   - ¿Qué se puede aprender de otros campos (medicina preventiva, jardinería, rituales, diarios personales, Spotify Wrapped, entrenadores personales)?
   - ¿Qué momento de la vida de un vínculo nadie está acompañando hoy?
   - ¿Qué haría falta para que la persona sienta que la app la conoce, sin haberle contado casi nada?
4. **Conceptos.** Proponé entre 5 y 7 conceptos de producto realmente distintos entre sí, no variaciones de uno. Para cada uno: la idea en una frase, cómo funciona, el momento "mágico", cuánto esfuerzo pide y su mayor riesgo. Incluí al menos uno que suene demasiado audaz.
5. **Evaluar.** Compará los conceptos contra estos criterios: impacto real en los vínculos, esfuerzo para la persona, respeto de los principios, si dan ganas de contarlo y viabilidad. Elegí uno o una combinación, y explicá por qué.

Si este prompt se corre en dos pasos, frená acá y esperá la elección.

### Fase 2: el documento funcional

Sobre el concepto elegido, escribí un documento para discutir ideas, con todo el detalle funcional necesario. No incluyas nada técnico, de UX ni de arquitectura: ni pantallas, ni diseño visual, ni tecnologías, ni modelos de datos, ni algoritmos. Lo que surja de eso va al final, en una lista de "para más adelante", sin resolverlo.

Una estructura posible, que podés cambiar si el concepto pide otra:
- El problema y la tesis.
- Qué hace sano a un vínculo y qué hace la solución con cada pilar, con la evidencia (citá la fuente y qué tan sólida es, sin inventar datos).
- Cómo sabe cómo está cada vínculo preguntando lo mínimo, y cuántas preguntas por semana le hace a la persona.
- Las funciones: qué hace cada una, cuándo aparece, qué pide, qué devuelve y con qué reglas.
- Casos de punta a punta, contados como historias: después de un encuentro; un conflicto o un distanciamiento largo; la revisión de la red cada tanto; invitar al otro a sumar su mirada.
- Alcance de la primera versión, las hipótesis más riesgosas y el experimento más barato para validar cada una antes de construir.
- Cómo sabemos que funciona en la vida real.
- Privacidad, ética y riesgos de mal uso (vigilar a la pareja, rumiación, sesgo hacia los días malos), en términos de quién ve qué.
- Un modelo de negocio sin publicidad ni venta de datos, que no premie la dependencia.
- Entre 5 y 7 preguntas duras para desafiar el documento, respondidas con tu mejor argumento, marcando cuáles quedan abiertas.
- Un resumen de una página: la primera versión mínima y qué hay que validar antes.

### Antes de entregar

Hacé una crítica dura de tu propio documento, como si fueras un inversor escéptico y un psicólogo exigente. Mejorá lo que no aguante la crítica. Si algo quedó en "normal", volvé a pensarlo.

## Formato
- En español rioplatense, claro y concreto, sin jerga.
- Marcá qué es evidencia, qué es supuesto y qué es una propuesta para discutir.
- Si una idea de partida o una directiva de este pedido te parece equivocada, decilo y proponé algo mejor.
```
