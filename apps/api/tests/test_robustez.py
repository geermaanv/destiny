"""Revisión nocturna: casos borde que cruzan varias specs (perfil sin coordenadas, sin nombre, sin hora)."""

import pytest

from tests.helpers import verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import sin_key  # noqa: F401

SIN_COORDENADAS = {"query": "Un pueblo que no está en el buscador"}


def _endpoints(pid):
    return [
        f"/profiles/{pid}/style",
        f"/profiles/{pid}/natal/dimensions",
        f"/profiles/{pid}/natal/dimensions/identidad/synthesis",
        f"/profiles/{pid}/astrochat",
        f"/home/my-day?profile_id={pid}&date=2026-10-12",
        f"/home/my-day/detail?profile_id={pid}&date=2026-10-12",
        f"/calendar/2026/10?profile_id={pid}",
    ]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"place": SIN_COORDENADAS},
        {"place": SIN_COORDENADAS, "birth_time": None},
        {"birth_time": None},
    ],
    ids=["sin-coordenadas", "sin-coordenadas-ni-hora", "sin-hora"],
)
def test_todas_las_pantallas_responden(client, sin_key, kwargs):  # noqa: F811
    pid = verified_user(client, "5491111111111", **kwargs)
    for url in _endpoints(pid):
        r = client.get(url)
        assert r.status_code == 200, (url, r.status_code, r.text[:300])
    assert client.post(f"/profiles/{pid}/astrochat", json={"texto": "hola"}).status_code == 200
    token = client.post(f"/profiles/{pid}/share").json()["token"]
    assert client.get(f"/public/carta/{token}").status_code == 200


def test_carta_publica_sin_nombre(client, new_client):
    pid = verified_user(client, "5491111111111", name=None)
    token = client.post(f"/profiles/{pid}/share").json()["token"]
    assert new_client().get(f"/public/carta/{token}").json()["nombre"] == "Alguien"


@pytest.mark.parametrize(
    "kwargs,falta",
    [({"place": SIN_COORDENADAS}, "lugar"), ({"birth_time": None}, "hora"), ({"place": SIN_COORDENADAS, "birth_time": None}, "hora"), ({}, None)],
    ids=["falta-lugar", "falta-hora", "faltan-los-dos", "completo"],
)
def test_mi_carta_dice_que_falta_la_hora_o_el_lugar(client, kwargs, falta):
    """Bug: con hora exacta pero ciudad fuera del buscador, decía "con tu hora exacta sumamos…"."""
    pid = verified_user(client, "5491111111111", **kwargs)
    assert client.get(f"/profiles/{pid}/natal/dimensions").json()["falta"] == falta


@pytest.mark.parametrize(
    "kwargs,falta",
    [({"place": SIN_COORDENADAS}, "lugar"), ({"birth_time": None}, "hora"), ({}, None)],
    ids=["falta-lugar", "falta-hora", "completo"],
)
def test_tu_dia_completo_dice_que_falta(client, sin_key, kwargs, falta):  # noqa: F811
    pid = verified_user(client, "5491111111111", **kwargs)
    body = client.get("/home/my-day/detail", params={"profile_id": pid, "date": "2026-10-12"}).json()
    assert body["falta"] == falta


@pytest.mark.parametrize("text", ["   ", "x" * 501])
def test_nota_del_calendario_vacia_o_gigante(client, text):
    """Bug: el calendario aceptaba notas vacías o de cualquier largo."""
    pid = verified_user(client, "5491111111111")
    r = client.post("/calendar/day/2026-10-12/annotations", json={"profile_id": pid, "text": text})
    assert r.status_code == 422


def test_nota_del_calendario_se_guarda_sin_espacios_de_mas(client):
    pid = verified_user(client, "5491111111111")
    r = client.post("/calendar/day/2026-10-12/annotations", json={"profile_id": pid, "text": "  Fui al cine  "})
    assert r.status_code in (200, 201) and r.json()["text"] == "Fui al cine"
