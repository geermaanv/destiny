# R1-robustez-y-validaciones — Datos inválidos rechazados y sin errores 500

- **Estado**: implemented
- **Módulo**: transversal (API)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-22 ("arrancá por todo"), a partir del primer informe del agente breaker (hallazgos 1, 10, 11, 12, 13, 15, 17 y 18).

## Problema

El agente breaker encontró que la API acepta datos que después la rompen. El caso más grave: un solo perfil con una zona horaria inexistente o coordenadas NaN deja Descubrir con error 500 para todos. También errores 500 con fechas extremas, caracteres nulos o pedidos dobles, y fotos que no son imágenes.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

1. **Datos de nacimiento**: la zona horaria tiene que existir (base IANA); latitud entre -90 y 90 y longitud entre -180 y 180, números finitos (sin NaN ni infinito); el texto del lugar hasta 200 caracteres; la fecha desde el 1/1/1900. Lo mismo para "Dónde vivís". Si no, 422.
2. **Descubrir no se cae por un candidato roto**: si calcular la compatibilidad con alguien falla, esa persona se saltea (y queda en el log), y el resto se muestra.
3. **Fechas fuera de rango → 422, no 500**: calendario (mes 1 a 12, año 1900 a 2100), próximos eventos, Tu día, Tu día completo, Hoy e Indagar con `dia`: entre 1900 y 2100.
4. **Textos**: se sacan los caracteres nulos y los invisibles (espacios de ancho cero) de nombres, frases, barrio, mensajes, preguntas a Indagar, nombre del invitado, detalle de género y lugares; un texto que queda vacío es inválido.
5. **Los errores 422 nunca dan 500**: la respuesta de validación no repite el valor recibido (un NaN no se puede devolver en JSON).
6. **Fotos**: además del tipo declarado, el contenido tiene que ser JPG, PNG o WebP de verdad (sus primeros bytes) y no puede estar vacío → si no, 415. Las fotos se sirven con `X-Content-Type-Options: nosniff`.
7. **Doble toque al aceptar una invitación**: dos pedidos a la vez no dan error; queda una sola aceptación.
8. **Webhook de WhatsApp**: un JSON con otra forma se ignora (200), sin error.

## Casos de prueba (`apps/api/tests/test_r1_robustez_y_validaciones.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Zona horaria inexistente, lat/lon fuera de rango, NaN, lugar gigante, año 1800 | 422 |
| 2 | Un candidato con datos rotos en la base | Descubrir responde 200 y muestra al resto |
| 3 | Fechas fuera de rango en calendario, Tu día, Indagar | 422 |
| 4 | Textos con nulos o solo invisibles | Se limpian; si quedan vacíos, 422 |
| 5 | Residencia con NaN | 422 (no 500) |
| 6 | Foto que dice ser PNG pero no lo es, o vacía | 415; las fotos llevan `nosniff` |
| 7 | Aceptar una invitación dos veces a la vez | Sin 500 |
| 8 | Webhook con otra forma | 200 |

## Criterios de aceptación

- [x] Los casos pasan.

## Fuera de alcance

Cookie de sesión `Secure` en desarrollo (se resuelve al pasar a hosting, BACKLOG).
