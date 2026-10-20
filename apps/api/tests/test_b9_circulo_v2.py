"""Spec B9: Círculo v2 — número global (promedio de los sistemas, provisorio, ADR 0014), ejes por sistema y distancia."""

import json

from tests.helpers import complete_personality
from tests.test_a10_verificacion_opcional import active_user

OBELISCO = {"query": "Buenos Aires, Argentina", "lat": -34.6037, "lon": -58.3816}
PALERMO = {"query": "Palermo, Buenos Aires, Argentina", "lat": -34.5875, "lon": -58.4250}  # ~4 km
ROSARIO = {"query": "Rosario, Santa Fe, Argentina", "lat": -32.9468, "lon": -60.6393}  # ~280 km
AXES = ["atraccion", "afecto", "comunicacion", "compromiso"]


def discover(client, viewer, **params):
    r = client.get("/discover", params={"viewer_id": viewer, **params})
    assert r.status_code == 200, r.text
    return {x["profile_id"]: x for x in r.json()}


def live(client, pid, place):
    r = client.post(f"/profiles/{pid}/residence", json=place)
    assert r.status_code == 200, r.text


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values))


# 1
def test_global_con_los_dos_sistemas(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana", birth_date="1992-08-03")
    complete_personality(a, viewer, choice=1)
    complete_personality(b, otra, choice=2)
    c = discover(a, viewer, context="laboral")[otra]
    astro, test = c["systems"]["astrologia"], c["systems"]["personalidad"]
    assert test is not None
    assert c["global_pct"] == mean([astro["total"], c["personality"]["total"]]) == c["compatibility_pct"]
    for axis in AXES:
        assert c["axes_global"][axis] == mean([astro["axes"][axis], test["axes"][axis]])


# 2
def test_sin_test_es_solo_astrologia(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana")
    complete_personality(a, viewer)
    c = discover(a, viewer)[otra]
    assert c["systems"]["personalidad"] is None
    assert c["global_pct"] == c["systems"]["astrologia"]["total"]
    assert c["axes_global"] == c["systems"]["astrologia"]["axes"]


# 3
def test_los_pesos_de_pablo_siguen_valiendo(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana", birth_date="1992-08-03")
    complete_personality(a, viewer, choice=1)
    complete_personality(b, otra, choice=3)
    for context in ["pareja", "amistad", "laboral", "ocasional"]:
        c = discover(a, viewer, context=context)[otra]
        assert c["systems"]["astrologia"]["total"] == c["astrology_pct"]
        assert c["systems"]["personalidad"]["total"] == round(c["personality"]["total"])
        assert c["global_pct"] == mean([c["astrology_pct"], c["personality"]["total"]])


# 4
def test_orden_y_minimo_por_global(new_client):
    a, b, c, d = new_client(), new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    active_user(b, name="Uno", birth_date="1985-01-15")
    active_user(c, name="Dos", birth_date="1992-08-03")
    active_user(d, name="Tres", birth_date="1978-06-21")
    r = a.get("/discover", params={"viewer_id": viewer}).json()
    pcts = [x["global_pct"] for x in r]
    assert pcts == sorted(pcts, reverse=True)
    corte = pcts[1]
    assert all(x["global_pct"] >= corte for x in discover(a, viewer, min_pct=corte).values())


# 5
def test_elegir_sistemas(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    con_test = active_user(b, name="Tomi")
    sin_test = active_user(c, name="Nico")
    r = a.get("/discover", params={"viewer_id": viewer, "sistemas": "personalidad"})
    assert r.status_code == 409
    assert a.get("/discover", params={"viewer_id": viewer, "sistemas": ""}).status_code == 422
    complete_personality(a, viewer)
    complete_personality(b, con_test)
    solo_astro = discover(a, viewer, sistemas="astrologia")
    assert solo_astro[con_test]["global_pct"] == solo_astro[con_test]["systems"]["astrologia"]["total"]
    assert solo_astro[con_test]["systems"]["personalidad"] is None
    solo_test = discover(a, viewer, sistemas="personalidad")
    assert sin_test not in solo_test
    assert solo_test[con_test]["global_pct"] == solo_test[con_test]["systems"]["personalidad"]["total"]


# 6
def test_guardar_donde_vivo(client):
    pid = active_user(client)
    live(client, pid, PALERMO)
    me = client.get(f"/profiles/{pid}").json()
    assert me["residence_label"] == PALERMO["query"]
    assert me["residence_lat"] == PALERMO["lat"]
    r = client.post(f"/profiles/{pid}/residence", json={"query": "Algún lugar"})
    assert r.status_code == 422


# 7
def test_distancia(new_client):
    a, b, c, d = new_client(), new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    cerca = active_user(b, name="Cami")
    lejos = active_user(c, name="Rami")
    sin_lugar = active_user(d, name="Nico")
    r = a.get("/discover", params={"viewer_id": viewer, "max_km": 25})
    assert r.status_code == 409  # quien busca no cargó dónde vive
    live(a, viewer, OBELISCO)
    live(b, cerca, PALERMO)
    live(c, lejos, ROSARIO)
    todos = discover(a, viewer)
    assert 3 <= todos[cerca]["distance_km"] <= 5
    assert 250 <= todos[lejos]["distance_km"] <= 320
    assert todos[sin_lugar]["distance_km"] is None
    cerca_solo = discover(a, viewer, max_km=25)
    assert cerca in cerca_solo and lejos not in cerca_solo and sin_lugar not in cerca_solo


# 8
def test_no_se_expone_donde_vive_otra_persona(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Cami")
    live(a, viewer, OBELISCO)
    live(b, otra, PALERMO)
    texto = json.dumps(a.get("/discover", params={"viewer_id": viewer}).json())
    assert "Palermo" not in texto and "-34.5875" not in texto and "residence" not in texto
