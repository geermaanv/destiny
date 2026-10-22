"""Spec P2: no deducir respuestas del test ni ubicación, y el bloqueo oculta (hallazgos del agente breaker)."""

import pytest

from tests.helpers import complete_personality, verified_user
from tests.test_a10_verificacion_opcional import active_user

OBELISCO = {"query": "Buenos Aires", "lat": -34.6037, "lon": -58.3816}
PALERMO = {"query": "Palermo", "lat": -34.5875, "lon": -58.4250}
ROSARIO = {"query": "Rosario", "lat": -32.9468, "lon": -60.6393}


def found(client, viewer, **params):
    return {x["profile_id"]: x for x in client.get("/discover", params={"viewer_id": viewer, **params}).json()}


# 1
def test_test_incompleto_no_se_muestra(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana")
    complete_personality(b, otra)
    a.put(f"/profiles/{viewer}/personality", json={"answers": {"E1.01": [2]}})
    assert found(a, viewer)[otra]["personality"] is None
    m = a.post("/matches", json={"profile_a_id": viewer, "profile_b_id": otra}).json()
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": otra})
    assert a.get(f"/matches/{m['id']}/compatibility").json()["personality"] is None


# 2
def test_ejes_del_test_en_multiplos_de_5(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana", birth_date="1992-08-03")
    complete_personality(a, viewer, choice=1)
    complete_personality(b, otra, choice=3)
    c = found(a, viewer)[otra]
    for value in [*c["personality"]["axes"].values(), *c["systems"]["personalidad"]["axes"].values()]:
        assert value is None or value % 5 == 0


# 3
def test_limite_de_cambios_con_el_test_completo(client):
    pid = active_user(client)
    complete_personality(client, pid, choice=2)
    from app.personality.engine import load_config

    ids = [q["id"] for q in load_config()["questions"]][:11]
    for qid in ids[:10]:
        assert client.put(f"/profiles/{pid}/personality", json={"answers": {qid: [1]}}).status_code == 200
    assert client.put(f"/profiles/{pid}/personality", json={"answers": {ids[10]: [1]}}).status_code == 429


# 4
def test_distancia_en_franjas(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    cerca = active_user(b, name="Cami")
    lejos = active_user(c, name="Rami")
    for client, pid, place in [(a, viewer, OBELISCO), (b, cerca, PALERMO), (c, lejos, ROSARIO)]:
        client.post(f"/profiles/{pid}/residence", json=place)
    todos = found(a, viewer)
    assert todos[cerca]["distance_km"] == 5 and todos[lejos]["distance_km"] == 300


# 5
@pytest.mark.parametrize("km,code", [(5, 200), (25, 200), (100, 200), (7, 422), (1, 422)])
def test_filtro_de_distancia(client, km, code):
    pid = active_user(client)
    client.post(f"/profiles/{pid}/residence", json=OBELISCO)
    assert client.get("/discover", params={"viewer_id": pid, "max_km": km}).status_code == code


# 6
def test_donde_vivis_redondeado_y_limitado(client):
    pid = active_user(client)
    r = client.post(f"/profiles/{pid}/residence", json={"query": "x", "lat": -34.603722, "lon": -58.381592})
    assert r.json()["residence_lat"] == -34.6 and r.json()["residence_lon"] == -58.38
    # Spec R3 (antes 3 por día): después de la primera carga, un cambio cada 30 días.
    assert client.post(f"/profiles/{pid}/residence", json=PALERMO).status_code == 200
    assert client.post(f"/profiles/{pid}/residence", json=ROSARIO).status_code == 429


# 7
def test_el_bloqueo_oculta_en_las_dos_direcciones(new_client):
    a, b = new_client(), new_client()
    pa = verified_user(a, "5491111111111", name="Ana")
    pb = verified_user(b, "5492222222222", name="Beto")
    m = a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb}).json()
    b.post(f"/matches/{m['id']}/block", json={"profile_id": pb})
    assert pb not in found(a, pa) and pb not in found(a, pa, q="beto")
    assert pa not in found(b, pb) and pa not in found(b, pb, q="ana")
    assert a.get(f"/discover/{pb}/explanation", params={"viewer_id": pa}).status_code == 404


# 8
def test_compatibilidad_de_un_chat_bloqueado(new_client):
    a, b = new_client(), new_client()
    pa = verified_user(a, "5491111111111", name="Ana")
    pb = verified_user(b, "5492222222222", name="Beto")
    m = a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb}).json()
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": pb})
    b.post(f"/matches/{m['id']}/block", json={"profile_id": pb})
    assert a.get(f"/matches/{m['id']}/compatibility").status_code == 409
