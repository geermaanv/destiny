# App de vínculos: prompts de diseño

> Para pedirle a Claude el diseño de la app de vínculos (`docs/APP_DE_VINCULOS.md`). Son **dos prompts separados**: primero la fase 1 (conceptos); se discuten y se elige; recién ahí se escribe y se corre la fase 2 (documento funcional) sobre el concepto elegido.
>
> v2 (2026-10-24): combina la versión anterior con la crítica de un prompt de Gemini (fases estrictamente separadas, foco en el núcleo, arquetipos concretos, datos propios con permiso sí y contenido ajeno no).

## Fase 1: destilar y elegir un concepto

```markdown
Actuá como una dupla: un Principal Product Designer obsesionado con el diseño por sustracción (quitar hasta que quede lo esencial, en la escuela de Dieter Rams y Don Norman) y un psicólogo clínico especialista en vínculos en la adultez media.

## El desafío

Encontrar la forma de que personas de 40 a 60 años en Argentina cuiden y mejoren sus vínculos reales (amistad y familia primero, siempre de a dos) con un esfuerzo casi nulo. Buscamos algo que parezca evidente una vez visto, aunque haya requerido descartar docenas de alternativas. No una app más con pantallas y menús.

"Increíble" significa: casi no pide nada, cambia algo real afuera de la pantalla (un mensaje, una llamada, un encuentro), tiene momentos que la gente cuenta sin que se lo pidan y se siente humano.

## El núcleo

En esta fase no busques cubrirlo todo. Buscá lo que resuelve la mayor parte del valor:
- **Estar atento:** darse cuenta a tiempo de que un vínculo importante se está enfriando.
- **Reciprocidad:** notar si siempre sos vos el que busca, o el que no busca.
- **Facilitar el reencuentro:** con el tiempo, lo que alejó deja de importar, y muchas veces alcanza con un "Hola". El problema es dar el primer paso.

Lo demás (reparar después de un conflicto, la energía de cada encuentro, el crecimiento, la diversidad de la red) es secundario en esta fase: sumalo solo si sale naturalmente del núcleo.

## Reglas que no se negocian

- **Herramienta, no oráculo:** nunca diagnostica ("este amigo te drena") ni puntúa a nadie. Devuelve preguntas o contrastes, y la persona puede decir "esto no me representa".
- **Nunca la única voz:** manda hacia afuera (la persona, alguien de confianza, un profesional). Ante señales de violencia o control, deriva a recursos (en Argentina, Línea 144).
- **No automatiza el contacto:** la app ayuda a estar atento y puede sugerir ideas o planes, pero el que escribe, llama o va es la persona.
- **Sirve aunque el otro no participe:** la herramienta es tuya. Si el otro se suma, con su consentimiento, mejor.
- **Esfuerzo mínimo:** nada difícil de configurar, nada que dé trabajo y valor desde el primer día. No puede depender de que la persona cargue todo a mano ni de que conteste muchas preguntas; además, lo que uno contesta sobre sí mismo puede estar sesgado.
- **Anti-dependencia:** nada de rachas, puntos, métricas de vanidad ni avisos que generen culpa. El éxito es que la persona deje la pantalla y genere un contacto real.
- **Privacidad:**
  - Se pueden usar **datos propios con permiso explícito** y explicando para qué: el calendario, los contactos y favoritos, el registro de llamadas en Android.
  - **Nunca** se lee el contenido de mensajes ni chats, ni se sigue la ubicación de nadie.
  - Exportar chats queda descartado: es demasiada fricción.

## Lo que pide quien impulsa la idea (necesidades, no soluciones)

- **Calidad antes que cantidad**, pero también **diversidad**: vincularse con gente parecida y muy distinta, y ampliar la red además de cuidarla.
- **Las etapas de la vida cambian los vínculos sin que uno lo decida** (cambio de trabajo, hijos que se van, jubilación), y no siempre para bien. Hoy nadie acompaña ese momento.
- **Ver de un vistazo cómo están tus cercanías.** Si eso necesita una forma gráfica (un mapa, un mapa de calor) o se resuelve de otra manera, decidilo vos y justificalo. Si hay algo visual, que muestre cercanías según tu vida y tu percepción, no un puntaje de las personas.
- **Tono de coach.** El canal (una app, WhatsApp, otra cosa) está abierto.
- **Ambición:** que la gente diga "me ayudó a mejorar mis vínculos".

## Contexto

Ya existen y no alcanzan:
- **Solo pareja:** Paired, Gottman Connect, Relish, Wefeel.
- **Compatibilidad astrológica con tono de oráculo:** Co-Star, The Pattern.
- **Conocer gente nueva:** Timeleft, Bumble BFF.
- **Agendas o mapas de contactos que se quedan en "acordate de escribirle":** Dex, Clay, Bond, Orbits.

## Tareas

1. **Descartar lo obvio.** Listá las 5 soluciones que propondría cualquier agencia (por ejemplo: una agenda de contactos con recordatorios programados, termómetros de ánimo después de cada llamada, encuestas periódicas, un diario de texto, una red interactiva para administrar). Explicá por qué fracasan con personas de 40 a 60 años con poco tiempo mental. Quedan prohibidas en su forma obvia: alguna solo puede volver si la transformás tanto que deja de ser esa solución, y explicás por qué.

2. **Primeros principios.**
   - Antes de los celulares, ¿cuál era la unidad mínima de atención que mantenía vivo un vínculo de décadas?
   - ¿Cómo se da cuenta una persona intuitiva de que un vínculo se está enfriando, sin llevar registros?
   - ¿Cómo se puede saber algo de un vínculo sin pedirle a nadie que complete nada?

3. **Cuatro arquetipos reales de Argentina, de 40 a 60 años:**
   - Alguien abrumado por el trabajo que posterga a sus amigos de toda la vida.
   - Alguien que tuvo un distanciamiento familiar por algo chico y no sabe cómo romper el hielo.
   - Alguien que siente que siempre es quien inicia el contacto.
   - Alguien a quien una etapa (los hijos que se van, un cambio de trabajo, la jubilación) le cambió la red sin que lo eligiera.

4. **Cinco conceptos radicales y contrastantes entre sí, no variaciones de uno.** Al menos uno no debe ser una app tradicional (por ejemplo: un bot conversacional mínimo, un widget pasivo, algo que viva en el calendario, audios asíncronos, algo que hoy no existe). Para cada uno:
   - La tesis en una frase.
   - La interacción central (idealmente un solo gesto).
   - De dónde saca lo que sabe, preguntando lo mínimo.
   - El momento revelador.
   - Cómo le sirve a cada arquetipo.
   - El riesgo que haría que la gente lo abandone.

5. **Podar.** Evaluá los cinco con un filtro despiadado: ¿cuál resuelve la mayor parte del núcleo con el menor tiempo de pantalla por semana (apuntá a menos de un minuto)? Además: ¿respeta las reglas, dan ganas de contarlo y parece evidente una vez visto? Elegí un ganador o la fusión mínima necesaria, y fundamentá el descarte de los demás.

Formato: en español rioplatense, claro y concreto. Marcá qué es evidencia, qué es supuesto y qué es propuesta. Si una regla o una necesidad de este pedido te parece equivocada, decilo y proponé algo mejor.

**Frená acá.** No escribas el documento funcional: primero vamos a discutir y desafiar los conceptos.
```

## Fase 2: documento funcional

Se escribe después de discutir la fase 1, sobre el concepto elegido. Ideas a conservar de la versión anterior:

- Solo funcional: nada técnico, de UX ni de arquitectura. Lo que surja de eso va a una lista de "para más adelante".
- La mecánica central primero, y todo lo demás justificado contra ella.
- Los pilares (reciprocidad, seguridad, reparación, energía, cercanía y ritmo, crecimiento, ecología de la red) con la evidencia: la fuente, qué tan sólida es y sin inventar datos.
- Cómo sabe cómo está cada vínculo preguntando lo mínimo, y cuántas preguntas por semana le hace a la persona.
- Casos contados como historias: después de un encuentro; un distanciamiento largo; la revisión de la red cada tanto; invitar al otro.
- Alcance de la primera versión, las hipótesis más riesgosas y el experimento más barato para cada una.
- Cómo sabemos que funciona en la vida real, y cómo se aparta el software del camino.
- Privacidad, ética y riesgos de mal uso, en términos de quién ve qué.
- Un modelo de negocio sin publicidad ni venta de datos, que no premie la dependencia.
- Los riesgos de la simplicidad y entre 5 y 7 preguntas duras respondidas.
- Una crítica propia (como un inversor escéptico y un psicólogo exigente) antes de entregar.
- Un resumen de una página.
