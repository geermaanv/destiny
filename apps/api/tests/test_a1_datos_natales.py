"""Spec A1-datos-natales: fecha, lugar (geocodificado) y hora de nacimiento."""

from datetime import date

from tests.helpers import BUENOS_AIRES


def _birth(client, **payload):
    profile_id = client.post("/profiles").json()["id"]
    payload.setdefault("birth_place", BUENOS_AIRES)
    return client.post(f"/profiles/{profile_id}/birth-data", json=payload)


def test_hora_exacta_se_guarda_tal_cual(client):
    r = _birth(client, birth_date="1990-05-20", birth_time="21:45")
    assert r.status_code == 200
    assert r.json()["birth_time"] == "21:45:00"
    assert r.json()["birth_time_estimated"] is False


def test_sin_hora_se_usan_las_12_y_queda_estimada(client):
    r = _birth(client, birth_date="1990-05-20")
    assert r.json()["birth_time"] == "12:00:00"
    assert r.json()["birth_time_estimated"] is True


def test_franja_del_dia_usa_el_punto_medio(client):
    esperados = {"madrugada": "03:00:00", "manana": "09:00:00", "tarde": "15:00:00", "noche": "21:00:00"}
    for franja, hora in esperados.items():
        r = _birth(client, birth_date="1990-05-20", birth_time_period=franja)
        assert r.json()["birth_time"] == hora, franja
        assert r.json()["birth_time_estimated"] is True


def test_hora_exacta_gana_sobre_la_franja(client):
    r = _birth(client, birth_date="1990-05-20", birth_time="07:15", birth_time_period="noche")
    assert r.json()["birth_time"] == "07:15:00"
    assert r.json()["birth_time_estimated"] is False


def test_menores_de_18_se_rechazan(client):
    hoy = date.today()
    menor = date(hoy.year - 17, hoy.month, 1).isoformat()
    assert _birth(client, birth_date=menor).status_code == 422


def test_con_18_anios_se_acepta(client):
    hoy = date.today()
    adulto = date(hoy.year - 18, 1, 1).isoformat()
    assert _birth(client, birth_date=adulto).status_code == 200


def test_se_guardan_coordenadas_y_zona_horaria(client):
    r = _birth(client, birth_date="1990-05-20")
    body = r.json()
    assert body["birth_place_lat"] == BUENOS_AIRES["lat"]
    assert body["birth_place_timezone"] == "America/Argentina/Buenos_Aires"


def test_busqueda_de_ciudad_devuelve_coordenadas_y_zona_horaria(client):
    r = client.get("/geocoding/search", params={"q": "Rosario"})
    assert r.status_code == 200
    place = r.json()[0]
    assert place["label"].startswith("Rosario")
    assert place["timezone"] == "America/Argentina/Cordoba"


def test_busqueda_de_ciudad_pide_al_menos_2_letras(client):
    assert client.get("/geocoding/search", params={"q": "x"}).status_code == 422


def test_alias_caba_se_traduce_a_buenos_aires():
    from app.geocoding import ALIASES, _normalize

    for alias in ("CABA", "Capital Federal", "Bs. As."):
        assert ALIASES.get(_normalize(alias)) == "Buenos Aires", alias
