"""Genera app/synastry/config/synastry_v2.json desde las 8 calculadoras oficiales de Pablo (spec A7).

Lee solo los valores de las celdas (no ejecuta nada de las planillas) en las mismas posiciones que usa
el motor de referencia de Pablo. Los Excel NO están en el repo: viven en ~/proyectos/destiny-fuentes/.

Uso: .venv/bin/python scripts/build_synastry_v2.py [ruta/al/zip_de_las_8_calculadoras]
"""

import hashlib
import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

DEFAULT_ZIP = Path.home() / "proyectos" / "destiny-fuentes" / "calculadoras_oficiales_v1_0.zip"
OUT = Path(__file__).resolve().parents[1] / "app" / "synastry" / "config" / "synastry_v2.json"
NS = {
    "m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
FILES = {
    "E1": "EJE1 FINAL.xlsm",
    "E2": " EJE 2 FINAL.xlsm",
    "E3": "EJE 3 FINAL .xlsm",
    "E4": "EJE4 FINAL.xlsm",
    "E5-1": "EJE5-1 FINAL.xlsm",
    "E5-2": "EJE5-2 FINAL.xlsm",
    "E5-3": "E5-3 FINAL.xlsm",
    "E5-4": "E5-4 FINAL.xlsm",
}
PLANETS = ["Sol", "Luna", "Mercurio", "Venus", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno", "Plutón"]
# Nombres de las planillas → claves del motor (las mismas de chart.py).
KEY = {
    "Sol": "sol", "Luna": "luna", "Mercurio": "mercurio", "Venus": "venus", "Marte": "marte",
    "Júpiter": "jupiter", "Saturno": "saturno", "Urano": "urano", "Neptuno": "neptuno", "Plutón": "pluton",
    "ASC": "asc", "MC": "mc", "Nodo Norte Verdadero": "nodo_norte",
}


def read_book(raw: bytes) -> dict[str, dict[str, object]]:
    z = zipfile.ZipFile(io.BytesIO(raw))
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    rels = {e.get("Id"): e.get("Target").lstrip("/") for e in ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))}
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        shared = ["".join(t.text or "" for t in si.findall(".//m:t", NS)) for si in root.findall("m:si", NS)]
    sheets = {}
    for sheet in wb.findall("m:sheets/m:sheet", NS):
        target = rels[sheet.get("{%s}id" % NS["r"])]
        target = target if target.startswith("xl/") else "xl/" + target
        cells = {}
        for c in ET.fromstring(z.read(target)).findall(".//m:sheetData/m:row/m:c", NS):
            v = c.find("m:v", NS)
            x = v.text if v is not None else None
            if c.get("t") == "s" and x:
                x = shared[int(x)]
            if c.get("t") == "inlineStr":
                x = "".join(t.text or "" for t in c.findall(".//m:t", NS))
            try:
                x = float(x)
            except (TypeError, ValueError):
                pass
            if x is not None:
                cells[c.get("r")] = x
        sheets[sheet.get("name")] = cells
    return sheets


def col(index: int) -> str:
    """1 → A, 27 → AA."""
    out = ""
    while index:
        index, k = divmod(index - 1, 26)
        out = chr(65 + k) + out
    return out


class Book:
    def __init__(self, sheets):
        self.sheets = sheets

    def get(self, sheet, cell):
        return self.sheets[sheet].get(cell)

    def num(self, sheet, cell) -> float:
        value = self.get(sheet, cell)
        if not isinstance(value, float):
            raise ValueError(f"{sheet}!{cell} no es numérico: {value!r}")
        return value

    def matrix(self, sheet, first_row=2, first_col=2, n=12, m=None) -> list[list[float]]:
        return [[self.num(sheet, f"{col(first_col + j)}{first_row + i}") for j in range(m or n)] for i in range(n)]


def pair(a: str, b: str) -> list[str]:
    return [KEY[a], KEY[b]]


def build_e1(b: Book) -> dict:
    pairs = [("Venus", "Marte"), ("ASC", "Venus"), ("ASC", "Marte"), ("Venus", "Venus"), ("Marte", "Marte"),
             ("Sol", "ASC"), ("Plutón", "Venus"), ("Plutón", "Marte")]
    sheets = ["M Venus-Marte", "M ASC-Venus", "M ASC-Marte", "M Venus-Venus", "M Marte-Marte", "M Sol-ASC",
              "M Pluton-Venus", "M Pluton-Marte"]
    return {
        "nombre": "Atracción",
        "pares": [pair(x, y) for x, y in pairs],
        "pesos": [b.num("07 CASAS", f"B{i + 2}") for i in range(8)],
        "matrices": [b.matrix(s) for s in sheets],
        "aspectos": [b.get("05 ASPECTOS", f"A{j + 2}") for j in range(11)],
        "angulos": [b.num("05 ASPECTOS", f"C{j + 2}") for j in range(11)],
        "impactos": [[b.num("05 ASPECTOS", f"{col(i + 5)}{j + 2}") for j in range(11)] for i in range(8)],
        "orbes": [[b.num("08 TOLERANCIAS V1.2", f"{col(j + 2)}{i + 2}") for j in range(11)] for i in range(8)],
        "casas": [[b.num("07 CASAS", f"{col(j + 5)}{i + 2}") for j in range(12)] for i in range(8)],
        "exponente": 0.7,
        "expansion": {"centro": b.num("E1 EXPANSION 145", "B3"), "factor": b.num("E1 EXPANSION 145", "B4")},
    }


def build_e2(b: Book) -> dict:
    pairs = [("Sol", "Luna"), ("Luna", "Luna"), ("Luna", "Venus"), ("Saturno", "Luna"), ("Júpiter", "Luna"),
             ("Plutón", "Luna"), ("Marte", "Luna"), ("Neptuno", "Luna")]
    return {
        "nombre": "Afecto",
        "pares": [pair(x, y) for x, y in pairs],
        "pesos": [b.num("01 PONDERACIONES", f"B{i + 2}") for i in range(8)],
        "matrices": [b.matrix(f"M {x}-{y}") for x, y in pairs],
        "aspectos": [b.get("03 ASPECTOS", f"A{j + 2}") for j in range(11)],
        "angulos": [b.num("03 ASPECTOS", f"B{j + 2}") for j in range(11)],
        "impactos": [[b.num("03 ASPECTOS", f"{col(i + 4)}{j + 2}") for j in range(11)] for i in range(8)],
        # Orbes por grupo: conjunción/oposición, cuadratura/trígono, sextil, menores.
        "orbes_por_grupo": [[b.num("04 ORBES", f"{col(j + 2)}{i + 2}") for j in range(4)] for i in range(8)],
        "grupo_de_cada_aspecto": [0, 2, 1, 1, 0, 3, 3, 3, 3, 3, 3],
        "exponentes": [b.num("04 ORBES", f"F{i + 2}") for i in range(8)],
        "casas": [[b.num("05 CASAS", f"{col(j + 2)}{i + 2}") for j in range(12)] for i in range(8)],
        "bonus_exactitud": {"orbe": 2.0, "umbral_impacto": 20.0, "maximo": 10.0, "impacto_pleno": 30.0},
    }


def build_e3(b: Book) -> dict:
    pairs = [("Mercurio", "Mercurio"), ("Mercurio", "Júpiter"), ("Mercurio", "Sol"), ("Mercurio", "Saturno"),
             ("Mercurio", "Marte"), ("Mercurio", "Plutón"), ("Mercurio", "Luna")]
    p = "01 PARÁMETROS"
    return {
        "nombre": "Comunicación",
        "pares": [pair(x, y) for x, y in pairs],
        "solo_una_direccion": [0],
        "pesos": [b.num(p, f"B{i + 2}") for i in range(7)],
        "matrices": [b.matrix(f"M{i + 1} {x}-{y}") for i, (x, y) in enumerate(pairs)],
        "aspectos": [b.get(p, f"E{j + 2}") for j in range(5)],
        "angulos": [b.num(p, f"F{j + 2}") for j in range(5)],
        "orbes": [b.num(p, f"G{j + 2}") for j in range(5)],
        "impactos": [[b.num(p, f"{col(13 + j)}{i + 2}") for j in range(5)] for i in range(7)],
        "exponente": 0.7,
        # Casas desde el GRADO del ASC en sectores de 30° (planilla 02 CÁLCULO O/P; pendiente de Pablo).
        "casas_desde_grado_asc": True,
        "casas": {"3": b.num(p, "R2"), "9": b.num(p, "S2"), "11": b.num(p, "M11")},
        "bonus_exactitud": {"orbe": 2.0, "umbral_impacto": 20.0, "maximo": 10.0},
    }


def build_e4(b: Book) -> dict:
    pairs = [("Saturno", "Venus"), ("Saturno", "Sol"), ("Saturno", "Luna"), ("Saturno", "ASC"), ("Saturno", "MC"),
             ("Júpiter", "Sol"), ("Saturno", "Nodo Norte Verdadero"), ("Nodo Norte Verdadero", "Sol"),
             ("Nodo Norte Verdadero", "Luna")]
    sheets = ["M1 Saturno-Venus", "M2 Saturno-Sol", "M3 Saturno-Luna", "M4 Saturno-Ascendente",
              "M5 Saturno-Medio Cielo", "M6 Júpiter-Sol", "M7 Saturno-Nodo Norte", "M8 Nodo Norte-Sol",
              "M9 Nodo Norte-Luna"]
    p = "02 PARAMETROS"
    return {
        "nombre": "Compromiso",
        "pares": [pair(x, y) for x, y in pairs],
        "pesos": [b.num(p, f"B{i + 2}") for i in range(9)],
        "matrices": [b.matrix(s) for s in sheets],
        "aspectos": [b.get(p, f"L{j + 2}") for j in range(5)],
        "angulos": [b.num(p, f"M{j + 2}") for j in range(5)],
        "orbes": [b.num(p, f"N{j + 2}") for j in range(5)],
        "impactos": [[b.num(p, f"{col(2 + j)}{14 + i}") for j in range(5)] for i in range(9)],
        "exponente": 0.7,
        "casas_bonus": {str(int(b.num(p, f"Q{i + 2}"))): b.num(p, f"R{i + 2}") for i in range(4)},
        "bonus_exactitud": {"orbe": 2.0, "umbral_impacto": 20.0, "positivo": 40.0, "negativo": -20.0},
        "juno": "no se informa (opcional en la planilla; pendiente de Pablo)",
        "expansion": {"centro": b.num("E4 EXPANSION 120", "B2"), "factor": b.num("E4 EXPANSION 120", "B3")},
    }


def _combos(b: Book, sheet: str, first: int, last: int, columns: str) -> list[list[int]]:
    """Combinaciones literales de la planilla: 'A Sol' → 0, 'B Luna' → 11 (0-9 persona A, 10-19 persona B)."""
    out = []
    for r in range(first, last + 1):
        labels = [b.get(sheet, f"{c}{r}") for c in columns]
        if any(not isinstance(x, str) for x in labels):
            continue
        idx = []
        for raw in labels:
            side, planet = raw.split(" ", 1)
            if planet not in PLANETS or side not in ("A", "B"):
                idx = []
                break
            idx.append((0 if side == "A" else 10) + PLANETS.index(planet))
        if len(idx) == len(columns):
            out.append(idx)
    return out


def build_e5(name: str, b: Book) -> dict:
    new = name in ("E5-3", "E5-4")
    tri_row, cross_row, angular_row = (2, 15, 40) if new else (4, 17, 30)
    out = {
        "trigono": b.matrix("06 MATRICES", tri_row, 2, 10),
        "cruz": b.matrix("06 MATRICES", cross_row, 2, 10),
        "angular": b.matrix("06 MATRICES", angular_row, 2, 10, 4),
        "gran_trigono": _combos(b, "03 GRAN TRIGONO", 2 if new else 4, 1141 if new else 1143, "ABC"),
        "gran_cruz": _combos(b, "04 GRAN CRUZ", 2 if new else 4, 4846 if new else 4848, "ABCD"),
    }
    if new:
        out["cruz_mixta"] = b.matrix("06 MATRICES", 28, 2, 10)
    out["reglas"] = E5_RULES[name]
    return out


# Reglas de los modificadores (fórmulas de las hojas E5, tal como las reproduce el motor de referencia de Pablo).
_COMMON = {
    "orbe_patron_trigono": 2.0, "orbe_exacto_trigono": 1.0, "factor_no_exacto": 0.5,
    "orbe_patron_cruz": 3.0, "orbe_angular": 2.0, "orbe_exacto_angular": 1.0, "tope_angular": 8.0, "tope_modificador": 10.0,
}
E5_RULES = {
    "E5-1": _COMMON | {
        "trigono": {"umbral": 4.0, "tope": None},
        "cruz": {"forma": "atraccion", "positivo_desde": 4.0, "resta": 3.0, "tope": 8.0, "negativo_hasta": -1.0, "piso": -3.0},
        "piso_angular": -3.0,
    },
    "E5-2": _COMMON | {
        "trigono": {"umbral": 5.0, "tope": 7.0},
        "cruz": {"forma": "solo_negativa", "negativo_hasta": -2.0, "piso": -8.0},
        "piso_angular": -6.0,
    },
    "E5-3": _COMMON | {
        "trigono": {"umbral": 4.0, "tope": 6.0, "factor_mercurio": {"0": 0.75, "1": 0.9, "2_o_mas": 1.0}},
        "cruz": {"forma": "mixta", "bloqueo_fuerte": -4.0, "bloqueo": -2.0, "piso": -8.0, "tope": 4.0},
        "piso_angular": -6.0,
    },
    "E5-4": _COMMON | {
        "trigono": {"umbral": 4.0, "tope": 6.0},
        "cruz": {"forma": "mixta", "bloqueo_fuerte": -4.0, "bloqueo": -2.0, "piso": -8.0, "tope": 3.0},
        "piso_angular": -6.0,
    },
}


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ZIP
    archive = zipfile.ZipFile(source)
    raw = {key: archive.read(name) for key, name in FILES.items()}
    books = {key: Book(read_book(data)) for key, data in raw.items()}
    config = {
        "version": "destiny-1.0",
        "fuente": {
            "descripcion": "Calculadoras oficiales de Pablo (paquete DESTINY 1.0, 13/10/2026). Generado con "
            "scripts/build_synastry_v2.py; no editar a mano: si Pablo cambia una planilla, se regenera.",
            "zip_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "archivos_sha256": {FILES[k]: hashlib.sha256(v).hexdigest() for k, v in raw.items()},
        },
        "planetas": [KEY[p] for p in PLANETS],
        "ejes": {
            "atraccion": build_e1(books["E1"]),
            "afecto": build_e2(books["E2"]),
            "comunicacion": build_e3(books["E3"]),
            "compromiso": build_e4(books["E4"]),
        },
        "modificadores_e5": {
            "atraccion": build_e5("E5-1", books["E5-1"]),
            "afecto": build_e5("E5-2", books["E5-2"]),
            "comunicacion": build_e5("E5-3", books["E5-3"]),
            "compromiso": build_e5("E5-4", books["E5-4"]),
        },
        "modo_reducido": {
            "neutralizar_compromiso": True,
            "descripcion": "Sin hora exacta: E4 = 50 + cobertura/100 × (E4 − 50). Experimental de Pablo.",
        },
        "tipos_de_relacion": {
            "por_defecto": "pareja",
            "tipos": {
                "ocasional": {"nombre": "Sexual ocasional", "pesos": {"atraccion": 0.70, "afecto": 0.10, "comunicacion": 0.15, "compromiso": 0.05}},
                "pareja": {"nombre": "Pareja formal", "pesos": {"atraccion": 0.25, "afecto": 0.25, "comunicacion": 0.25, "compromiso": 0.25}},
                "amistad": {"nombre": "Amistad", "pesos": {"atraccion": 0.10, "afecto": 0.35, "comunicacion": 0.40, "compromiso": 0.15}},
                "laboral": {"nombre": "Profesional", "pesos": {"atraccion": 0.10, "afecto": 0.10, "comunicacion": 0.40, "compromiso": 0.40}},
            },
        },
        "explicacion": {"peso_minimo_eje": 0.15},
    }
    OUT.write_text(json.dumps(config, ensure_ascii=False, separators=(",", ":")) + "\n")
    e5 = {k: (len(v["gran_trigono"]), len(v["gran_cruz"])) for k, v in config["modificadores_e5"].items()}
    print(f"Escrito {OUT} ({OUT.stat().st_size // 1024} KB). Combinaciones GT/GC: {e5}")
    assert re.match(r"^[0-9a-f]{64}$", config["fuente"]["zip_sha256"])


if __name__ == "__main__":
    main()
