# A4-perfil-liviano — Perfil liviano

- **Estado**: implemented
- **Módulo**: A4 (nuevo, extiende el Módulo A de `../ALCANCE_MVP.md`)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-07

## Problema

Hoy un perfil es solo una carta natal: en Descubrir se ve "Por descubrir · 60%" sin nombre ni cara. Hace falta un perfil mínimo que identifique a la persona, **sin convertir Destiny en una app de citas**: el perfil no dice qué tipo de relación busca cada uno (eso se elige en Descubrir, ver `B5`).

## Decisiones tomadas (German, 2026-10-07)

- **Perfil liviano**: pocos datos, rápido de completar.
- **El perfil no restringe el tipo de relación** (pareja, amistad, trabajo, socio…). No se pide género ni "a quién buscás" en el perfil. El contexto se elige al descubrir y queda abierto a nuevos tipos (`B5`).

- **Foto opcional**; si no sube foto, elige un **avatar** de una lista (por defecto, el del signo).
- **Barrio opcional** (texto libre corto).

## Puntos abiertos

Ninguno.

## Requisitos funcionales

Datos del perfil:

| Dato | Obligatorio | Notas |
|---|---|---|
| Nombre o apodo | Sí | Lo que ven los demás. |
| Foto | No | Una sola foto en v1 (JPG/PNG/WebP, hasta 5 MB). |
| Avatar | Automático / elegible | Si no hay foto se muestra el avatar elegido; por defecto, el del signo. |
| Barrio | No | Texto libre corto (ej. "Palermo"). |
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
  "bio": "..." | null,
  "neighborhood": "Palermo" | null,
  "avatar": "luna" | null
}
POST /profiles/{id}/photo   (multipart)
GET  /profiles/{id}/photo
```

`GET /discover` suma por candidato: `display_name`, `age`, `sun_sign`, `photo_url`, `avatar`, `energy_period`, `interests`, `bio`, `neighborhood`.

## UX / Flujo

1. Pantalla "Tu perfil" en el onboarding, después de datos natales: nombre (obligatorio) y el resto opcional, con "Completar después".
2. En Descubrir, cada tarjeta muestra nombre, edad, signo, foto/avatar y la etiqueta de resonancia.
3. "Mi perfil" (`/perfil`) desde la barra de navegación, con el mismo formulario.

## Implementación (2026-10-07)

- API: `POST /profiles/{id}/basic-info`, `POST`/`DELETE`/`GET /profiles/{id}/photo` (JPG/PNG/WebP, 5 MB, guardadas en `apps/api/uploads/`, fuera del repo). `app/public_profile.py` arma los datos públicos (edad y signo calculados). `GET /profiles/{id}` suma `sun_sign` y `has_photo`.
- Web: `components/ProfileForm.tsx` (onboarding `/onboarding/perfil` y `/perfil`), `components/ProfileAvatar.tsx`, etiquetas en `lib/profile.ts`. Onboarding: datos natales → **perfil** → ritmo → verificación.
- Intereses (12, máx. 5): música, deporte, arte, tecnología, viajes, espiritualidad, lectura, cine, naturaleza, cocina, emprendimientos, juegos. Avatares: signo (default), luna, sol, estrella, planeta, fuego, ola, hoja, mariposa, rayo.

## Casos de prueba

Tests automáticos en `apps/api/tests/test_a4_perfil_liviano.py` (correr: `cd apps/api && .venv/bin/pytest`).

| # | Caso | Test |
|---|---|---|
| 1 | Perfil completo se guarda | `test_perfil_completo_se_guarda` |
| 2 | Nombre es obligatorio | `test_nombre_es_obligatorio` |
| 3 | Intereses fuera de la lista o más de 5 se rechazan | `test_intereses_fuera_de_la_lista_o_mas_de_5_se_rechazan` |
| 4 | Frase hasta 140 caracteres | `test_frase_hasta_140_caracteres` |
| 5 | Foto subir ver y borrar | `test_foto_subir_ver_y_borrar` |
| 6 | Foto que no es imagen se rechaza | `test_foto_que_no_es_imagen_se_rechaza` |
| 7 | Edad y signo se calculan solos | `test_edad_y_signo_se_calculan_solos` |
| 8 | Perfiles sin nombre no aparecen en Descubrir | `test_perfiles_sin_nombre_no_aparecen_en_descubrir` |
| 9 | Géminis en castellano | `test_geminis_en_castellano` |

## Criterios de aceptación

- [x] Los perfiles sin nombre (incompletos) no aparecen en Descubrir ni cuentan en "En tu frecuencia".
- [x] No se puede avanzar del paso sin nombre/apodo.
- [x] Descubrir muestra nombre, edad y signo de cada candidato.
- [x] Ningún endpoint que ven otros usuarios expone teléfono ni datos natales exactos.
- [x] El perfil se puede editar después del onboarding.

## Fuera de alcance

- Tipo de relación buscada en el perfil (se elige en Descubrir, `B5`).
- Género / orientación.
- Varias fotos, verificación de que la foto coincide con la persona (eso va con la selfie de A3 v2).
- Ubicación geográfica precisa (el barrio es texto libre, sin geocodificar).
