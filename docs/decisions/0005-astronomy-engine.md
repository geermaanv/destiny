# 0005 — `astronomy-engine` en vez de Swiss Ephemeris

- **Estado**: aceptada.

## Contexto

Se necesita un motor de cálculo de posiciones planetarias para signos, aspectos y tránsitos (base de los módulos A y B de `../ALCANCE_MVP.md`). Swiss Ephemeris es el estándar de precisión en software astrológico profesional, pero exige licencia GPL o pago comercial a Astrodienst para uso cerrado/comercial.

## Decisión

Usar `astronomy-engine` (MIT), que calcula posiciones planetarias directamente vía VSOP87/ELP2000, sin restricción de licencia para uso comercial cerrado.

## Consecuencias

- Para compatibilidad de consumo (signos, aspectos, tránsitos) no hace falta la precisión de sistemas de casas de nivel profesional que da Swiss Ephemeris.
- Si más adelante se necesita esa precisión (ej. casas astrológicas exactas para funciones premium), evaluar licenciar Swiss Ephemeris aparte — es una **decisión de negocio**, no un default técnico, y requiere reabrir este ADR.
