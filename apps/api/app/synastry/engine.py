"""Motor oficial de compatibilidad Destiny 1.0 (spec A7): las 8 calculadoras de Pablo.

Un solo motor y tres modalidades de datos (completa+completa, completa+aproximada,
aproximada+aproximada): lo que no se puede calcular (ASC, MC, casas) se omite y su
peso se redistribuye. Todas las tablas, pesos y reglas vienen de
config/synastry_v2.json (generado desde los Excel con scripts/build_synastry_v2.py);
acá solo está el orden de los cálculos, igual al motor de referencia de Pablo.
"""

import json
import math
import unicodedata
from functools import lru_cache
from pathlib import Path

from app.synastry.chart import Chart

CONFIG_PATH = Path(__file__).parent / "config" / "synastry_v2.json"
SCORED_AXES = ("atraccion", "afecto", "comunicacion", "compromiso")
REQUIRED = ("sol", "luna", "mercurio", "venus", "marte", "jupiter", "saturno", "urano", "neptuno", "pluton", "nodo_norte")
MODE_NAMES = ("completa_completa", "completa_aproximada", "aproximada_aproximada")
# Pares de la Gran Cruz: (01, 02, 03, 12, 13, 23); oposiciones (01,23), (02,13), (03,12) y el resto cuadraturas.
CROSS_PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
CROSS_OPPOSITIONS = ((0, 5), (1, 4), (2, 3))


@lru_cache(maxsize=1)
def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, float(x)))


def _angle(a: float, b: float) -> float:
    return abs((a - b + 180) % 360 - 180)


def _sign(lon: float) -> int:
    return int((lon % 360) // 30)


def _whole_sign_house(lon: float, asc: float) -> int:
    """Casa por signo entero, 0 = casa 1."""
    return (_sign(lon) - _sign(asc)) % 12


def _closest_aspect(sep: float, angles: list[float], orbs: list[float]) -> int | None:
    """Un solo aspecto por contacto: el más exacto dentro de su orbe (empate → el primero)."""
    best, best_diff = None, None
    for j, angle in enumerate(angles):
        diff = abs(sep - angle)
        if diff <= orbs[j] and (best_diff is None or diff < best_diff):
            best, best_diff = j, diff
    return best


def _aspect_key(name: str) -> str:
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()


def _contact(found: list, axis_cfg: dict, i: int, j: int, delta: float) -> None:
    x, y = axis_cfg["pares"][i]
    found.append({"a": x, "b": y, "aspecto": _aspect_key(axis_cfg["aspectos"][j]), "puntos": round(delta, 2)})


# ---------------------------------------------------------------- E1 Atracción
def axis_e1(a: dict, b: dict, cfg: dict, found: list) -> tuple[float, float]:
    total = available = 0.0
    for i, (x, y) in enumerate(cfg["pares"]):
        for sender, recv in ((a, b), (b, a)):
            if x not in sender or y not in recv:
                continue
            xx, yy = sender[x], recv[y]
            base = cfg["matrices"][i][_sign(xx)][_sign(yy)]
            j = _closest_aspect(_angle(xx, yy), cfg["angulos"], cfg["orbes"][i])
            delta = 0.0
            if j is not None:
                orb = cfg["orbes"][i][j]
                decay = max(0.0, 1 - abs(_angle(xx, yy) - cfg["angulos"][j]) / orb) ** cfg["exponente"] if orb else 0.0
                delta = cfg["impactos"][i][j] * decay
                _contact(found, cfg, i, j, delta)
            after = clamp(base + delta)
            b1 = cfg["casas"][i][_whole_sign_house(xx, recv["asc"])] if "asc" in recv else 0
            b2 = cfg["casas"][i][_whole_sign_house(yy, sender["asc"])] if "asc" in sender else 0
            weight = cfg["pesos"][i] / 2
            total += clamp(after * (1 + (b1 + b2) / 200)) * weight
            available += weight
    exp = cfg["expansion"]
    return clamp(exp["centro"] + exp["factor"] * (total / available - exp["centro"])), available


# ---------------------------------------------------------------- E2 Afecto
def axis_e2(a: dict, b: dict, cfg: dict, found: list) -> float:
    bonus_cfg = cfg["bonus_exactitud"]
    components = []
    for i, (x, y) in enumerate(cfg["pares"]):
        orbs = [cfg["orbes_por_grupo"][i][g] for g in cfg["grupo_de_cada_aspecto"]]
        values = []
        for sender, recv in ((a, b), (b, a)):
            xx, yy = sender[x], recv[y]
            base = cfg["matrices"][i][_sign(xx)][_sign(yy)]
            sep = _angle(xx, yy)
            j = _closest_aspect(sep, cfg["angulos"], orbs)
            delta = bonus = 0.0
            if j is not None:
                d = abs(cfg["angulos"][j] - sep)
                delta = cfg["impactos"][i][j] * max(0.0, 1 - d / orbs[j]) ** cfg["exponentes"][i]
                if d < bonus_cfg["orbe"] and abs(delta) >= bonus_cfg["umbral_impacto"]:
                    bonus = (
                        (1 if delta > 0 else -1) * bonus_cfg["maximo"] * max(0.0, 1 - d / bonus_cfg["orbe"])
                        * min(1.0, abs(delta) / bonus_cfg["impacto_pleno"])
                    )
                _contact(found, cfg, i, j, delta + bonus)
            lo, hi = (-10, 110) if bonus != 0 else (0, 100)
            before = clamp(base + delta + bonus, lo, hi)
            hb = cfg["casas"][i][_whole_sign_house(xx, recv["asc"])] if "asc" in recv else 0.0
            ha = cfg["casas"][i][_whole_sign_house(yy, sender["asc"])] if "asc" in sender else 0.0
            home = (hb + ha) / 2
            effect = 2 * home if home > 0 else home
            values.append(clamp(before * (1 + effect / 100), lo, hi))
        components.append(sum(values) / len(values))
    return clamp(sum(c * w for c, w in zip(components, cfg["pesos"])))


# ---------------------------------------------------------------- E3 Comunicación
def _e3_house_bonus(lon: float, asc: float | None, cfg: dict) -> float:
    if asc is None:
        return 0.0
    # Planilla 02 CÁLCULO O/P: sectores de 30° desde el GRADO del ASC (no signo entero; pendiente de Pablo).
    house = int(((lon - asc) % 360) // 30) + 1
    return cfg["casas"].get(str(house), 0.0)


def axis_e3(a: dict, b: dict, cfg: dict, found: list) -> float:
    bonus_cfg = cfg["bonus_exactitud"]
    outputs = []
    for i, (x, y) in enumerate(cfg["pares"]):
        directions = [(a, b)] if i in cfg["solo_una_direccion"] else [(a, b), (b, a)]
        values = []
        for sender, recv in directions:
            xx, yy = sender[x], recv[y]
            base = cfg["matrices"][i][_sign(xx)][_sign(yy)]
            sep = _angle(xx, yy)
            j = _closest_aspect(sep, cfg["angulos"], cfg["orbes"])
            delta = bonus = 0.0
            if j is not None:
                d = abs(cfg["angulos"][j] - sep)
                delta = cfg["impactos"][i][j] * max(0.0, 1 - d / cfg["orbes"][j]) ** cfg["exponente"]
                if d < bonus_cfg["orbe"] and abs(delta) >= bonus_cfg["umbral_impacto"]:
                    bonus = (1 if delta > 0 else -1 if delta < 0 else 0) * bonus_cfg["maximo"] * (1 - d / bonus_cfg["orbe"])
                _contact(found, cfg, i, j, delta + bonus)
            q = (_e3_house_bonus(xx, recv.get("asc"), cfg) + _e3_house_bonus(yy, sender.get("asc"), cfg)) / 2
            if bonus == 0:
                values.append(clamp(clamp(base + delta) * (1 + q / 100)))
            else:
                values.append(clamp(clamp(base + delta + bonus, -10, 110) * (1 + q / 100), -10, 110))
        outputs.append(sum(values) / len(values))
    return clamp(sum(o * w for o, w in zip(outputs, cfg["pesos"])))


# ---------------------------------------------------------------- E4 Compromiso
def axis_e4(a: dict, b: dict, cfg: dict, found: list) -> tuple[float, float]:
    bonus_cfg = cfg["bonus_exactitud"]
    total = available = 0.0
    for i, (x, y) in enumerate(cfg["pares"]):
        for sender, recv in ((a, b), (b, a)):
            if x not in sender or y not in recv:
                continue
            xx, yy = sender[x], recv[y]
            base = float(cfg["matrices"][i][_sign(xx)][_sign(yy)])
            sep = _angle(xx, yy)
            j = _closest_aspect(sep, cfg["angulos"], cfg["orbes"])
            delta = bonus = 0.0
            if j is not None:
                d = abs(cfg["angulos"][j] - sep)
                delta = cfg["impactos"][i][j] * max(0.0, 1 - d / cfg["orbes"][j]) ** cfg["exponente"]
                if d < bonus_cfg["orbe"] and abs(delta) >= bonus_cfg["umbral_impacto"]:
                    bonus = (bonus_cfg["positivo"] if delta > 0 else bonus_cfg["negativo"]) * (1 - d / bonus_cfg["orbe"])
                _contact(found, cfg, i, j, delta + bonus)
            aa = cfg["casas_bonus"].get(str(_whole_sign_house(xx, recv["asc"]) + 1), 0) if "asc" in recv else 0
            bb = cfg["casas_bonus"].get(str(_whole_sign_house(yy, sender["asc"]) + 1), 0) if "asc" in sender else 0
            lo, hi = (-10, 110) if bonus else (0, 100)
            weight = cfg["pesos"][i] / 2
            total += weight * clamp(clamp(base + delta + bonus, lo, hi) * (1 + (aa + bb) / 2 / 100), lo, hi)
            available += weight
    exp = cfg["expansion"]
    return clamp(exp["centro"] + exp["factor"] * (clamp(total / available) - exp["centro"])), available


# ---------------------------------------------------------------- E5 Modificadores
def _mean(values) -> float:
    values = list(values)
    return sum(values) / len(values)


def _trine_bonus(sep: list[list[float]], m: dict, rules: dict) -> float:
    orb, exact = rules["orbe_patron_trigono"], rules["orbe_exacto_trigono"]
    tri = rules["trigono"]
    near = [sum(1 for j in range(20) if j != i and abs(sep[i][j] - 120) < orb) for i in range(20)]
    best = 0.0
    for combo in m["gran_trigono"]:
        if any(near[k] < 2 for k in combo):
            continue
        p, q, r = combo
        dists = (abs(sep[p][q] - 120), abs(sep[p][r] - 120), abs(sep[q][r] - 120))
        if not all(d < orb for d in dists):
            continue
        ip, iq, ir = p % 10, q % 10, r % 10
        avg = (m["trigono"][ip][iq] + m["trigono"][ip][ir] + m["trigono"][iq][ir]) / 3
        factor = 1.0 if all(d < exact for d in dists) else rules["factor_no_exacto"]
        benefit = max(0.0, avg - tri["umbral"])
        if tri.get("tope") is not None:
            benefit = min(tri["tope"], benefit)
        benefit *= factor
        if "factor_mercurio" in tri:
            mercury = sum(1 for k in (ip, iq, ir) if k == 2)
            fm = tri["factor_mercurio"]
            benefit *= fm["2_o_mas"] if mercury >= 2 else fm["1"] if mercury == 1 else fm["0"]
        best = max(best, benefit)
    return best


def _cross_effect(values: float, mixed: float | None, rule: dict) -> float:
    form = rule["forma"]
    if form == "atraccion":
        if values >= rule["positivo_desde"]:
            return min(rule["tope"], values - rule["resta"])
        if values <= rule["negativo_hasta"]:
            return max(rule["piso"], values)
        return 0.0
    if form == "solo_negativa":
        return max(rule["piso"], values) if values <= rule["negativo_hasta"] else 0.0
    if values <= rule["bloqueo_fuerte"]:
        return max(rule["piso"], values)
    if values <= rule["bloqueo"]:
        return min(0.0, values + mixed)
    return clamp(values + mixed, rule["piso"], rule["tope"])


def _cross_bonus(sep: list[list[float]], m: dict, rules: dict) -> float:
    orb = rules["orbe_patron_cruz"]
    ok = [
        sum(1 for j in range(20) if j != i and abs(sep[i][j] - 180) <= orb) >= 1
        and sum(1 for j in range(20) if j != i and abs(sep[i][j] - 90) <= orb) >= 2
        for i in range(20)
    ]
    best = 0.0
    for combo in m["gran_cruz"]:
        if not all(ok[k] for k in combo):
            continue
        seps = [sep[combo[p]][combo[q]] for p, q in CROSS_PAIRS]
        present = any(
            all(abs(seps[k] - 180) <= orb for k in opp) and all(abs(seps[k] - 90) <= orb for k in range(6) if k not in opp)
            for opp in CROSS_OPPOSITIONS
        )
        if not present:
            continue
        idx = [k % 10 for k in combo]
        values = _mean(m["cruz"][idx[p]][idx[q]] for p, q in CROSS_PAIRS)
        mixed = _mean(m["cruz_mixta"][idx[p]][idx[q]] for p, q in CROSS_PAIRS) if "cruz_mixta" in m else None
        effect = _cross_effect(values, mixed, rules["cruz"])
        if abs(effect) > abs(best):  # como MATCH(MAX(ABS)) de Excel: el primero que llega al máximo
            best = effect
    return best


def _angular_bonus(a: dict, b: dict, planets: list[str], m: dict, rules: dict) -> float:
    sends = []
    for sender, recv in ((a, b), (b, a)):
        if "asc" not in recv or "mc" not in recv:
            sends.append([])
            continue
        angles = [recv["asc"], (recv["asc"] + 180) % 360, recv["mc"], (recv["mc"] + 180) % 360]
        active = []
        for i, planet in enumerate(planets):
            for j, lon in enumerate(angles):
                d = _angle(sender[planet], lon)
                if d < rules["orbe_angular"]:
                    active.append(m["angular"][i][j] * (1 if d < rules["orbe_exacto_angular"] else rules["factor_no_exacto"]))
        sends.append(active)
    if not all(sends):
        return 0.0
    return clamp((_mean(sends[0]) + _mean(sends[1])) / 2, rules["piso_angular"], rules["tope_angular"])


def modifiers_e5(a: dict, b: dict, cfg: dict) -> dict:
    planets = cfg["planetas"]
    lons = [a[p] for p in planets] + [b[p] for p in planets]
    sep = [[_angle(x, y) for y in lons] for x in lons]
    out = {}
    for axis in SCORED_AXES:
        m = cfg["modificadores_e5"][axis]
        rules = m["reglas"]
        gt = _trine_bonus(sep, m, rules)
        gc = _cross_bonus(sep, m, rules)
        aa = _angular_bonus(a, b, planets, m, rules)
        limit = rules["tope_modificador"]
        out[axis] = {"GT": gt, "GC": gc, "AA": aa, "mod": clamp(gt + gc + aa, -limit, limit)}
    return out


# ---------------------------------------------------------------- Integración
def _check(chart: dict) -> dict:
    missing = [k for k in REQUIRED if k not in chart or chart[k] is None]
    if missing:
        raise ValueError(f"Faltan posiciones: {missing}")
    out = {}
    for key, value in chart.items():
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value < 360:
            raise ValueError(f"Longitud inválida: {key}")
        out[key] = float(value)
    if ("asc" in out) != ("mc" in out):
        raise ValueError("ASC y MC van juntos")
    return out


def calcular(a: dict, b: dict, neutralizar: bool = True) -> dict:
    """Puntajes de Destiny 1.0 entre dos cartas (posiciones en grados). Igual a `calcular` del motor de Pablo."""
    cfg = load_config()
    a, b = _check(a), _check(b)
    exact = ("asc" in a) + ("asc" in b)
    mode = MODE_NAMES[2 - exact]
    found = {axis: [] for axis in SCORED_AXES}
    axes_cfg = cfg["ejes"]
    e1, coverage1 = axis_e1(a, b, axes_cfg["atraccion"], found["atraccion"])
    e2 = axis_e2(a, b, axes_cfg["afecto"], found["afecto"])
    e3 = axis_e3(a, b, axes_cfg["comunicacion"], found["comunicacion"])
    e4, coverage4 = axis_e4(a, b, axes_cfg["compromiso"], found["compromiso"])
    if neutralizar and cfg["modo_reducido"]["neutralizar_compromiso"] and mode != "completa_completa":
        e4 = 50 + (coverage4 / 100) * (e4 - 50)
    base = {"atraccion": e1, "afecto": e2, "comunicacion": e3, "compromiso": e4}
    e5 = modifiers_e5(a, b, cfg)
    integrated = {axis: clamp(base[axis] + e5[axis]["mod"]) for axis in SCORED_AXES}
    globales = {
        kind: sum(w * integrated[axis] for axis, w in t["pesos"].items())
        for kind, t in cfg["tipos_de_relacion"]["tipos"].items()
    }
    return {
        "modalidad": mode,
        "base": base,
        "e5": e5,
        "integrado": integrated,
        "globales": globales,
        "visibles": {k: math.floor(v + 0.5) for k, v in {**integrated, **globales}.items()},
        "cobertura_atraccion": coverage1,
        "cobertura_compromiso": coverage4,
        "contactos": found,
    }


def synastry(a: Chart, b: Chart, relationship: str | None = None) -> dict:
    """Resultado para la app: ejes y total visibles (enteros), detalle para explicar."""
    cfg = load_config()
    types = cfg["tipos_de_relacion"]
    relationship = relationship if relationship in types["tipos"] else types["por_defecto"]
    result = calcular(a.points, b.points)
    return {
        "tipo_de_relacion": relationship,
        "total": result["visibles"][relationship],
        "ejes": {axis: result["visibles"][axis] for axis in SCORED_AXES},
        "ejes_exactos": result["integrado"],
        "aproximado": not (a.time_known and b.time_known),
        "modalidad": result["modalidad"],
        "detalle": {
            axis: {
                "puntaje_base": round(result["base"][axis], 1),
                "modificador_e5": round(result["e5"][axis]["mod"], 2),
                "aspectos_encontrados": sorted(result["contactos"][axis], key=lambda c: -abs(c["puntos"]))[:5],
            }
            for axis in SCORED_AXES
        },
        "version_tablas": cfg["version"],
    }
