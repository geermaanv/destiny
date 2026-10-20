"""Spec U3: chats con novedades (sin leer) para la franja de conexiones de Círculo."""

import pytest

from tests.helpers import verified_user


@pytest.fixture
def chat(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto")
    m = a.post("/matches", json={"profile_a_id": pid_a, "profile_b_id": pid_b}).json()
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": pid_b})
    return a, pid_a, b, pid_b, m["id"]


def unread(client, profile_id, match_id):
    conns = client.get("/connections", params={"profile_id": profile_id}).json()
    return next(c for c in conns if c["match_id"] == match_id)["unread"]


# 1
def test_la_otra_persona_escribe(chat):
    a, pid_a, b, pid_b, mid = chat
    b.post(f"/chats/{mid}/messages", json={"profile_id": pid_b, "text": "Hola Ana"})
    assert unread(a, pid_a, mid) is True
    assert unread(b, pid_b, mid) is False


# 2 y 3
def test_abrir_el_chat_lo_marca_leido(chat):
    a, pid_a, b, pid_b, mid = chat
    b.post(f"/chats/{mid}/messages", json={"profile_id": pid_b, "text": "Hola Ana"})
    a.get(f"/chats/{mid}/messages")
    assert unread(a, pid_a, mid) is False
    b.post(f"/chats/{mid}/messages", json={"profile_id": pid_b, "text": "¿Estás?"})
    assert unread(a, pid_a, mid) is True


# 4
def test_el_rompehielos_no_cuenta(chat):
    a, pid_a, b, pid_b, mid = chat
    assert unread(a, pid_a, mid) is False and unread(b, pid_b, mid) is False
