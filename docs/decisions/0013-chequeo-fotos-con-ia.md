# 0013 — Chequeo de fotos con IA (excepción a "la IA no recibe datos personales")

- **Estado**: aceptada (German Villamarin, 2026-10-15).

## Contexto

Con fotos en Descubrir (spec A11) hace falta frenar desnudos, violencia, fotos de menores y fotos que no son de una persona en la principal. No hay equipo para revisar a mano. La regla del proyecto es que la IA nunca recibe datos personales (spec X1), y una foto de la cara lo es.

## Decisión

- Cada foto se chequea al subirla con el mismo modelo que ya usamos por OpenRouter (Gemini Flash-Lite, multimodal). Costo de referencia: menos de USD 1 cada 10.000 fotos.
- **Excepción acotada** a la regla de X1: se manda **solo la imagen**, sin nombre, id ni ningún otro dato, y el pedido le exige a OpenRouter proveedores que no guarden ni usen los datos (`provider.data_collection = "deny"`).
- La IA solo responde si la foto es apta, el motivo y si se ve una persona. No describe ni guarda nada.
- Si la IA no responde o no hay key, la foto se acepta y queda "sin revisar" (no se bloquea a nadie por una caída).
- El modelo se puede cambiar con `OPENROUTER_MODERATION_MODEL` (por defecto el mismo `OPENROUTER_MODEL`).

## Consecuencias

- La política de privacidad tiene que decir que las fotos se chequean automáticamente con un proveedor externo (pendiente para antes de abrir a usuarios reales).
- Las fotos "sin revisar" necesitan una revisión manual cuando haya reportes (fuera de alcance de A11).
