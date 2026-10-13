# X2-hiperpersonalizacion — v1: estilo de redacción según la carta

- **Estado**: approved
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

## Fuera de alcance (v2 en adelante)

Tema visual (paleta, acento, tipografía, fondo con el cielo de nacimiento) y aprendizaje por uso (👍/👎).
