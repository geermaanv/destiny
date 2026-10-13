# X2-hiperpersonalizacion — v1: estilo de redacción según la carta

- **Estado**: v1 implemented (falta el ok de Pablo al verlo en la app) · v2 (tema visual) implemented · v3 implemented
- **Módulo**: X2 (transversal)
- **Owner de decisión de producto**: German Villamarin (por ahora). El **mapeo carta → estilo** es parte del modelo: Pablo es la última palabra (ADR 0011) y lo ajusta en la configuración.
- **Aprobada para implementación por**: German Villamarin, 2026-10-13
- **Relacionado**: X1 (redacción con IA), B4 v2 ("Tu día"), roadmap "Hiperpersonalización" en `BACKLOG.md`.

## Problema

Destiny le habla igual a todos. Pero sabe cómo es cada persona: su carta dice cómo procesa la información, cuánta contención necesita y qué formato le sirve. La idea es usar ese conocimiento para **hablarle a cada uno a su manera** (ej. a German, directo y práctico).

## Decisiones

- **Los estilos salen de la astrología**, cada dimensión de un punto de la carta (no de 4 cajas por signo solar).
- Todo el mapeo vive en `apps/api/app/personalization/config/estilos_v1.json` (parametrizable).
- La persona **puede elegir otro registro** en Mi perfil ("Cómo te hablamos") o volver a "Que lo decida mi carta". Siempre se le explica **por qué** se le sugiere su estilo (es autoconocimiento, pilar Explain).
- v1 personaliza **textos**, no lo visual (eso es v2).

## El modelo

| Dimensión | Qué la define | Valores |
|---|---|---|
| **Registro** (cómo procesás la información) | Elemento de **Mercurio** | fuego → *directo* (al grano, motivador) · tierra → *práctico* (concreto, accionable) · aire → *analítico* (ideas, el porqué, datos) · agua → *intuitivo* (emocional, con imágenes) |
| **Tono** (cuánta contención) | Elemento de la **Luna** | agua o tierra → *contenedor* · fuego o aire → *liviano* |
| **Formato** (qué te sirve) | **Modalidad dominante** (Sol y Luna ×3, Ascendente ×2, Mercurio, Venus y Marte ×1; empate: la de Mercurio) | cardinal → *acciones* · fija → *profundidad* · mutable → *opciones* |

Ejemplo (German): Mercurio en Sagitario → directo; Luna en Cáncer → contenedor; modalidad empatada cardinal/fija → la de Mercurio (mutable) → opciones. Explicación: "Te hablamos directo porque tu Mercurio está en Sagitario (fuego)."

## Dónde se aplica (v1)

- **Explicaciones de Descubrir** (las redacta la IA, spec X1): el prompt suma las instrucciones de registro, tono y formato de quien la lee. La cache distingue por estilo.
- **"Tu día"** (spec B4 v2): la biblioteca pasa a tener un texto por **registro** (4 × 6 tránsitos × 12 signos lunares = 288), generados una vez con la IA y revisables por Pablo. Si falta el texto del registro, se usa el de la v1.
- No se aplica al rompehielos (es un mensaje compartido por las dos personas).

## Contrato de datos / API

```
GET /profiles/{id}/style -> { registro, tono, formato, source: "carta" | "elegido", por_que: "...", registro_carta }
PUT /profiles/{id}/style { "registro": "directo" | "practico" | "analitico" | "intuitivo" | null }   (null = que decida la carta)
```

Modelo: `Profile.style_registro` (nullable; la elección manual).

## UX

Mi perfil → tarjeta **"Cómo te hablamos"**: el estilo actual en palabras ("Directo, contenedor, con opciones"), el porqué astrológico, y para elegir otro registro (4 opciones + "Que lo decida mi carta").

## Casos de prueba (`apps/api/tests/test_x2_hiperpersonalizacion.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Estilo de una persona | Registro según el elemento de su Mercurio, tono según su Luna, formato según la modalidad dominante (empate → Mercurio) |
| 2 | El porqué | Menciona el planeta, el signo y el elemento |
| 3 | Elegir otro registro y volver a "que decida la carta" | `source` pasa a "elegido" y vuelve a "carta" |
| 4 | Registro inválido / estilo de otra persona | 422 / 403 (401 sin sesión) |
| 5 | Cambiar el mapeo en la configuración | Cambia el estilo sin tocar código |
| 6 | Explicación con IA | El prompt incluye las instrucciones del estilo de quien la lee |
| 7 | Cambiar de registro | La explicación se vuelve a redactar (la cache distingue estilo) |
| 8 | "Tu día" | Devuelve el texto del registro de la persona |
| 9 | Biblioteca de "Tu día" | 4 registros × 6 tránsitos × 12 signos, completa |

## v2 — Tema visual (aprobada por German, 2026-10-13: "¿podemos cambiar colores además de la forma de hablar?")

**Modelo** (whitepaper §3.2): el tema sale del **elemento predominante** de la carta, `P(e) = Σ wᵢ·[elemento(i) = e] / Σ wᵢ`, con pesos configurables (v2: Sol 3, Luna 3, Ascendente 2, Mercurio 1, Venus 1, Marte 1; sin hora exacta no cuenta el Ascendente). Empate → el elemento del Sol.

| Tema | Paleta orientativa (whitepaper) | Lenguaje |
|---|---|---|
| Fuego | rojo profundo, terracota, dorado | expresivo, contraste cálido |
| Tierra | verde bosque, arena, cobre | orgánico, sobrio |
| Aire | azul claro, plata, lavanda | ligero |
| Agua | índigo, océano, violeta | fluido, contemplativo |
| Clásico | los colores del logo (azul noche, coral, dorado) | el de siempre |

- Cada tema define las **tres escalas** que usa toda la app: fondo/neutros, acción principal y acento. Se generan con la **misma luminosidad** que la paleta clásica (solo cambian tono y saturación), así el contraste de textos y botones se mantiene.
- La persona puede **elegir otro tema** (4 elementos o Clásico) o volver al de su carta. Sin sesión se ve el Clásico.
- Colores en la configuración (`estilos_v1.json` → `tema`), servidos por la API: se cambian sin tocar el front.
- Fuera de alcance de v2: modo claro, tipografías, fondo con el cielo de nacimiento, acento por Venus.

**API**: `GET /profiles/{id}/style` suma `tema`, `tema_carta`, `tema_source` ("carta" | "elegido"), `elementos` (porcentaje por elemento) y `paleta` (las 3 escalas del tema). `PUT /profiles/{id}/style` acepta `tema` (`fuego`|`tierra`|`aire`|`agua`|`clasico`|null); solo cambia los campos que se mandan. Modelo: `Profile.style_tema` (nullable).

**UX**: en "Cómo te hablamos" (pasa a llamarse "Tu estilo") se ve el tema, el porqué ("predomina el agua en tu carta: 45 %") y los 5 temas para elegir. El front aplica la paleta a toda la app al iniciar sesión (y la recuerda en el dispositivo para que no parpadee).

### Casos de prueba v2 (`apps/api/tests/test_x2_tema_visual.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 10 | Tema de una persona | Porcentajes por elemento según los pesos de la configuración; tema = el predominante (empate → elemento del Sol) |
| 11 | Sin hora exacta | El Ascendente no cuenta |
| 12 | Elegir otro tema y volver a la carta | `tema_source` pasa a "elegido" y vuelve a "carta"; cambiar el tema no cambia el registro y viceversa |
| 13 | Tema inválido | 422 |
| 14 | Paleta | Es la del tema en la configuración, con las 3 escalas completas |
| 15 | Contraste | Cada tema mantiene la luminosidad de la paleta clásica en cada tono (± 2 %) |
| 16 | Cambiar los pesos en la configuración | Cambia el tema sin tocar código |

## v3 — Acento, modo claro, tipografía y cielo de nacimiento (aprobada por German, 2026-10-13: "seguí con la v3")

- **Acento por Venus**: si el tema lo decide la carta, el color de acento (escala `gold`) es el del elemento de Venus (lo que te atrae y te gusta). Si la persona eligió un tema, el acento es el de ese tema.
- **Modo claro u oscuro** (`modo`, por defecto oscuro). El claro invierte la luminosidad de fondos, textos y acento (el dorado se oscurece más: tiene mucha luminancia) y deja igual los botones; se genera con `scripts/build_theme_palettes.py` (`paleta_claro`). Los controles nativos siguen el modo (`color-scheme`).
- **Contraste WCAG medido** en los 5 temas × 2 modos, con las combinaciones que usa la app: texto principal ≥ 7 (slate-100 sobre slate-950); texto secundario ≥ 4,5 (slate-300 sobre 900, slate-400 sobre 950, violet-400 y gold-300); texto tenue ≥ 3,5 (slate-500); texto blanco en botones ≥ 3 (violet-600, texto grande/negrita).
- **Tipografía de títulos por tema** (la de lectura no cambia, como pide el whitepaper): Fuego Sora, Tierra Lora, Aire Josefin Sans, Agua Cormorant Garamond, Clásico la de siempre.
- **Fondo con el cielo de nacimiento**: una rueda zodiacal muy tenue detrás de la app con los planetas donde estaban al nacer (y el Ascendente si hay hora exacta). Se puede apagar (`fondo`, por defecto prendido). Es estático: no suma movimiento. Va **detrás** del contenido (las tarjetas la tapan, nunca queda sobre el texto), la rueda entra entera en la pantalla (lado más corto) y las estrellas tienen tamaño fijo. Alrededor de la rueda, escrita en círculo, una **leyenda** con el nombre y los datos principales de la carta (fecha, ciudad, Sol, Luna y Ascendente), y esos mismos puntos se **destacan** en la rueda (Sol y Luna más grandes, Ascendente marcado "AC") — pedido de German.

**API**: `GET /profiles/{id}/style` suma `modo`, `acento` (elemento de Venus), `tipografia`, `fondo`, `cielo` (`[{punto, lon}]`) y `cielo_leyenda` (texto: nombre · fecha · ciudad · Sol en … · Luna en … · Asc. en …; sin hora exacta, sin Ascendente). Solo para la propia persona. `PUT` acepta `modo` (`oscuro`|`claro`) y `fondo` (bool). Modelo: `Profile.style_modo`, `Profile.style_fondo` (nullables).

### Casos de prueba v3 (`apps/api/tests/test_x2_v3.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 17 | Acento | Con el tema de la carta, `gold` es el del tema del elemento de Venus; con un tema elegido, el de ese tema |
| 18 | Modo claro | `paleta` pasa a la clara del tema (con el acento de Venus en su versión clara) y vuelve |
| 19 | Contraste | Las combinaciones de arriba cumplen sus mínimos en los 5 temas × 2 modos |
| 20 | Tipografía | Es la del tema actual |
| 21 | Cielo | Los puntos y longitudes son los de la carta; sin hora exacta no hay Ascendente; `fondo` se puede apagar y prender |
| 22 | Modo inválido | 422 |
| 23 | Leyenda del cielo | Nombre, fecha, ciudad y los signos de Sol, Luna y Ascendente de la carta; sin hora exacta no menciona el Ascendente |

## Fuera de alcance (v4 en adelante)

Aprendizaje por uso (👍/👎), animaciones del cielo y reducir movimiento (hoy no hay animaciones).
