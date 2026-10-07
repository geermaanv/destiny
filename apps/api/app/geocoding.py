"""Geocodificación del lugar de nacimiento (spec A1): texto -> lat/lon + timezone.

Adapter con el mismo patrón que KYC/explainer/icebreaker: el proveedor actual
es Open-Meteo (gratis, sin key, devuelve timezone). Sus términos lo dan gratis
para uso no comercial; revisar antes de abrir a usuarios reales.
"""

import json
import logging
import unicodedata
from dataclasses import dataclass
from typing import Protocol
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
MAX_RESULTS = 6

# Formas habituales de nombrar CABA que el geocoder no reconoce.
ALIASES = {
    "caba": "Buenos Aires",
    "capital federal": "Buenos Aires",
    "capital": "Buenos Aires",
    "ciudad autonoma de buenos aires": "Buenos Aires",
    "bs as": "Buenos Aires",
    "bsas": "Buenos Aires",
}


class GeocodingUnavailable(Exception):
    pass


@dataclass
class Place:
    label: str
    lat: float
    lon: float
    timezone: str


class Geocoder(Protocol):
    def search(self, query: str) -> list[Place]: ...


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(text.lower().replace(".", " ").split())


class OpenMeteoGeocoder:
    def _fetch(self, name: str, country_code: str | None) -> list[dict]:
        params = {"name": name, "count": MAX_RESULTS, "language": "es", "format": "json"}
        if country_code:
            params["countryCode"] = country_code
        request = Request(f"{OPEN_METEO_URL}?{urlencode(params)}", headers={"User-Agent": "destiny-mvp"})
        try:
            with urlopen(request, timeout=5) as response:
                return json.load(response).get("results", [])
        except (URLError, TimeoutError, ValueError) as exc:
            logger.warning("Open-Meteo geocoding failed: %s", exc)
            raise GeocodingUnavailable from exc

    def search(self, query: str) -> list[Place]:
        name = ALIASES.get(_normalize(query), query.strip())
        # Mercado de lanzamiento: Argentina primero, después el resto del mundo.
        results = self._fetch(name, "AR") + self._fetch(name, None)

        places: list[Place] = []
        seen: set[str] = set()
        for r in results:
            if not r.get("timezone") or r.get("feature_code", "").startswith("AIRP"):
                continue
            parts = [r["name"], r.get("admin1"), r.get("country")]
            label = ", ".join(dict.fromkeys(p for p in parts if p))
            if label in seen:
                continue
            seen.add(label)
            places.append(Place(label=label, lat=r["latitude"], lon=r["longitude"], timezone=r["timezone"]))
        return places[:MAX_RESULTS]


def get_geocoder() -> Geocoder:
    return _default_geocoder


_default_geocoder = OpenMeteoGeocoder()
