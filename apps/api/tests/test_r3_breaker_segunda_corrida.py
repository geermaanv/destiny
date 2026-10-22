"""Spec R3: bloqueo sin fugas, explicación con test completo, Círculo rápido, límites y sesión (breaker, 2da corrida)."""

import json
import threading

from tests.helpers import complete_personality, send_whatsapp, verified_user
from tests.test_a10_verificacion_opcional import active_user
from tests.test_x1_redaccion_con_ia import openrouter  # noqa: F401

PALERMO = {"query": "Palermo", "lat": -34.5875, "lon": -58.4250}
ROSARIO = {"query": "Rosario", "lat": -32.9468, "lon": -60.6393}
CORDOBA = {"query": "Córdoba", "lat": -31.4201, "lon": -64.1888}


def parallel(fns):
    out = []
    threads = [threading.Thread(target=lambda f=f: out.append(f())) for f in fns]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return out


# 1
def test_el_bloqueo_corta_las_invitaciones_y_la_ficha(new_client):
    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana")
    ref = a.post("/invitations", json={"inviter_id": ana, "friend_name": "Amigos"}).json()["ref_id"]
    beto = verified_user(b, "5492222222222", name="Beto")
    m = b.post("/matches", json={"profile_a_id": beto, "profile_b_id": ana}).json()
    a.post(f"/matches/{m['id']}/block", json={"profile_id": ana})
    assert b.get(f"/invitations/{ref}/reveal", params={"invitee_id": beto}).status_code == 404
    assert b.post(f"/invitations/{ref}/accept").status_code == 404
    assert a.get("/invitations/mine", params={"profile_id": ana}).json()[0]["aceptaron"] == 0
    assert b.get(f"/matches/{m['id']}").status_code == 404
    assert a.get(f"/matches/{m['id']}").status_code == 404
    assert b.post(f"/matches/{m['id']}/block", json={"profile_id": beto}).status_code == 409


# 2
def test_la_explicacion_no_usa_el_test_incompleto(new_client, openrouter):  # noqa: F811
    a, b = new_client(), new_client()
    viewer = verified_user(a, "5491111111111", name="Vera")
    otra = verified_user(b, "5492222222222", name="Ana")
    complete_personality(b, otra)
    a.put(f"/profiles/{viewer}/personality", json={"answers": {"E2.01": [1]}})
    a.get(f"/discover/{otra}/explanation", params={"viewer_id": viewer})
    assert "test_de_personalidad" not in json.dumps(openrouter.requests[-1]["body"], ensure_ascii=False)


# 3
def test_circulo_calcula_cada_par_una_sola_vez(new_client, monkeypatch):
    from app.synastry import engine

    calls = []
    original = engine.calcular
    monkeypatch.setattr(engine, "calcular", lambda *args, **kw: calls.append(1) or original(*args, **kw))
    engine.clear_pair_cache()
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    active_user(b, name="Ana", birth_date="1992-08-03")
    active_user(c, name="Beto", birth_date="1985-01-15")
    for context in ["pareja", "amistad", "pareja"]:
        a.get("/discover", params={"viewer_id": viewer, "context": context})
    assert len(calls) == 2


# 4
def test_donde_vivis_una_vez_por_mes(client):
    pid = active_user(client)
    assert client.post(f"/profiles/{pid}/residence", json=PALERMO).status_code == 200  # primera carga
    assert client.post(f"/profiles/{pid}/residence", json=ROSARIO).status_code == 200  # el cambio del mes
    assert client.post(f"/profiles/{pid}/residence", json=CORDOBA).status_code == 429


def test_donde_vivis_en_paralelo(client):
    pid = active_user(client)
    client.post(f"/profiles/{pid}/residence", json=PALERMO)
    codes = parallel([lambda: client.post(f"/profiles/{pid}/residence", json=ROSARIO).status_code for _ in range(10)])
    assert codes.count(200) == 1


# 5
def test_aceptar_y_rechazar_a_la_vez(new_client):
    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana")
    beto = verified_user(b, "5492222222222", name="Beto")
    m = a.post("/matches", json={"profile_a_id": ana, "profile_b_id": beto}).json()
    results = parallel(
        [lambda: ("aceptada", b.post(f"/matches/{m['id']}/accept", json={"profile_id": beto}).status_code)] * 2
        + [lambda: ("rechazada", b.post(f"/matches/{m['id']}/reject", json={"profile_id": beto}).status_code)] * 2
    )
    ok = [state for state, code in results if code == 200]
    assert len(ok) == 1
    assert b.get(f"/matches/{m['id']}").json()["status"] == ok[0]


# 6
def test_seguir_con_mi_cuenta_con_datos_en_el_duplicado(new_client):
    a, b = new_client(), new_client()
    existente = verified_user(a, "5491111111111", name="Ana")
    nueva = active_user(b, name="Ana bis")  # sesión, foto y aviso aceptado (A10)
    complete_personality(b, nueva)
    code = b.post(f"/profiles/{nueva}/verification/whatsapp").json()
    send_whatsapp(b, "5491111111111", code["code"])
    r = b.post(f"/profiles/{nueva}/verification/continue-existing", json={"claim_token": code["claim_token"]})
    assert r.status_code == 200, r.text
    assert b.get("/me").json()["id"] == existente


# 7
def test_cerrar_sesion_cierra_de_verdad(client):
    pid = active_user(client)
    client.post("/sessions/logout")
    assert client.get("/me").status_code == 401
    assert client.post("/sessions/start", json={"profile_id": pid}).status_code == 403


# 8
def test_un_link_no_pasa_por_encima_de_un_rechazo(new_client):
    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana")
    beto = verified_user(b, "5492222222222", name="Beto")
    m = b.post("/matches", json={"profile_a_id": beto, "profile_b_id": ana}).json()
    a.post(f"/matches/{m['id']}/reject", json={"profile_id": ana})
    ref = a.post("/invitations", json={"inviter_id": ana, "friend_name": "Amigos"}).json()["ref_id"]
    b.post(f"/invitations/{ref}/accept")
    assert a.get("/connections", params={"profile_id": ana}).json() == []
    assert b.get(f"/matches/{m['id']}").json()["status"] == "pendiente"
