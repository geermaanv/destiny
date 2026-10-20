"""Spec B11: cada día del calendario con su tipo (fluye, desafía, intenso, tranquilo)."""

from tests.helpers import verified_user

TIPOS = {
    "trígono": "fluye",
    "sextil": "fluye",
    "cuadratura": "desafia",
    "oposición": "desafia",
    "conjunción": "intenso",
}


# 1
def test_tipo_de_cada_dia_del_mes(client):
    from datetime import date

    from app.database import SessionLocal
    from app.models import Profile
    from app.transits import day_transit

    pid = verified_user(client, "5491111111111")
    dias = client.get("/calendar/2026/10", params={"profile_id": pid}).json()
    assert len(dias) == 31
    with SessionLocal() as db:
        profile = db.get(Profile, pid)
        for d in dias:
            aspect = day_transit(profile, date.fromisoformat(d["date"]))["aspect"]
            assert d["tipo"] == TIPOS.get(aspect, "tranquilo")
            assert (d["tipo"] != "tranquilo") == d["has_key_transit"]
    assert {d["tipo"] for d in dias} - {"tranquilo"}, "un mes tiene días con tránsitos"


# 2
def test_eventos_proximos_traen_su_tipo(client):
    pid = verified_user(client, "5491111111111")
    eventos = client.get("/calendar/upcoming", params={"profile_id": pid, "from": "2026-10-01"}).json()
    assert eventos
    for e in eventos:
        assert e["tipo"] == TIPOS[e["aspect"]]
