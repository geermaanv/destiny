# A12-privacidad-y-orden-del-test — Aviso de privacidad aceptado, test ordenado por lo que buscás

- **Estado**: implemented
- **Módulo**: A (registro) y A6 (test de personalidad)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 — reunión de check con Pablo (`docs/reuniones/2026-10-20-check-pablo.html`), tanda 2: aviso "como una aceptación de términos" al registrarse y al empezar el test; grupos del test según lo que busca la persona sin preguntarle nada nuevo; Atracción menos intimidante (al final, pantalla de entrada, "Responder más tarde").

## Problema

El usuario tiene que saber sin dudas cómo se usan sus datos, sobre todo las respuestas íntimas del test. Y el test arranca siempre por Atracción, que intimida a quien busca amistad o trabajo.

## Puntos abiertos

Ninguno que bloquee. El título "Química y atracción" para el grupo de Atracción espera el ok de Pablo (texto de su test): queda el actual.

## Requisitos funcionales

### Aviso de privacidad (versión `privacidad_v1`)
- **Al registrarse** (primer paso, datos de nacimiento), antes de continuar: "Cómo cuidamos tus datos" con una casilla obligatoria **"Leí y acepto cómo Destiny usa mis datos"**:
  - Tu fecha, hora y lugar de nacimiento se usan solo para calcular tu carta. Nadie más los ve.
  - Las demás personas ven tu nombre, tus fotos, tu signo y la compatibilidad con ellas; nunca tus datos de nacimiento ni tu teléfono.
  - Para redactar tus lecturas y responder en Indagar usamos un servicio de IA externo, sin tu nombre ni datos que te identifiquen. Las fotos que subís se revisan automáticamente con ese servicio.
- **Al empezar el test**, una pantalla antes de la primera pregunta con **"Entiendo, empezar"**: "Tus respuestas son privadas: son solo para vos y para mejorar las coincidencias. Nunca se muestran a nadie: los demás solo ven el resultado de la compatibilidad. Para responderte en Indagar usamos algunas respuestas (nunca las de atracción), sin datos que te identifiquen."
- Se guarda cuándo y qué versión aceptó cada uno. Sin aceptar: no se termina el registro (`POST /sessions/start` → 409) ni se guardan respuestas del test (409).

### Orden del test
- "¿Qué buscás?" de Círculo se guarda en el perfil (`looking_for`) cada vez que se cambia.
- Los 4 grupos se ordenan por el peso de Pablo para ese vínculo (de mayor a menor); a igual peso, el orden base es Emoción, Comunicación, Compromiso, Atracción. Sin dato, el orden base (Atracción al final).
  - Pareja: Emoción · Comunicación · Compromiso · Atracción
  - Casual: Atracción · Comunicación · Emoción · Compromiso
  - Amistad: Comunicación · Emoción · Compromiso · Atracción
  - Trabajo: Comunicación · Compromiso · Emoción · Atracción

### Atracción menos intimidante (web)
- Antes del grupo de Atracción, si todavía no tiene respuestas: pantalla de entrada "Las próximas preguntas son sobre atracción. Son privadas, nadie las ve, y solo pesan si buscás pareja o algo casual."
- Si no busca pareja ni casual: botón **"Responder más tarde"** (sigue con el resto o termina).
- En Círculo, si elige pareja o casual y le faltan preguntas de Atracción: aviso "Completá las preguntas de atracción para tu compatibilidad de pareja →".

## Contrato de datos / API

```
POST /profiles/{id}/privacy {"version": "privacidad_v1", "contexto": "registro" | "test"} → ProfileOut
POST /profiles/{id}/looking-for {"looking_for": "pareja" | "amistad" | "laboral" | "ocasional"} → ProfileOut
GET  /profiles/{id}/personality → suma "axis_order": ["E2","E3","E4","E1"] y "privacy_accepted": bool
```

`Profile`: `privacy_version`, `privacy_accepted_at`, `test_privacy_version`, `test_privacy_accepted_at`, `looking_for`. `ProfileOut` devuelve `privacy_version`, `test_privacy_version` y `looking_for`.

## Casos de prueba (`apps/api/tests/test_a12_privacidad_y_orden_del_test.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Aceptar el aviso del registro | Queda la versión y la fecha en el perfil |
| 2 | Terminar el registro sin aceptar | `POST /sessions/start` → 409 |
| 3 | Test sin aceptar su aviso | Guardar respuestas → 409; después de aceptar, 200; `privacy_accepted` lo refleja |
| 4 | Orden según lo que busca | Pareja, casual, amistad, trabajo y sin dato dan los órdenes de arriba |
| 5 | Validaciones | `looking_for` o `contexto` inválidos → 422 |

## Criterios de aceptación

- [x] Los 5 casos pasan.
- [x] Casilla obligatoria en el registro, pantalla de entrada del test, pantalla de Atracción con "Responder más tarde" y aviso en Círculo.

## Fuera de alcance

Política de privacidad completa y términos legales (antes de abrir a usuarios reales), borrar la cuenta, cambiar el título del grupo de Atracción (espera a Pablo).
