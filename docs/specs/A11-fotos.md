# A11-fotos — Fotos del perfil con chequeo automático

- **Estado**: implemented
- **Módulo**: A4 (perfil liviano) y B5 (Descubrir)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-15 ("hasta 4 fotos, no en el onboarding, agregar en la sección Descubrir y en el perfil"; chequeo con Gemini; boceto de las 3 pantallas aprobado). Pedido de Pablo: "en el apartado de relacionamiento tenemos que mostrar como mínimo una foto de la persona".

## Problema

Para decidir con quién conectar hace falta ver a la persona. Hoy hay una sola foto opcional y casi nadie la sube, así que Descubrir muestra avatares. Pero pedir fotos en el registro frena a quien viene por el autoconocimiento.

## Puntos abiertos

Ninguno. Quedan fuera de alcance con default: reportar fotos, almacenamiento en la nube (hoy disco, se resuelve con el hosting), fotos por elemento, qué compartir con cada conexión (C10).

## Requisitos funcionales

- **Hasta 4 fotos** por perfil (`fotos.max` en la configuración). La primera es la **principal**: la que se ve en la tarjeta de Descubrir y como avatar en chats y listas.
- **No se piden en el registro**: el paso "Tu perfil" ya no tiene foto (queda el avatar).
- **Se cargan** desde Descubrir (aviso "Subí tu foto para que otros te vean" si no tenés ninguna) y desde Perfil → "Tus fotos".
- **Para aparecer en Descubrir hace falta al menos una foto.** Sin foto se puede usar Descubrir (ver a otros), pero nadie te ve.
- **Todas las fotos se ven antes del match**, en el perfil de la persona dentro de Descubrir.
- Se puede **elegir otra como principal** y **borrar**. No se reordena arrastrando.
- **Chequeo automático al subir** (Gemini por OpenRouter, ADR 0013): rechaza desnudos o contenido sexual, violencia, menores y fotos que no son una foto real (captura de pantalla, meme). La principal además tiene que mostrar una persona. Si se rechaza, no se guarda y se explica el motivo.
- **Si la IA no responde o no está configurada, la foto se acepta** y queda marcada "sin revisar" para revisar a mano después: una caída no bloquea a nadie.
- A la IA se le manda **solo la imagen**, sin nombre ni ningún otro dato, y se le pide al proveedor que no la guarde.
- La web achica la foto antes de subirla (lado mayor 1600 px, JPEG), así las del celular no superan el límite de 5 MB.

## Contrato de datos / API

```
POST   /profiles/{id}/photos              (multipart "photo") → 201 PhotosOut | 409 tope | 413 | 415 | 422 {detail: motivo}
DELETE /profiles/{id}/photos/{photo_id}   → PhotosOut
POST   /profiles/{id}/photos/{photo_id}/principal → PhotosOut | 409 si no se ve una persona
GET    /profiles/{id}/photos              → PhotosOut (solo el dueño)
GET    /photos/{photo_id}                 → la imagen
GET    /profiles/{id}/photo               → la principal (compatibilidad: avatar en chats y listas)

PhotosOut = {"photos": [{"id", "url", "principal": bool}], "max": 4}
```

- Tabla `profile_photos`: `id`, `profile_id`, `path`, `position` (0 = principal), `persona` (bool | null), `moderacion` ("aprobada" | "sin_revisar"), `created_at`.
- `GET /discover` suma por candidato `photos: [url]` (la principal primero). `ProfileOut.has_photo` sigue indicando si hay principal.
- Las fotos que ya existían (`profiles.photo_path`) pasan a ser la principal.
- Configuración: `app/photos/config/fotos_v1.json` (tope, prompt, motivos y textos de rechazo).
- Se reemplazan `POST/DELETE /profiles/{id}/photo` (A4) por los endpoints de arriba.

## UX / Flujo

1. **Descubrir** sin foto: aviso arriba "Subí tu foto para que otros te vean" con "Subir foto →" (lleva a Tus fotos). Tarjetas con la foto principal grande.
2. **Perfil de otra persona** (`/discover/[id]`): fotos para deslizar con puntitos, nombre, edad, signo, barrio, frase, intereses, compatibilidad y Conectar.
3. **Perfil → Tus fotos** (`/perfil/fotos`): 4 lugares; "Principal" marcada; menú ⋯ con "Usar como principal" y "Borrar"; los vacíos dicen "+ Agregar". Si se rechaza: "Esta foto no se puede usar: {motivo}".

## Casos de prueba (`apps/api/tests/test_a11_fotos.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Subir, listar y ver una foto | 201; la primera queda principal; `GET /photos/{id}` la devuelve |
| 2 | Tope de 4 | La quinta → 409 |
| 3 | Formato y tamaño | Texto → 415; más de 5 MB → 413 |
| 4 | Solo el dueño sube, borra y lista | Otro navegador → 401 |
| 5 | Elegir otra como principal | Pasa a primera; `/profiles/{id}/photo` devuelve la nueva |
| 6 | Borrar la principal | La siguiente pasa a principal; sin fotos, `has_photo` es false |
| 7 | La IA rechaza (desnudo) | 422 con el motivo; no se guarda |
| 8 | Principal sin persona | Primera foto sin persona → 422; como extra se acepta; hacerla principal → 409 |
| 9 | La IA falla o no hay key | Se acepta como "sin revisar" |
| 10 | A la IA va solo la imagen | El pedido no incluye nombre ni datos del perfil, y pide no guardar datos |
| 11 | Descubrir exige foto | Sin foto no aparece; con foto aparece con `photos` |
| 12 | Quien no tiene foto igual ve Descubrir | 200 |

## Criterios de aceptación

- [x] Los 12 casos pasan.
- [x] El registro ya no pide foto.
- [x] Descubrir, perfil de otra persona y Tus fotos funcionan en el celular.

## Fuera de alcance

Reportar fotos y revisión manual (por ahora quedan marcadas "sin revisar"), almacenamiento en la nube, reordenar arrastrando, fotos por elemento, qué compartir con cada conexión (C10), chequear que la foto sea de la persona (selfie de A3 v2).
