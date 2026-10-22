"""Spec R1: datos inválidos rechazados y sin errores 500 (hallazgos del agente breaker)."""

import threading

import pytest

from tests.helpers import BUENOS_AIRES, png, verified_user
from tests.test_a10_verificacion_opcional import active_user


def birth(client, pid, **place):
    return client.post(
        f"/profiles/{pid}/birth-data",
        json={"birth_date": place.pop("birth_date", "1990-05-20"), "birth_time": "10:00", "birth_place": {**BUENOS_AIRES, **place}},
    )


# 1
@pytest.mark.parametrize(
    "bad",
    [
        {"timezone": "Mars/Olympus"},
        {"lat": 95},
        {"lon": -200},
        {"query": "x" * 201},
        {"birth_date": "1800-01-01"},
    ],
    ids=["zona", "lat", "lon", "lugar", "anio"],
)
def test_datos_de_nacimiento_invalidos(client, bad):
    pid = client.post("/profiles").json()["id"]
    assert birth(client, pid, **bad).status_code == 422


def test_nan_en_datos_de_nacimiento(client):
    pid = client.post("/profiles").json()["id"]
    body = '{"birth_date":"1990-05-20","birth_place":{"query":"x","lat":NaN,"lon":-58,"timezone":"America/Argentina/Buenos_Aires"}}'
    r = client.post(f"/profiles/{pid}/birth-data", content=body, headers={"Content-Type": "application/json"})
    assert r.status_code == 422


# 2
def test_un_candidato_roto_no_tira_descubrir(new_client):
    from app.database import SessionLocal
    from app.models import Profile

    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    roto = active_user(b, name="Roto")
    sano = active_user(c, name="Sano")
    with SessionLocal() as db:  # datos que quedaron mal de antes de la validación
        db.get(Profile, roto).birth_place_timezone = "Mars/Olympus"
        db.commit()
    r = a.get("/discover", params={"viewer_id": viewer})
    assert r.status_code == 200
    ids = [x["profile_id"] for x in r.json()]
    assert sano in ids and roto not in ids


# 3
def test_fechas_fuera_de_rango(client):
    pid = verified_user(client, "5491111111111")
    for url in [
        "/calendar/2026/13",
        "/calendar/2026/0",
        "/calendar/10000/1",
        f"/calendar/upcoming?profile_id={pid}&from=9999-12-31",
        f"/home/my-day?profile_id={pid}&date=0001-01-01",
        f"/home/my-day/detail?profile_id={pid}&date=0001-01-01",
        "/home/today?date=0001-01-01",
    ]:
        r = client.get(url, params={"profile_id": pid} if url.startswith("/calendar/2") or url.startswith("/calendar/1") else None)
        assert r.status_code == 422, url
    r = client.post(f"/profiles/{pid}/astrochat", json={"texto": "x", "dia": "0001-01-01"})
    assert r.status_code == 422


# 4
def test_textos_con_nulos_o_invisibles(client):
    pid = active_user(client)
    r = client.post(f"/profiles/{pid}/basic-info", json={"display_name": "An\x00a"})
    assert r.status_code == 200 and r.json()["display_name"] == "Ana"
    assert client.post(f"/profiles/{pid}/basic-info", json={"display_name": "​​"}).status_code == 422
    r = client.post("/invitations", json={"inviter_id": pid, "friend_name": "Ju\x00an"})
    assert r.status_code == 201 and "¡Hola Juan!" in r.json()["message"]


def test_mensaje_de_chat_invisible(new_client):
    a, b = new_client(), new_client()
    pa = verified_user(a, "5491111111111", name="Ana")
    pb = verified_user(b, "5492222222222", name="Beto")
    m = a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb}).json()
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": pb})
    assert a.post(f"/chats/{m['id']}/messages", json={"profile_id": pa, "text": "​"}).status_code == 422
    assert a.post(f"/chats/{m['id']}/messages", json={"profile_id": pa, "text": "ho\x00la"}).json()["text"] == "hola"


# 5
def test_residencia_nan(client):
    pid = active_user(client)
    r = client.post(
        f"/profiles/{pid}/residence", content='{"query":"x","lat":NaN,"lon":1}', headers={"Content-Type": "application/json"}
    )
    assert r.status_code == 422


# 6
def test_foto_que_no_es_imagen(client):
    pid = active_user(client, photo=False)
    falsa = client.post(f"/profiles/{pid}/photos", files={"photo": ("x.png", b"<html><script>1</script></html>", "image/png")})
    vacia = client.post(f"/profiles/{pid}/photos", files={"photo": ("x.png", b"", "image/png")})
    assert falsa.status_code == 415 and vacia.status_code == 415
    ok = client.post(f"/profiles/{pid}/photos", files={"photo": ("p.png", png(), "image/png")})
    assert client.get(ok.json()["photos"][0]["url"]).headers["x-content-type-options"] == "nosniff"


# 7
def test_aceptar_invitacion_dos_veces_a_la_vez(new_client):
    a, b = new_client(), new_client()
    pablo = verified_user(a, "5491111111111", name="Pablo")
    ref = a.post("/invitations", json={"inviter_id": pablo, "friend_name": "Mavi"}).json()["ref_id"]
    active_user(b, name="Mavi")
    codes = []
    threads = [threading.Thread(target=lambda: codes.append(b.post(f"/invitations/{ref}/accept").status_code)) for _ in range(4)]
    [t.start() for t in threads]
    [t.join() for t in threads]
    assert 500 not in codes


# 8
def test_webhook_con_otra_forma(client):
    from tests.helpers import APP_SECRET

    import hashlib
    import hmac
    import json

    for payload in [{"entry": "x"}, [1, 2], {"entry": [{"changes": "x"}]}]:
        body = json.dumps(payload).encode()
        sig = "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
        r = client.post("/webhooks/whatsapp", content=body, headers={"Content-Type": "application/json", "X-Hub-Signature-256": sig})
        assert r.status_code == 200, payload
