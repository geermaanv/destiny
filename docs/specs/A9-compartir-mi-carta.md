# A9-compartir-mi-carta — Compartir mi carta con un link

- **Estado**: implemented
- **Módulo**: A (autoconocimiento) + crecimiento
- **Aprobada para implementación por**: German Villamarin, 2026-10-13 ("debería ser simple compartir, hagamos nosotros el filtro de datos y todo listo para compartir").
- **Origen**: análisis de competencia (NeoHumanCode vende informes en PDF). German prefirió compartir online en vez de PDF.

## Problema

Mi carta le da valor a la persona, pero no sale de la app. Un link compartible hace crecer Destiny (quien lo abre puede descubrir su propia carta), se ve bien en WhatsApp, está siempre actualizado y se puede desactivar. Tiene que ser **un solo toque**: Destiny decide qué datos se muestran.

## Comportamiento

- En **Mi carta**, el link **"Compartir →"** va arriba a la derecha, junto al título (German: compartir es sobre toda la carta), con la aclaración de qué se comparte debajo: crea (o reutiliza) el link de la persona y abre el menú de compartir del celular (o WhatsApp en la compu) con el mensaje: "¿Por qué con algunas personas fluye y con otras no? Mirá mi carta en Destiny y descubrí la tuya: {link}".
- Un solo link activo por persona, imposible de adivinar (`/c/{token}`). Debajo: "Se vio N veces · Dejar de compartir" (o, si no se compartió, qué se comparte y qué no). Al dejar de compartir, el link deja de funcionar; si vuelve a compartir, se crea uno nuevo.
- **Página pública** `/c/{token}`, con los colores, la tipografía y el fondo de la persona: "La carta de {nombre}", sus signos (☉ ☽ AC), la rueda, las síntesis de las 4 dimensiones y al final el gancho con "Descubrí tu carta gratis" (lleva a la entrada de Destiny).
- **Vista previa en WhatsApp**: título "La carta de {nombre} en Destiny", descripción con los signos y el gancho.

## Qué se muestra y qué no (lo decide Destiny)

- **Sí**: nombre o apodo (si no tiene, "Alguien"), signo del Sol, la Luna y el Ascendente (si hay hora exacta), la rueda con cada planeta **ubicado en el medio de su signo** (no en el grado exacto), las síntesis de las 4 dimensiones, su paleta, tipografía y fondo.
- **No**: fecha, hora y lugar de nacimiento, grados exactos de los planetas (con ellos se podría deducir la fecha), casas y aspectos, teléfono, foto, barrio, intereses, bio, respuestas del test, conexiones.
- Las síntesis son las mismas de Mi carta (cache); si no estaban, se generan igual que en Mi carta.

## API

- `POST /profiles/{id}/share` (solo la propia persona) → `{token, vistas}`; si ya hay uno activo lo devuelve.
- `GET /profiles/{id}/share` → `{activo, token?, vistas}`.
- `DELETE /profiles/{id}/share` → desactiva.
- `GET /public/carta/{token}` (sin sesión) → `{nombre, signos: {sol, luna, asc?}, cielo, dimensiones: [{clave, nombre, pregunta, sintesis}], paleta, tipografia, fondo, elementos}`; suma una vista. Link inexistente o desactivado → 404.
- Modelo: tabla `share_links` (token, profile_id, created_at, revoked_at, views).

## Fuera de alcance v1

Conectar automáticamente a quien se registra desde el link con quien lo compartió (hoy eso lo hace la invitación C8), informe de vínculo compartible (necesita el consentimiento de las dos personas), imagen de vista previa generada, descarga en PDF.

## Casos de prueba (`apps/api/tests/test_a9_compartir_carta.py`)

1. Crear el link: solo la propia persona (otra → 403, sin sesión → 401); la segunda vez devuelve el mismo token.
2. La página pública trae nombre, signos, las 4 dimensiones con síntesis, paleta, tipografía y fondo.
3. La página pública **no** trae fecha, hora ni lugar de nacimiento, teléfono, foto ni grados exactos: cada planeta queda en su signo correcto pero no en su longitud real.
4. Sin hora exacta no hay Ascendente ni en los signos ni en la rueda.
5. Cada visita suma una vista y la persona la ve en `GET /profiles/{id}/share`.
6. Dejar de compartir: el link da 404; compartir de nuevo crea un token distinto.
7. Token inexistente → 404.
8. Sin key de IA, la síntesis es la plantilla (no llama a la red); con IA, si la síntesis ya estaba en la cache no se vuelve a pedir.
