"""Spec X2 v1: estilo de redacción según la carta (Mercurio, Luna, modalidad dominante)."""

import json
from datetime import date, time

import pytest

from app.astro import ZODIAC_SIGNS
from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import openrouter  # noqa: F401

ELEMENTS = ["fuego", "tierra", "aire", "agua"]
MODALITIES = ["cardinal", "fijo", "mutable"]
REGISTRO = {"fuego": "directo", "tierra": "practico", "aire": "analitico", "agua": "intuitivo"}
TONO = {"fuego": "liviano", "aire": "liviano", "tierra": "contenedor", "agua": "contenedor"}
FORMATO = {"cardinal": "acciones", "fijo": "profundidad", "mutable": "opciones"}
WEIGHTS = {"sol": 3, "luna": 3, "asc": 2, "mercurio": 1, "venus": 1, "marte": 1}


def _chart(birth_date, birth_time):
    return compute_chart(
        date.fromisoformat(birth_date), time.fromisoformat(birth_time), True,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    )


def _expected(birth_date, birth_time):
    c = _chart(birth_date, birth_time)
    sign = lambda p: int(c.points[p] // 30)  # noqa: E731
    totals = [0] * 3
    for point, w in WEIGHTS.items():
        totals[sign(point) % 3] += w
    best = max(totals)
    tied = [i for i, t in enumerate(totals) if t == best]
    modality = MODALITIES[tied[0]] if len(tied) == 1 else MODALITIES[sign("mercurio") % 3]
    return {
        "registro": REGISTRO[ELEMENTS[sign("mercurio") % 4]],
        "tono": TONO[ELEMENTS[sign("luna") % 4]],
        "formato": FORMATO[modality],
        "mercurio": ZODIAC_SIGNS[sign("mercurio")],
    }


@pytest.mark.parametrize("birth", [("1990-05-20", "14:30"), ("1985-11-03", "21:45"), ("1978-02-11", "06:10"), ("2001-08-30", "17:00")])
def test_estilo_sale_de_la_carta(client, birth):
    pid = verified_user(client, "5491111111111", birth_date=birth[0], birth_time=birth[1])
    style = client.get(f"/profiles/{pid}/style").json()
    expected = _expected(*birth)
    assert (style["registro"], style["tono"], style["formato"]) == (expected["registro"], expected["tono"], expected["formato"])
    assert style["source"] == "carta" and style["registro_carta"] == expected["registro"]


def test_el_porque_menciona_planeta_signo_y_elemento(client):
    pid = verified_user(client, "5491111111111", birth_date="1990-05-20", birth_time="14:30")
    style = client.get(f"/profiles/{pid}/style").json()
    expected = _expected("1990-05-20", "14:30")
    assert "Mercurio" in style["por_que"] and expected["mercurio"] in style["por_que"]


def test_elegir_otro_registro_y_volver_a_la_carta(client):
    pid = verified_user(client, "5491111111111")
    carta = client.get(f"/profiles/{pid}/style").json()["registro"]
    otro = "analitico" if carta != "analitico" else "practico"
    r = client.put(f"/profiles/{pid}/style", json={"registro": otro})
    assert r.status_code == 200 and r.json()["registro"] == otro and r.json()["source"] == "elegido"
    back = client.put(f"/profiles/{pid}/style", json={"registro": None}).json()
    assert back["registro"] == carta and back["source"] == "carta"


def test_registro_invalido_y_estilo_de_otro(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    assert a.put(f"/profiles/{pid}/style", json={"registro": "poetico"}).status_code == 422
    assert b.get(f"/profiles/{pid}/style").status_code == 403
    assert anon.get(f"/profiles/{pid}/style").status_code == 401


def test_cambiar_el_mapeo_en_la_configuracion(client, monkeypatch):
    from app.personalization.style import load_config

    pid = verified_user(client, "5491111111111", birth_date="1990-05-20", birth_time="14:30")
    elemento = ELEMENTS[int(_chart("1990-05-20", "14:30").points["mercurio"] // 30) % 4]
    otro = "analitico" if REGISTRO[elemento] != "analitico" else "practico"
    monkeypatch.setitem(load_config()["registro"]["por_elemento"], elemento, otro)
    assert client.get(f"/profiles/{pid}/style").json()["registro"] == otro


def _explain(client, viewer, candidate):
    return client.get(f"/discover/{candidate}/explanation", params={"viewer_id": viewer, "context": "pareja"})


def test_la_explicacion_usa_el_estilo_de_quien_lee(openrouter, new_client):  # noqa: F811
    from app.personalization.style import load_config

    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana")
    beto = verified_user(b, "5492222222222", name="Beto")
    b.put(f"/profiles/{beto}/style", json={"registro": "analitico"})
    _explain(b, beto, ana)
    system = openrouter.requests[0]["body"]["messages"][0]["content"]
    assert load_config()["registro"]["estilos"]["analitico"]["instruccion"] in system


def test_cambiar_de_registro_vuelve_a_redactar(openrouter, new_client):  # noqa: F811
    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana")
    beto = verified_user(b, "5492222222222", name="Beto")
    _explain(b, beto, ana)
    _explain(b, beto, ana)
    assert len(openrouter.requests) == 1
    b.put(f"/profiles/{beto}/style", json={"registro": "intuitivo"})
    _explain(b, beto, ana)
    assert len(openrouter.requests) == 2


def test_biblioteca_de_tu_dia_por_registro():
    from app.content.transits import ASPECTS, load_library

    lib = load_library()
    for registro in REGISTRO.values():
        for aspect in ASPECTS:
            for sign in ZODIAC_SIGNS:
                entry = lib["por_registro"][registro][aspect][sign]
                assert entry["titulo"].strip() and entry["texto"].strip() and len(entry["texto"]) <= 280


def test_tu_dia_usa_el_registro_de_la_persona(client):
    from app.content.transits import load_library

    pid = verified_user(client, "5491111111111")
    client.put(f"/profiles/{pid}/style", json={"registro": "practico"})
    day = client.get("/home/my-day", params={"profile_id": pid, "date": "2026-10-12"}).json()
    entry = load_library()["por_registro"]["practico"][day["aspect"]][day["moon_sign"]]
    assert (day["title"], day["text"]) == (entry["titulo"], entry["texto"])
