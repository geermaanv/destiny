# C12-invitar-simple — Invitar en un paso: nombre, signo si lo sabés, y el mensaje se arma solo

- **Estado**: implemented
- **Módulo**: C (crecimiento); simplifica C8 (v1 adelanto astrológico, v2 comparar el test)
- **Owner de decisión de producto**: German Villamarin (por ahora)
- **Aprobada para implementación por**: German Villamarin, 2026-10-20 ("hagamos algo más simple: le preguntamos nombre y signo; si sabe el signo, incluimos el adelanto astrológico como gancho; si ya hizo el test, hacemos la comparación").

## Problema

Invitar tenía cuatro pasos y dos tipos de invitación para entender (comparar test o adelanto astrológico), pedía el vínculo, frenaba a quien no había completado su test y tenía un paso de vista previa antes de mandar.

## Puntos abiertos

Ninguno.

## Requisitos funcionales

- **Un solo formulario**: su nombre (obligatorio) y su signo (opcional, "No lo sé"). Debajo, el mensaje armado en vivo y el botón **"Enviar por WhatsApp"**. Sin elegir tipo, sin vínculo, sin paso de vista previa.
- **El mensaje se arma solo**:
  - Siempre: "¡Hola {nombre}! ¿Por qué con algunas personas fluye y con otras no?" y el link.
  - Con su signo: suma el adelanto astrológico (signo del amigo con tu carta, aproximado).
  - Si completaste tu test: suma "Ya completé mi test de personalidad: hacelo vos y comparamos". Si no, no lo menciona (no frena).
- **Vínculo**: el que tenés en "¿Qué buscás?" (spec A12) o pareja.
- **Del lado del invitado**: la página de la invitación muestra el adelanto si hay signo, la invitación al test si quien invita lo hizo, o un mensaje general si no hay ninguna de las dos. Se registra, acepta, quedan conectados (como en C8) y suma la pregunta extra de C11.

## Contrato de datos / API

```
POST /invitations          {inviter_id, friend_name, friend_sun_sign?} → 201 InvitationOut (crea la invitación)
POST /invitations/preview  {inviter_id, friend_name, friend_sun_sign?} → {message} (no crea nada; el link va como "[link]")
```

- `kind` y `relationship` ya no se mandan: `kind` = "test" si quien invita completó su test, si no "astro"; `relationship` = su "¿Qué buscás?" o "pareja".
- `partial_report` cuando hay signo.

## Casos de prueba (`apps/api/tests/test_c12_invitar_simple.py`)

| # | Caso | Resultado esperado |
|---|---|---|
| 1 | Solo el nombre | 201; saludo, gancho y link; sin adelanto ni test |
| 2 | Con su signo | El mensaje trae el adelanto y hay `partial_report` |
| 3 | Con mi test completo | El mensaje invita a comparar el test; `kind` = test |
| 4 | Sin mi test completo | Igual se crea (no hay 409) y no menciona el test |
| 5 | Vínculo | Toma mi "¿Qué buscás?"; sin dato, pareja |
| 6 | Vista previa | Devuelve el mismo mensaje con "[link]" y no crea invitaciones |
| 7 | Página del invitado sin signo ni test | Mensaje general con el nombre de quien invita |

## Criterios de aceptación

- [x] Los 7 casos pasan; los tests de C8 que pedían tipo o test completo se ajustan.
- [x] Un solo formulario con el mensaje en vivo y "Enviar por WhatsApp".

## Fuera de alcance

Link personal reutilizable, menú de compartir del celular, QR (spec C9).
