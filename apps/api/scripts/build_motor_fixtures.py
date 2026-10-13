"""Arma tests/fixtures/motor_oficial_casos.json con casos de referencia del paquete DESTINY 1.0 (spec A7).

Toma de las auditorías de Pablo (1.500 sinastrías sintéticas, calculadas por SU motor) las posiciones de
entrada y los resultados esperados en las 3 modalidades. Elige todos los casos donde algún patrón E5 está
activo más una muestra del resto, y suma los 3 resultados de demostración del paquete.

Uso: .venv/bin/python scripts/build_motor_fixtures.py ruta/a/DESTINY_1_0_ENTREGA_CONSOLIDADA
"""

import json
import sys
import zipfile
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "motor_oficial_casos.json"
KEY = {
    "Sol": "sol", "Luna": "luna", "Mercurio": "mercurio", "Venus": "venus", "Marte": "marte",
    "Júpiter": "jupiter", "Saturno": "saturno", "Urano": "urano", "Neptuno": "neptuno", "Plutón": "pluton",
    "ASC": "asc", "MC": "mc", "Nodo Norte Verdadero": "nodo_norte", "Nodo Norte Medio": "nodo_medio",
}
AXES = {"E1": "atraccion", "E2": "afecto", "E3": "comunicacion", "E4": "compromiso"}
E5 = {"E5-1": "atraccion", "E5-2": "afecto", "E5-3": "comunicacion", "E5-4": "compromiso"}
RELATIONS = {"Sexual ocasional": "ocasional", "Pareja formal": "pareja", "Amistad": "amistad", "Profesional": "laboral"}
EXTRA_SAMPLE = 60


def positions(chart: dict) -> dict:
    return {KEY[k]: v for k, v in chart.items() if k in KEY}


def birth(person: dict) -> dict:
    return {k: person[k] for k in ("date", "lat", "lon", "tz", "part", "utc_exact", "utc_mid")}


def mode(m: dict) -> dict:
    return {
        "base": {AXES[k]: v for k, v in m["base"].items()},
        "e5": {E5[k]: {c: v[c] for c in ("GT", "GC", "AA", "mod")} for k, v in m["e5"].items()},
        "integrado": {AXES[k]: v for k, v in m["integrated"].items()},
        "cobertura_compromiso": m["E4_weight"],
    }


def main():
    root = Path(sys.argv[1]) / "02_MOTOR_Y_EJEMPLOS"
    charts = [json.loads(x) for x in (root / "auditorias" / "DESTINY_AUDITORIA_E1_1500_CASOS.jsonl").read_text().splitlines()]
    z = zipfile.ZipFile(root / "auditorias" / "auditoria_historica_E2_E3_E4_E5.zip")
    expected = [json.loads(x) for x in z.read("DESTINY_AUDITORIA_E2_E3_E4_E5_REDUCIDO_1500_CASOS.jsonl").decode().splitlines()]

    def active(r):
        return any(v[c] != 0 for m in r["modes"] for v in m["e5"].values() for c in ("GT", "GC", "AA"))

    picked = [i for i, r in enumerate(expected) if active(r)]
    rest = [i for i in range(len(expected)) if i not in set(picked)]
    picked = sorted(picked + rest[:: max(1, len(rest) // EXTRA_SAMPLE)][:EXTRA_SAMPLE])

    cases = []
    for i in picked:
        c, r = charts[i], expected[i]
        assert c["n"] == r["n"]
        cases.append({
            "n": c["n"],
            "A": {"completa": positions(c["A"]["full"]), "aproximada": positions(c["A"]["approx"]), "nacimiento": birth(c["A"])},
            "B": {"completa": positions(c["B"]["full"]), "aproximada": positions(c["B"]["approx"]), "nacimiento": birth(c["B"])},
            "esperado": {name: mode(m) for name, m in zip(("completa_completa", "completa_aproximada", "aproximada_aproximada"), r["modes"])},
        })

    demos = []
    for name in ("completa_completa", "completa_aproximada", "aproximada_aproximada"):
        data = json.loads((root / "ejemplos" / f"{name}.json").read_text())
        result = json.loads((Path(sys.argv[1]) / "06_EJECUCIONES_VERIFICADAS" / f"demo_{name}_resultado.json").read_text())
        demos.append({
            "modalidad": name,
            "A": positions(data["A"].get("posiciones", data["A"])),
            "B": positions(data["B"].get("posiciones", data["B"])),
            "ejes_finales": {AXES[k]: v for k, v in result["ejes_finales"].items()},
            "globales": {RELATIONS[k]: v for k, v in result["resultados_globales"].items()},
            "visibles": {RELATIONS.get(k, AXES.get(k)): v for k, v in result["resultados_visibles"].items()},
            "cobertura_compromiso": result["cobertura_E4"],
        })

    OUT.write_text(json.dumps({
        "fuente": "Auditorías del paquete DESTINY 1.0 de Pablo (motor de referencia con Swiss Ephemeris/Moshier).",
        "casos": cases,
        "demos": demos,
    }, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Escrito {OUT}: {len(cases)} casos ({OUT.stat().st_size // 1024} KB), {len(demos)} demos")


if __name__ == "__main__":
    main()
