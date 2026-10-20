# B10-filtros-activos-intereses — Filtros activos con ✕ e intereses en Círculo

- **Estado**: implemented
- **Módulo**: B5 (Descubrir / Círculo)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 (boceto de filtros activos; "filtra con todos"; "N intereses en común" siempre en la tarjeta). Viene de la reunión de check con Pablo: "organizar Círculo por intereses".

## Problema

Con varios filtros (sistemas, compatibilidad, edad, distancia) no se ve qué está aplicado ni hay una forma rápida de sacarlo. Y los intereses de cada persona no ayudan a elegir: no se pueden filtrar ni se ve qué tienen en común.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

- **Filtros activos** (web): debajo de la búsqueda, una pastilla por cada filtro distinto del valor por defecto (distancia, edad, compatibilidad mínima, sistema apagado, cada interés), con ✕ para sacarlo, y "Borrar todos" si hay más de uno. "¿Qué buscás?" no lleva ✕: siempre hay uno elegido.
- **Filtro de intereses**: en el panel Filtros, los 12 intereses para marcar y el atajo "Usar mis intereses". Aparece solo quien tiene **todos** los intereses marcados.
- **Intereses en común**: cada tarjeta muestra "N intereses en común: …" (los que coinciden con los tuyos), siempre, aunque no se filtre por intereses. Sin ninguno en común no se muestra nada.
- **Orden**: por número global (B9); a igual número, primero quien tiene más intereses en común.
- La búsqueda por nombre ignora el filtro de intereses, como los demás filtros (B8).

## Contrato de datos / API

```
GET /discover?...&intereses=musica,viajes   (inválido → 422)
```

Por candidato: `common_interests: ["musica", "viajes"]` (en el orden de la lista de intereses de A4).

## Casos de prueba (`apps/api/tests/test_b10_filtros_activos_intereses.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Filtra con todos | Con "música y viajes" aparece quien tiene los dos; no quien tiene uno solo |
| 2 | Interés inválido | 422 |
| 3 | Intereses en común siempre | `common_interests` es la coincidencia con los míos, aunque no filtre |
| 4 | Desempate | A igual número global, primero quien tiene más intereses en común |
| 5 | La búsqueda ignora el filtro | Buscando por nombre aparece aunque no tenga los intereses |

## Criterios de aceptación

- [x] Los 5 casos pasan.
- [x] Filtros activos con ✕, sección de intereses y "N intereses en común" en el celular.

## Fuera de alcance

Intereses nuevos o libres, pesar los intereses en el número global.

**Ajuste (2026-10-20, German)**: la fila de filtros se ve siempre, con todos los criterios: los que están por defecto en gris y sin ✕ (tocarlos abre Filtros), los que cambiaste resaltados y con ✕.
