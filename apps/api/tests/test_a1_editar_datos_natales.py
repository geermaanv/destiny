"""Spec A1 v2: editar los datos de nacimiento desde Mi perfil."""

from datetime import date

from tests.helpers import BUENOS_AIRES, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401  (reusa el OpenRouter simulado)
from tests.test_x1_redaccion_con_ia import openrouter  # noqa: F401

ROSARIO = {"query": "Rosario, Provincia de Santa Fe, Argentina", "lat": -32.9468, "lon": -60.6393, "timezone": "America/Argentina/Cordoba"}


def _edit(client, pid, **payload):
    payload.setdefault("birth_place", ROSARIO)
    return client.post(f"/profiles/{pid}/birth-data", json=payload)


def test_editar_con_la_propia_sesion(client):
    pid = verified_user(client, "5491111111111", birth_date="1990-05-20")
    antes = client.get(f"/profiles/{pid}").json()
    r = _edit(client, pid, birth_date="1985-11-03", birth_time="21:45")
    assert r.status_code == 200
    despues = client.get(f"/profiles/{pid}").json()
    assert despues["birth_date"] == "1985-11-03" and despues["birth_time"] == "21:45:00"
    assert despues["birth_place_lat"] == ROSARIO["lat"] and despues["birth_place_timezone"] == ROSARIO["timezone"]
    assert antes["sun_sign"] == "Tauro" and despues["sun_sign"] == "Escorpio"


def test_editar_datos_de_otro(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    assert _edit(b, pid, birth_date="1985-11-03").status_code == 403
    assert _edit(anon, pid, birth_date="1985-11-03").status_code == 401


def test_editar_con_fecha_de_menor(client):
    pid = verified_user(client, "5491111111111")
    menor = date(date.today().year - 16, 1, 1).isoformat()
    assert _edit(client, pid, birth_date=menor).status_code == 422


def test_la_explicacion_se_vuelve_a_redactar_al_cambiar_la_carta(openrouter, new_client):  # noqa: F811
    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana", birth_date="1990-05-20")
    beto = verified_user(b, "5492222222222", name="Beto", birth_date="1985-11-03")
    params = {"viewer_id": beto, "context": "pareja"}
    b.get(f"/discover/{ana}/explanation", params=params)
    b.get(f"/discover/{ana}/explanation", params=params)
    assert len(openrouter.requests) == 1
    _edit(a, ana, birth_date="1992-02-14", birth_place=BUENOS_AIRES)
    b.get(f"/discover/{ana}/explanation", params=params)
    assert len(openrouter.requests) == 2
