"""Spec X2 v3: acento por Venus, modo claro, contraste, tipografía y cielo de nacimiento."""

from datetime import date, time

import pytest

from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user

ELEMENTS = ["fuego", "tierra", "aire", "agua"]
BIRTH = ("1990-05-20", "14:30")


def _chart(known=True, birth_time=BIRTH[1]):
    return compute_chart(
        date.fromisoformat(BIRTH[0]), time.fromisoformat(birth_time), known,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    )


def _temas():
    from app.personalization.style import load_config

    return load_config()["tema"]["temas"]


def test_acento_por_venus(client):
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    venus = ELEMENTS[int(_chart().points["venus"] // 30) % 4]
    body = client.get(f"/profiles/{pid}/style").json()
    assert body["tema_source"] == "carta" and body["acento"] == venus
    temas = _temas()
    assert body["paleta"]["gold"] == temas[venus]["paleta"]["gold"]
    assert body["paleta"]["slate"] == temas[body["tema"]]["paleta"]["slate"]
    chosen = client.put(f"/profiles/{pid}/style", json={"tema": "clasico"}).json()
    assert chosen["paleta"] == temas["clasico"]["paleta"]


def test_modo_claro_y_vuelta(client):
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    venus = ELEMENTS[int(_chart().points["venus"] // 30) % 4]
    dark = client.get(f"/profiles/{pid}/style").json()
    assert dark["modo"] == "oscuro"
    light = client.put(f"/profiles/{pid}/style", json={"modo": "claro"}).json()
    temas = _temas()
    assert light["modo"] == "claro"
    assert light["paleta"]["slate"] == temas[light["tema"]]["paleta_claro"]["slate"]
    assert light["paleta"]["gold"] == temas[venus]["paleta_claro"]["gold"]
    assert light["tema"] == dark["tema"]  # el modo no cambia el tema
    back = client.put(f"/profiles/{pid}/style", json={"modo": "oscuro"}).json()
    assert back["paleta"] == dark["paleta"]


def _luminance(hex_color):
    def channel(v):
        v = v / 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast(a, b):
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# (texto, fondo, mínimo) con las combinaciones que usa la app.
PAIRS = [
    (("slate", "100"), ("slate", "950"), 7.0),
    (("slate", "300"), ("slate", "900"), 4.5),
    (("slate", "400"), ("slate", "950"), 4.5),
    (("violet", "400"), ("slate", "950"), 4.5),
    (("gold", "300"), ("slate", "900"), 4.5),
    (("slate", "500"), ("slate", "950"), 3.5),
    ("#ffffff", ("violet", "600"), 3.0),
]


@pytest.mark.parametrize("mode", ["paleta", "paleta_claro"])
def test_contraste_en_todos_los_temas(mode):
    for name, theme in _temas().items():
        p = theme[mode]
        for text, bg, minimum in PAIRS:
            fg = text if isinstance(text, str) else p[text[0]][text[1]]
            ratio = _contrast(fg, p[bg[0]][bg[1]])
            assert ratio >= minimum, (name, mode, text, bg, round(ratio, 2))


def test_tipografia_del_tema(client):
    pid = verified_user(client, "5491111111111")
    for theme in ELEMENTS + ["clasico"]:
        body = client.put(f"/profiles/{pid}/style", json={"tema": theme}).json()
        assert body["tipografia"] == _temas()[theme]["tipografia"]


def test_cielo_de_nacimiento(client):
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    body = client.get(f"/profiles/{pid}/style").json()
    c = _chart()
    sky = {p["punto"]: p["lon"] for p in body["cielo"]}
    for point in ("sol", "luna", "mercurio", "venus", "marte", "jupiter", "saturno", "urano", "neptuno", "pluton", "asc"):
        assert sky[point] == pytest.approx(c.points[point], abs=1e-6)
    assert body["fondo"] is True
    assert client.put(f"/profiles/{pid}/style", json={"fondo": False}).json()["fondo"] is False
    assert client.put(f"/profiles/{pid}/style", json={"fondo": True}).json()["fondo"] is True


def test_cielo_sin_hora_exacta_no_tiene_ascendente(client):
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=None)
    points = {p["punto"] for p in client.get(f"/profiles/{pid}/style").json()["cielo"]}
    assert "asc" not in points and "sol" in points


def test_modo_invalido(client):
    pid = verified_user(client, "5491111111111")
    assert client.put(f"/profiles/{pid}/style", json={"modo": "sepia"}).status_code == 422
