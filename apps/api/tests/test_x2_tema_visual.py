"""Spec X2 v2: tema visual según el elemento predominante de la carta."""

import colorsys
from datetime import date, time

import pytest

from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user

ELEMENTS = ["fuego", "tierra", "aire", "agua"]
SCALES = {"slate": [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
          "violet": [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950],
          "gold": [100, 200, 300, 400, 500]}
BIRTHS = [("1990-05-20", "14:30"), ("1985-01-03", "06:10"), ("1979-09-14", "22:05"), ("2000-12-25", "03:40")]


def _expected(birth_date, birth_time, known=True):
    from app.personalization.style import load_config

    weights = load_config()["tema"]["pesos"]
    c = compute_chart(
        date.fromisoformat(birth_date), time.fromisoformat(birth_time), known,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    )
    totals = dict.fromkeys(ELEMENTS, 0.0)
    for point, w in weights.items():
        if point in c.points:
            totals[ELEMENTS[int(c.points[point] // 30) % 4]] += w
    total = sum(totals.values())
    pct = {e: round(100 * v / total) for e, v in totals.items()}
    best = max(totals.values())
    tied = [e for e in ELEMENTS if totals[e] == best]
    theme = tied[0] if len(tied) == 1 else ELEMENTS[int(c.points["sol"] // 30) % 4]
    return theme, pct


@pytest.mark.parametrize("birth", BIRTHS)
def test_tema_por_elemento_predominante(client, birth):
    pid = verified_user(client, "5491111111111", birth_date=birth[0], birth_time=birth[1])
    body = client.get(f"/profiles/{pid}/style").json()
    theme, pct = _expected(*birth)
    assert body["tema"] == body["tema_carta"] == theme
    assert body["tema_source"] == "carta"
    assert body["elementos"] == pct


def test_sin_hora_exacta_no_cuenta_el_ascendente(client):
    pid = verified_user(client, "5491111111111", birth_date="1990-05-20", birth_time=None)
    theme, pct = _expected("1990-05-20", "12:30", known=False)
    body = client.get(f"/profiles/{pid}/style").json()
    assert (body["tema"], body["elementos"]) == (theme, pct)


def test_elegir_tema_y_volver_a_la_carta(client):
    pid = verified_user(client, "5491111111111")
    before = client.get(f"/profiles/{pid}/style").json()
    other = "clasico" if before["tema"] != "clasico" else "agua"
    r = client.put(f"/profiles/{pid}/style", json={"tema": other})
    assert r.status_code == 200
    assert (r.json()["tema"], r.json()["tema_source"]) == (other, "elegido")
    assert r.json()["registro"] == before["registro"] and r.json()["source"] == "carta"
    r = client.put(f"/profiles/{pid}/style", json={"registro": "analitico"})
    assert r.json()["tema"] == other  # cambiar el registro no toca el tema
    r = client.put(f"/profiles/{pid}/style", json={"tema": None})
    assert (r.json()["tema"], r.json()["tema_source"]) == (before["tema_carta"], "carta")
    assert r.json()["registro"] == "analitico"


def test_tema_invalido(client):
    pid = verified_user(client, "5491111111111")
    assert client.put(f"/profiles/{pid}/style", json={"tema": "neon"}).status_code == 422


def test_paleta_del_tema(client):
    from app.personalization.style import load_config

    pid = verified_user(client, "5491111111111")
    for theme in ELEMENTS + ["clasico"]:
        body = client.put(f"/profiles/{pid}/style", json={"tema": theme}).json()
        palette = load_config()["tema"]["temas"][theme]["paleta"]
        assert body["paleta"] == palette
        for scale, steps in SCALES.items():
            assert set(palette[scale]) == {str(s) for s in steps}, (theme, scale)


def _lightness(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return colorsys.rgb_to_hls(r, g, b)[1]


def test_cada_tema_mantiene_la_luminosidad_de_la_clasica():
    from app.personalization.style import load_config

    temas = load_config()["tema"]["temas"]
    classic = temas["clasico"]["paleta"]
    for name, theme in temas.items():
        for scale, steps in classic.items():
            for step, color in steps.items():
                assert abs(_lightness(theme["paleta"][scale][step]) - _lightness(color)) <= 0.02, (name, scale, step)


def test_cambiar_los_pesos_cambia_el_tema(client, monkeypatch):
    from app.personalization.style import load_config

    pid = verified_user(client, "5491111111111", birth_date="1990-05-20", birth_time="14:30")
    theme, _ = _expected("1990-05-20", "14:30")
    c = compute_chart(date(1990, 5, 20), time(14, 30), True, BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"])
    target = next(p for p in ("sol", "luna", "asc", "mercurio", "venus", "marte") if ELEMENTS[int(c.points[p] // 30) % 4] != theme)
    monkeypatch.setitem(load_config()["tema"], "pesos", {target: 1})
    assert client.get(f"/profiles/{pid}/style").json()["tema"] == ELEMENTS[int(c.points[target] // 30) % 4]
