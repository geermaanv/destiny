"""Spec U2: Indagar con un día del calendario y calendario sin notas."""

import json

import pytest

from tests.helpers import verified_user
from tests.test_x1_redaccion_con_ia import openrouter  # noqa: F401


def _facts(fake) -> dict:
    """Los datos que vio la IA, del prompt de sistema del último pedido."""
    system = fake.requests[-1]["body"]["messages"][0]["content"]
    return json.loads(system.split("Datos de su carta (calculados por Destiny): ", 1)[1])


# 1
def test_las_notas_ya_no_existen(client):
    pid = verified_user(client, "5491111111111")
    r = client.post("/calendar/day/2026-10-12/annotations", json={"profile_id": pid, "text": "Cena"})
    assert r.status_code in (404, 405)
    dia = client.get(f"/calendar/day/2026-10-12?profile_id={pid}").json()
    assert "annotations" not in dia
    eventos = client.get(f"/calendar/upcoming?profile_id={pid}&from=2026-10-12").json()
    assert all("has_notes" not in e for e in eventos)


# 2
def test_preguntar_por_un_dia(client, openrouter):  # noqa: F811
    pid = verified_user(client, "5491111111111")
    r = client.post(f"/profiles/{pid}/astrochat", json={"texto": "¿Qué significa para mí el 23 de octubre?", "dia": "2026-10-23"})
    assert r.status_code == 200, r.text
    dia = _facts(openrouter)["dia_consultado"]
    assert dia["fecha"] == "2026-10-23"
    assert "transitos" in dia and "luna" in dia and "areas" in dia


# 3
def test_sin_dia_no_hay_dia_consultado(client, openrouter):  # noqa: F811
    pid = verified_user(client, "5491111111111")
    client.post(f"/profiles/{pid}/astrochat", json={"texto": "¿Cómo viene mi semana?"})
    assert "dia_consultado" not in _facts(openrouter)


# 4
@pytest.mark.parametrize("dia", ["mañana", "2026-13-40"])
def test_dia_invalido(client, dia):
    pid = verified_user(client, "5491111111111")
    r = client.post(f"/profiles/{pid}/astrochat", json={"texto": "Hola", "dia": dia})
    assert r.status_code == 422
