# A8-mi-carta-dimensiones — Mi carta: autoconocimiento por dimensiones

- **Estado**: implemented
- **Módulo**: A (perfil) — primera pieza de "Autoconocimiento primero" (BACKLOG, whitepaper v1 §3.3).
- **Owner de decisión de producto**: German Villamarin; Pablo revisa la matriz de indicadores y los textos (es parte del modelo, ADR 0011).
- **Aprobada para implementación por**: German Villamarin, 2026-10-13 ("avanzar con el 3").

## Problema

Hasta tener una base amplia de usuarios, el matchmaking solo no retiene: cada persona tiene que recibir valor sobre sí misma desde el primer día (estrategia en `VISION.md`). El whitepaper organiza el perfil natal por **áreas de vida**, no por posiciones planetarias, y pide que cada lectura sea trazable a la carta calculada.

## Alcance v1: 4 dimensiones (MVP 1 del whitepaper)

| Dimensión | Pregunta | Indicadores (propuesta; los revisa Pablo) |
|---|---|---|
| Identidad y propósito | ¿Quién soy y qué me mueve? | Sol (signo y casa), Ascendente (signo), aspectos al Sol |
| Amor y vínculos | ¿Cómo amo y me vinculo? | Venus (signo y casa), Descendente (signo), aspectos a Venus |
| Vocación y carrera | ¿Dónde puedo desarrollarme? | Medio Cielo (signo), Saturno (signo y casa), aspectos al MC y a Saturno |
| Seguridad emocional | ¿Qué me da estabilidad? | Luna (signo y casa), Fondo de Cielo (signo), aspectos a la Luna |

Cada dimensión tiene:
1. **Fundamentos trazables**: los indicadores de la persona (ej. "Sol en Escorpio", "Sol en casa 11", "Sol en trígono con Neptuno"), cada uno con su texto.
2. **Síntesis**: un párrafo que integra los fundamentos, en el estilo de la persona (spec X2).
3. **Preguntas de reflexión** (2 o 3 por dimensión, fijas en la configuración).

## Reglas

- **Cálculo**: los indicadores salen de la carta calculada (`chart_for_profile`, la misma del motor A7: casas por signo entero). Descendente = Ascendente + 180°, Fondo de Cielo = Medio Cielo + 180°. Los aspectos natales son los mayores (conjunción, sextil, cuadratura, trígono, oposición), el más exacto dentro del orbe, entre Sol, Luna, Mercurio, Venus, Marte, Júpiter, Saturno, Urano, Neptuno, Plutón, ASC y MC. Orbes en la configuración.
- **Sin hora exacta**: no hay Ascendente, Medio Cielo, Descendente, Fondo de Cielo ni casas. Esos indicadores no se muestran y la dimensión lista qué falta (`faltan_por_hora`), para invitar a cargar la hora. Lo marca "aproximado".
- **Configuración** (`app/natal/config/dimensiones_v1.json`): dimensiones, indicadores, orden, preguntas de reflexión, orbes y significado de cada aspecto, palabra clave de cada planeta. Todo editable sin tocar código.
- **Textos** (`app/content/carta_v1.json`): un texto por indicador × signo (Sol, Ascendente, Venus, Descendente, Medio Cielo, Saturno, Luna, Fondo de Cielo: 96) y por indicador × casa (Sol, Venus, Saturno, Luna: 48). Se generan **una sola vez** con IA (`scripts/generate_carta_texts.py`), quedan `revisado_por_pablo: false` y se editan a mano. Máximo 280 caracteres. Los aspectos usan una frase de plantilla armada desde la configuración.
- **Síntesis con IA** (como X1): la IA recibe solo la dimensión y los textos de los fundamentos (nunca nombre, fecha, lugar ni teléfono), con la guía editorial y las instrucciones del estilo de la persona. Máximo 500 caracteres. Se cachea (`ai_texts`, tipo `carta`) por persona + datos natales + dimensión + estilo + modelo + versión de configuración y textos. Sin key o si falla: plantilla con los dos primeros fundamentos.
- **Privacidad**: solo la propia persona ve su carta (`require_self`).

## API

- `GET /profiles/{id}/natal/dimensions` → `{aproximado, dimensiones: [{clave, nombre, pregunta, fundamentos: [{tipo: "signo"|"casa"|"aspecto", punto, signo?, casa?, otro?, aspecto?, texto}], preguntas, faltan_por_hora}]}`. No llama a la IA (rápido).
- `GET /profiles/{id}/natal/dimensions/{clave}/synthesis` → `{texto, ia: bool}`. Se pide por tarjeta.

## UX

Pantalla **Mi carta** (`/perfil/carta`), con acceso desde Mi perfil: una tarjeta por dimensión con la pregunta, la síntesis (carga aparte), "En qué se basa" desplegable con los fundamentos y las preguntas de reflexión. Si falta la hora: aviso con link a editar los datos de nacimiento.

## Fuera de alcance v1

- Las otras 12 dimensiones del whitepaper (fase 2), guardar respuestas a las preguntas de reflexión (Destiny Mirror), regentes de casas, aspectos menores, cuerpos extra.

## Casos de prueba

En `apps/api/tests/test_a8_mi_carta.py`:

1. Devuelve las 4 dimensiones en el orden de la configuración, con nombre, pregunta y preguntas de reflexión.
2. Identidad trae el Sol en el signo y la casa que da la carta calculada, y el Ascendente en su signo.
3. Los aspectos de cada dimensión son exactamente los que salen de las longitudes de la carta con los orbes de la configuración.
4. Sin hora exacta: no hay Ascendente, MC, Descendente, Fondo de Cielo ni casas; `faltan_por_hora` los nombra y `aproximado` es true.
5. La biblioteca tiene texto para cada indicador × signo y × casa de la configuración, de 280 caracteres o menos, y cada fundamento usa el texto de la biblioteca.
6. Síntesis sin key: plantilla, sin llamar a la red, con texto de los fundamentos; `ia` false.
7. Síntesis con IA: el system prompt incluye las instrucciones del estilo de la persona; lo que se manda no tiene nombre ni fecha de nacimiento; la segunda vez sale de la cache; si cambia el estilo, se vuelve a redactar.
8. Otra persona → 403; sin sesión → 401; dimensión inexistente → 404.
9. Cambiar los indicadores de una dimensión en la configuración cambia los fundamentos sin tocar código.
