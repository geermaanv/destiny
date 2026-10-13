"""Spec A9: compartir mi carta con un link público, con los datos filtrados por Destiny."""

import json
from datetime import date, time

import pytest

from app.astro import ZODIAC_SIGNS
from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import openrouter, sin_key  # noqa: F401

PHONE = "5491111111111"
BIRTH = ("1990-05-20", "14:30")


def _chart(known=True):
    return compute_chart(
        date.fromisoformat(BIRTH[0]), time.fromisoformat(BIRTH[1]), known,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    )


def _share(client, pid):
    r = client.post(f"/profiles/{pid}/share")
    assert r.status_code == 200, r.text
    return r.json()["token"]


# 1
def test_crear_link_solo_la_propia_persona(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, PHONE, name="Ana")
    verified_user(b, "5492222222222")
    assert b.post(f"/profiles/{pid}/share").status_code == 403
    assert anon.post(f"/profiles/{pid}/share").status_code == 401
    token = _share(a, pid)
    assert len(token) >= 20
    assert _share(a, pid) == token


# 2
def test_pagina_publica_con_lo_necesario(client, new_client):
    pid = verified_user(client, PHONE, name="Ana", birth_date=BIRTH[0], birth_time=BIRTH[1])
    token = _share(client, pid)
    body = new_client().get(f"/public/carta/{token}").json()
    c = _chart()
    sign = lambda p: ZODIAC_SIGNS[int(c.points[p] // 30)]  # noqa: E731
    assert body["nombre"] == "Ana"
    assert body["signos"] == {"sol": sign("sol"), "luna": sign("luna"), "asc": sign("asc")}
    assert [d["clave"] for d in body["dimensiones"]] == ["identidad", "amor", "vocacion", "emociones"]
    assert all(d["sintesis"] and d["nombre"] and d["pregunta"] for d in body["dimensiones"])
    assert set(body["paleta"]) == {"slate", "violet", "gold"}
    assert body["tipografia"] and body["fondo"] == "constelacion"


# 3
def test_pagina_publica_sin_datos_sensibles(client, new_client):
    pid = verified_user(client, PHONE, name="Ana", birth_date=BIRTH[0], birth_time=BIRTH[1])
    token = _share(client, pid)
    body = new_client().get(f"/public/carta/{token}").json()
    raw = json.dumps(body, ensure_ascii=False)
    for forbidden in ("birth", "1990", "20/05", "14:30", "Buenos Aires", PHONE, "photo", "foto", "barrio", "fundamentos"):
        assert forbidden not in raw, forbidden
    c = _chart()
    for p in body["cielo"]:
        real = c.points[p["punto"]]
        assert int(p["lon"] // 30) == int(real // 30), p  # mismo signo
        assert abs(p["lon"] - real) > 1e-6  # pero no el grado exacto


# 4
def test_sin_hora_exacta_no_hay_ascendente(client, new_client):
    pid = verified_user(client, PHONE, name="Ana", birth_date=BIRTH[0], birth_time=None)
    token = _share(client, pid)
    body = new_client().get(f"/public/carta/{token}").json()
    assert "asc" not in body["signos"]
    assert all(p["punto"] not in ("asc", "mc") for p in body["cielo"])


# 5
def test_vistas(client, new_client):
    pid = verified_user(client, PHONE, name="Ana")
    token = _share(client, pid)
    viewer = new_client()
    viewer.get(f"/public/carta/{token}")
    viewer.get(f"/public/carta/{token}")
    status = client.get(f"/profiles/{pid}/share").json()
    assert status == {"activo": True, "token": token, "vistas": 2}


# 6
def test_dejar_de_compartir(client, new_client):
    pid = verified_user(client, PHONE, name="Ana")
    token = _share(client, pid)
    assert client.delete(f"/profiles/{pid}/share").status_code == 204
    assert new_client().get(f"/public/carta/{token}").status_code == 404
    assert client.get(f"/profiles/{pid}/share").json()["activo"] is False
    assert _share(client, pid) != token


# 7
def test_token_inexistente(client):
    assert client.get("/public/carta/no-existe-este-link").status_code == 404


# 8
def test_sintesis_sin_key_es_plantilla(client, new_client, sin_key):  # noqa: F811
    pid = verified_user(client, PHONE, name="Ana")
    token = _share(client, pid)
    assert new_client().get(f"/public/carta/{token}").status_code == 200


def test_sintesis_con_ia_usa_la_cache(client, new_client, openrouter):  # noqa: F811
    pid = verified_user(client, PHONE, name="Ana")
    for clave in ("identidad", "amor", "vocacion", "emociones"):
        client.get(f"/profiles/{pid}/natal/dimensions/{clave}/synthesis")
    before = len(openrouter.requests)
    token = _share(client, pid)
    body = new_client().get(f"/public/carta/{token}").json()
    assert len(openrouter.requests) == before
    assert all(d["sintesis"] == openrouter.reply for d in body["dimensiones"])
