# B8-filtros-descubrir — Buscar y filtrar en Descubrir

- **Estado**: implemented
- **Módulo**: B5 (Descubrir)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-15 (a partir del pedido de Pablo: lupa, buscar por compatibilidad, tipo de relación, sistema, compatibilidad mínima, edad y preferencias).

## Problema

Descubrir muestra los 5 de mayor compatibilidad astrológica para un tipo de vínculo y nada más: no se puede buscar a alguien, ni elegir el sistema, ni la edad, y a quien busca pareja le aparecen personas del género que no le interesa.

## Puntos abiertos

Ninguno. Fuera de alcance con default: distancia (no hay ubicación), numerología (no hay modelo), @ usuario y QR (spec C9).

## Requisitos funcionales

- **Lupa**: buscar por nombre. La búsqueda ignora los filtros de compatibilidad, sistema y edad (buscás a alguien puntual), pero respeta las reglas de quién aparece (cuenta activa, foto, género en "pareja"). Hasta 20 resultados.
- **Filtros** (panel "Filtros"):
  - **Qué buscás**: pareja, amistad, trabajo, casual (ya existía).
  - **Según qué sistema**: astrología (por defecto) o test de personalidad. Con "personalidad" solo aparecen quienes completaron el test, y el orden y el porcentaje son los del test. Si quien busca no hizo el test → 409 y la app ofrece hacerlo.
  - **Compatibilidad mínima**: 0, 50, 60, 70 u 80 %, según el sistema elegido.
  - **Edad**: desde/hasta.
  - Los filtros se recuerdan en el navegador.
- **Género y "Mostrame"** (cambia lo que dejaba afuera A4):
  - "Tu género": mujer, hombre, no binario; más un texto libre opcional (ej. "mujer trans").
  - "En Descubrir, mostrame": mujeres, hombres, personas no binarias (selección múltiple; "Todas las personas" = las tres).
  - Las personas no binarias eligen además en qué búsquedas aparecer: de mujeres, de hombres o ambas.
  - **Es mutuo y aplica solo a "pareja"**: A ve a B si B entra en lo que A quiere ver **y** A entra en lo que B quiere ver. En amistad, trabajo y casual se ve a todos.
  - Quien no cargó "Mostrame" ve a todos; quien no cargó su género no aparece en "pareja" para quien sí filtra (no sabemos si encaja).
  - No se pregunta la orientación. Se pide al entrar a Descubrir en "pareja" sin haberlo cargado, no en el registro, y se edita en Editar perfil.
  - El género se muestra en el perfil público **solo si la persona elige mostrarlo**. Nunca va a la IA.
- Sin resultados: "Nadie con estos filtros todavía" con "Ampliar filtros".

## Contrato de datos / API

```
GET /discover?viewer_id&context&sistema=astrologia|personalidad&min_pct=0..100&edad_min&edad_max&q=texto
POST /profiles/{id}/preferences {gender, gender_detail, show_me: [..], appear_in: [..], show_gender} → ProfileOut
```

- `Profile`: `gender` ("mujer" | "hombre" | "no_binario" | null), `gender_detail` (texto ≤ 40), `show_me` (lista), `appear_in` (lista, solo no binario), `show_gender` (bool, por defecto false).
- `ProfileOut` suma esos campos. `public_fields` suma `gender_label` solo si `show_gender`.
- Edad entre 18 y 99; `edad_min` > `edad_max` → 422.
- Cada candidato trae `compatibility_pct` (según el sistema elegido) y `astrology_pct` (siempre la sinastría), para mostrar las dos en el perfil.

## Casos de prueba (`apps/api/tests/test_b8_filtros_descubrir.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Guardar preferencias | Se guardan y vuelven en `/profiles/{id}`; valores inválidos → 422 |
| 2 | "Mostrame" mutuo en pareja | Hombre que busca mujeres ve a mujer que busca hombres; no ve a mujer que busca mujeres |
| 3 | No binario elige dónde aparecer | Aparece para quien busca mujeres si eligió aparecer ahí |
| 4 | Fuera de pareja no filtra género | En amistad se ve a todos |
| 5 | Sin "Mostrame" se ve a todos; sin género no aparece para quien filtra | |
| 6 | Edad | Solo aparecen los de la franja; min > max → 422 |
| 7 | Compatibilidad mínima | Solo los que la superan |
| 8 | Sistema personalidad | Solo quienes hicieron el test, con su porcentaje; sin test propio → 409 |
| 9 | Búsqueda por nombre | Encuentra por parte del nombre, sin importar mayúsculas ni acentos, ignorando compatibilidad y edad |
| 10 | Género público solo si se elige | `gender_label` aparece solo con `show_gender` |

## Criterios de aceptación

- [x] Los 10 casos pasan.
- [x] Panel de filtros, lupa y pregunta de género funcionan en el celular.

## Fuera de alcance

Distancia y ubicación, numerología, @ usuario y QR (C9), filtrar por intereses, guardar filtros en la cuenta (se guardan en el navegador).

**Cambio posterior (2026-10-20, spec B9)**: "Según qué sistema" pasa a ser qué sistemas suman al número global (`sistemas` reemplaza a `sistema`), y el porcentaje que se ordena y filtra es el global.
