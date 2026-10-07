# 0009 — Geocodificación del lugar de nacimiento con Open-Meteo

- **Estado**: aceptada (2026-10-07).

## Contexto

La spec `A1` pide que el lugar de nacimiento se geocodifique a lat/lon + timezone (necesario para ascendente y casas). Hasta ahora era texto libre sin coordenadas. Basta con la ciudad: la diferencia entre puntos de una misma ciudad es despreciable para el cálculo, y pedir una dirección suma fricción y datos sensibles.

## Decisión

Autocomplete de ciudad contra la API de geocodificación de **Open-Meteo**, detrás de un adapter (`app/geocoding.py`, endpoint `GET /geocoding/search?q=`), con el mismo patrón que los otros adapters.

- Gratis, sin API key, y devuelve la **timezone** directamente (Photon/Nominatim no, habría que sumar una librería para calcularla).
- Se busca primero en Argentina (`countryCode=AR`, mercado de lanzamiento) y después en el resto del mundo.
- Alias para formas habituales que el geocoder no reconoce: "CABA", "Capital Federal", "Bs As" → Buenos Aires.
- Sin dependencias nuevas: la llamada usa `urllib` de la librería estándar.

## Consecuencias

- Los términos de Open-Meteo lo dan gratis para **uso no comercial**. Para el MVP alcanza; antes de abrir a usuarios reales con fines comerciales, revisar los términos o pasar a su plan pago (o cambiar de proveedor: solo se reescribe el adapter).
- Si Open-Meteo no responde, la pantalla acepta el texto libre sin coordenadas para no bloquear el onboarding.
