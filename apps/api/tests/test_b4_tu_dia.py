"""Spec B4 v2: "Tu día" — tránsito personal del día en Inicio, con textos de una biblioteca fija."""

from datetime import date, time

import pytest

from app.aspects import angle_between, classify_aspect
from app.astro import ZODIAC_SIGNS, moon_longitude, zodiac_sign
from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user

ASPECTS = ["conjunción", "sextil", "cuadratura", "trígono", "oposición", "sin aspecto mayor"]
DAY = "2026-10-12"


def test_biblioteca_completa():
    from app.content.transits import load_library

    lib = load_library()
    for aspect in ASPECTS:
        for sign in ZODIAC_SIGNS:
            entry = lib["textos"][aspect][sign]
            assert entry["titulo"].strip() and entry["texto"].strip(), (aspect, sign)
            assert len(entry["texto"]) <= 280, (aspect, sign)


def _expected(birth_date="1990-05-21", birth_time="06:00"):
    sol = compute_chart(
        date.fromisoformat(birth_date), time.fromisoformat(birth_time), True,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    ).points["sol"]
    moon = moon_longitude(date.fromisoformat(DAY))
    return classify_aspect(angle_between(moon, sol))["aspect"], zodiac_sign(moon)


def test_tu_dia_usa_el_sol_natal_y_la_biblioteca(client):
    from app.content.transits import load_library

    pid = verified_user(client, "5491111111111", birth_date="1990-05-21", birth_time="06:00")
    r = client.get("/home/my-day", params={"profile_id": pid, "date": DAY})
    assert r.status_code == 200
    body = r.json()
    aspect, moon_sign = _expected()
    assert (body["aspect"], body["moon_sign"], body["date"]) == (aspect, moon_sign, DAY)
    # Spec X2: el texto sale de la versión en el registro de la persona (lo decide su carta).
    registro = client.get(f"/profiles/{pid}/style").json()["registro"]
    entry = load_library()["por_registro"][registro][aspect][moon_sign]
    assert (body["title"], body["text"]) == (entry["titulo"], entry["texto"])
    assert body["reviewed"] is False


def test_mismo_transito_que_el_calendario(client):
    pid = verified_user(client, "5491111111111")
    mi_dia = client.get("/home/my-day", params={"profile_id": pid, "date": DAY}).json()
    calendario = client.get(f"/calendar/day/{DAY}", params={"profile_id": pid}).json()
    assert mi_dia["aspect"] == calendario["transits"][0]["aspect"]


def test_sin_sesion_o_de_otro(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    assert anon.get("/home/my-day", params={"profile_id": pid, "date": DAY}).status_code == 401
    assert b.get("/home/my-day", params={"profile_id": pid, "date": DAY}).status_code == 403


def test_no_llama_a_la_ia(client, monkeypatch):
    from app import llm

    def boom(*args, **kwargs):
        raise AssertionError("Tu día no debe llamar a la IA")

    monkeypatch.setattr(llm, "complete", boom)
    pid = verified_user(client, "5491111111111")
    assert client.get("/home/my-day", params={"profile_id": pid, "date": DAY}).status_code == 200


def test_si_falta_el_texto_usa_el_generico(client, monkeypatch):
    from app.content.transits import load_library
    from app.transits import TRANSIT_TEXT

    pid = verified_user(client, "5491111111111", birth_date="1990-05-21", birth_time="06:00")
    aspect, moon_sign = _expected()
    lib = load_library()
    monkeypatch.delitem(lib["textos"][aspect], moon_sign)
    body = client.get("/home/my-day", params={"profile_id": pid, "date": DAY}).json()
    generic = TRANSIT_TEXT.get(aspect)
    if generic:
        assert (body["title"], body["text"]) == generic
    else:
        assert body["title"] and body["text"]


def test_clima_del_dia_usa_la_fecha_local_que_manda_la_app(client):
    """El encabezado de Hoy y "Tu día" tienen que hablar de la misma fecha (la local de la persona)."""
    from datetime import date as d

    from app.astro import astro_weather_for_date

    r = client.get("/home/today", params={"date": "2026-10-12"})
    assert r.status_code == 200
    assert r.json() == {"astro_weather": astro_weather_for_date(d(2026, 10, 12)), "date": "2026-10-12"}
