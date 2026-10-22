"""Spec R2: sin duplicados, límites que se respetan y conexiones que no se traban (agente breaker)."""

import threading

import pytest

from tests.helpers import create_profile, verified_user
from tests.test_a10_verificacion_opcional import active_user
from tests.test_x1_redaccion_con_ia import openrouter  # noqa: F401


@pytest.fixture
def dos(new_client):
    a, b = new_client(), new_client()
    pa = verified_user(a, "5491111111111", name="Ana")
    pb = verified_user(b, "5492222222222", name="Beto")
    return a, pa, b, pb


def parallel(fns):
    out = []
    threads = [threading.Thread(target=lambda f=f: out.append(f())) for f in fns]
    [t.start() for t in threads]
    [t.join() for t in threads]
    return out


def conexiones(client, pid):
    return [c for c in client.get("/connections", params={"profile_id": pid}).json()]


# 1
def test_una_sola_conexion_por_par(dos):
    a, pa, b, pb = dos
    fns = [
        (lambda: a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb}).status_code)
        if i % 2 == 0
        else (lambda: b.post("/matches", json={"profile_a_id": pb, "profile_b_id": pa}).status_code)
        for i in range(10)
    ]
    codes = parallel(fns)
    assert 500 not in codes
    assert len(conexiones(a, pa)) == 1


# 2
def test_limite_de_indagar_en_paralelo(client, openrouter, monkeypatch):  # noqa: F811
    from app.astrochat.chat import load_config

    monkeypatch.setitem(load_config(), "limite_diario", 3)
    pid = verified_user(client, "5491111111111")
    codes = parallel([lambda: client.post(f"/profiles/{pid}/astrochat", json={"texto": "hola"}).status_code for _ in range(20)])
    assert codes.count(200) == 3 and len(openrouter.requests) == 3


# 3
def test_privacidad_antes_de_verificar(client):
    pid = create_profile(client, name="Ana", privacy=False)
    assert client.post(f"/profiles/{pid}/verification/whatsapp").status_code == 409
    r = client.post(f"/profiles/{pid}/privacy", json={"version": "no_lei_nada", "contexto": "registro"})
    assert r.status_code == 422
    client.post(f"/profiles/{pid}/privacy", json={"version": "privacidad_v1", "contexto": "registro"})
    assert client.post(f"/profiles/{pid}/verification/whatsapp").status_code == 200


# 4
@pytest.mark.parametrize("previo", ["pendiente", "rechazada"])
def test_la_invitacion_conecta_igual(new_client, previo):
    a, b = new_client(), new_client()
    pablo = verified_user(a, "5491111111111", name="Pablo")
    ref = a.post("/invitations", json={"inviter_id": pablo, "friend_name": "Mavi"}).json()["ref_id"]
    mavi = active_user(b, name="Mavi")
    if previo == "rechazada":
        # Mavi había rechazado a Pablo y después acepta su link: cambió de idea, se conectan.
        # (Si Pablo la hubiera rechazado, su link no los conecta: spec R3.)
        m = a.post("/matches", json={"profile_a_id": pablo, "profile_b_id": mavi}).json()
        b.post(f"/matches/{m['id']}/reject", json={"profile_id": mavi})
    else:
        b.post("/matches", json={"profile_a_id": mavi, "profile_b_id": pablo})
    r = b.post(f"/invitations/{ref}/accept")
    assert r.status_code == 200
    assert b.get(f"/matches/{r.json()['match_id']}").json()["status"] == "aceptada"


# 5
def test_quien_rechazo_pide_conexion(dos):
    a, pa, b, pb = dos
    m = a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb}).json()
    b.post(f"/matches/{m['id']}/reject", json={"profile_id": pb})
    r = b.post("/matches", json={"profile_a_id": pb, "profile_b_id": pa})
    assert r.json()["status"] == "aceptada"


# 6
def test_quien_fue_rechazado_no_se_entera(dos):
    a, pa, b, pb = dos
    m = a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb}).json()
    b.post(f"/matches/{m['id']}/reject", json={"profile_id": pb})
    assert a.get(f"/matches/{m['id']}").json()["status"] == "pendiente"
    assert [c["status"] for c in conexiones(a, pa)] == ["pendiente"]
    again = a.post("/matches", json={"profile_a_id": pa, "profile_b_id": pb})
    assert again.json()["status"] == "pendiente" and again.json()["id"] == m["id"]
