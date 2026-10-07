# A4-perfil-liviano — Perfil liviano

- **Estado**: draft
- **Módulo**: A4 (nuevo, extiende el Módulo A de `../ALCANCE_MVP.md`)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: —

## Problema

Hoy un perfil es solo una carta natal: en Descubrir se ve "Por descubrir · 60%" sin nombre ni cara. Hace falta un perfil mínimo que identifique a la persona, **sin convertir Destiny en una app de citas**: el perfil no dice qué tipo de relación busca cada uno (eso se elige en Descubrir, ver `B5`).

## Decisiones tomadas (German, 2026-10-07)

- **Perfil liviano**: pocos datos, rápido de completar.
- **El perfil no restringe el tipo de relación** (pareja, amistad, trabajo, socio…). No se pide género ni "a quién buscás" en el perfil. El contexto se elige al descubrir y queda abierto a nuevos tipos (`B5`).

## Puntos abiertos

- [ ] ¿Foto obligatoria u opcional? Propuesta: **opcional** en v1 (menos fricción y menos moderación), con un avatar por signo si no hay foto.
- [ ] ¿Ciudad/barrio actual en el perfil? Propuesta: **no** en v1 (el "N en tu frecuencia" geográfico es otra iteración); se puede sumar sin cambiar el resto.

## Requisitos funcionales

Datos del perfil:

| Dato | Obligatorio | Notas |
|---|---|---|
| Nombre o apodo | Sí | Lo que ven los demás. |
| Foto | A definir (propuesta: no) | Una sola foto en v1. |
| Edad | Automático | Sale de la fecha de nacimiento (A1); no se edita aparte. |
| Signo solar | Automático | Sale de la carta natal. |
| Momento del día con más energía | No | Madrugada / mañana / tarde / noche. Dato de color y señal futura de matching (idea de German). |
| Intereses | No | Chips de una lista corta (ej. música, deporte, arte, tecnología, viajes, espiritualidad…), máximo 5. |
| Frase corta | No | "Algo sobre vos", hasta ~140 caracteres. |

- Se completa como un paso más del onboarding (después de datos natales) y se puede editar después desde la app.
- Otros usuarios ven: nombre, foto, edad, signo, energía, intereses y frase. **Nunca** el teléfono ni la fecha/hora/lugar de nacimiento exactos.

## Contrato de datos / API (borrador)

```
POST /profiles/{id}/basic-info
{
  "display_name": "Gerry",
  "energy_period": "manana" | "tarde" | "noche" | "madrugada" | null,
  "interests": ["musica", "viajes"],
  "bio": "..." | null
}
POST /profiles/{id}/photo   (multipart, si se aprueba la foto)
```

`GET /discover` suma por candidato: `display_name`, `age`, `sun_sign`, `photo_url`, `energy_period`, `interests`, `bio`.

## UX / Flujo

1. Pantalla "Tu perfil" en el onboarding, después de datos natales: nombre (obligatorio) y el resto opcional, con "Completar después".
2. En Descubrir, cada tarjeta muestra nombre, edad, signo, foto/avatar y la etiqueta de resonancia.
3. Acceso a "Mi perfil" para editar (ubicación a definir junto con la navegación).

## Criterios de aceptación

- [ ] No se puede avanzar del paso sin nombre/apodo.
- [ ] Descubrir muestra nombre, edad y signo de cada candidato.
- [ ] Ningún endpoint que ven otros usuarios expone teléfono ni datos natales exactos.
- [ ] El perfil se puede editar después del onboarding.

## Fuera de alcance

- Tipo de relación buscada en el perfil (se elige en Descubrir, `B5`).
- Género / orientación.
- Varias fotos, verificación de que la foto coincide con la persona (eso va con la selfie de A3 v2).
- Ubicación geográfica.
