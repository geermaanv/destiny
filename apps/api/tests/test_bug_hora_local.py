"""Bug de la hora (spec A1, corrección 2026-10-12): la hora de nacimiento es hora local del lugar."""

from datetime import date, time

from app.aspects import angle_between, classify_aspect
from app.astro import moon_longitude
from app.synastry.chart import compute_chart
from tests.helpers import create_profile, verified_user

TOKIO = {"query": "Tokio, Japón", "lat": 35.6895, "lon": 139.6917, "timezone": "Asia/Tokyo"}


def test_signo_solar_con_hora_local(client):
    # 21/5/1990 06:00 en Buenos Aires = 09:00 UTC: el Sol ya entró en Géminis (como UTC daba Tauro).
    pid = create_profile(client, birth_date="1990-05-21", birth_time="06:00")
    assert client.get(f"/profiles/{pid}").json()["sun_sign"] == "Géminis"


def test_descubrir_muestra_el_signo_correcto(new_client):
    a, b = new_client(), new_client()
    verified_user(a, "5491111111111", name="Ana", birth_date="1990-05-21", birth_time="06:00")
    yo = verified_user(b, "5492222222222", name="Beto")
    assert b.get("/discover", params={"viewer_id": yo}).json()[0]["sun_sign"] == "Géminis"


def test_calendario_usa_el_sol_natal_con_hora_local(client):
    # Tokio (+9): la diferencia con UTC mueve el Sol natal ~0,4°, suficiente para cambiar días límite.
    pid = verified_user(client, "5491111111111", birth_date="1988-03-20", birth_time="07:30", place=TOKIO)
    sol = compute_chart(date(1988, 3, 20), time(7, 30), True, TOKIO["lat"], TOKIO["lon"], TOKIO["timezone"]).points["sol"]
    dias = client.get("/calendar/2026/10", params={"profile_id": pid}).json()
    for d in dias:
        esperado = classify_aspect(angle_between(moon_longitude(date.fromisoformat(d["date"])), sol))["is_major"]
        assert d["has_key_transit"] == esperado, d["date"]


def test_revelacion_de_la_invitacion_usa_el_motor_de_sinastria(new_client):
    from app.models import Profile
    from app.database import SessionLocal
    from app.synastry import profile_synastry

    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana")
    ref = a.post("/invitations", json={"inviter_id": ana, "friend_name": "Juan", "friend_sun_sign": "Leo"}).json()["ref_id"]
    juan = verified_user(b, "5492222222222", name="Juan", birth_date="1991-08-10", birth_time="08:00")
    reveal = b.get(f"/invitations/{ref}/reveal", params={"invitee_id": juan}).json()
    with SessionLocal() as db:
        esperado = profile_synastry(db.get(Profile, ana), db.get(Profile, juan), "pareja")["total"]
    assert reveal["percentage"] == esperado


def test_ya_no_queda_el_calculo_con_hora_utc():
    import importlib.util

    assert importlib.util.find_spec("app.compatibility") is None
