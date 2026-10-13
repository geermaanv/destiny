"""Spec X3: Astrochat (preguntale a Destiny), con OpenRouter simulado."""

import json
from datetime import date, time

import pytest

from app.astro import ZODIAC_SIGNS
from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import openrouter, sin_key  # noqa: F401

PHONE = "5491111111111"
BIRTH = ("1990-05-20", "14:30")


def _url(pid):
    return f"/profiles/{pid}/astrochat"


def _ask(client, pid, texto, **extra):
    return client.post(_url(pid), json={"texto": texto, **extra})


def _config():
    from app.astrochat.chat import load_config

    return load_config()


# 1
def test_solo_la_propia_persona(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, PHONE)
    verified_user(b, "5492222222222")
    assert b.get(_url(pid)).status_code == 403
    assert anon.get(_url(pid)).status_code == 401
    assert b.post(_url(pid), json={"texto": "hola"}).status_code == 403


# 2
def test_conversacion_vacia(client):
    pid = verified_user(client, PHONE)
    client.put(f"/profiles/{pid}/style", json={"registro": "analitico"})
    body = client.get(_url(pid)).json()
    cfg = _config()
    assert body["mensajes"] == []
    assert body["modo"] == cfg["modo_por_registro"]["analitico"]
    assert [m["clave"] for m in body["modos"]] == list(cfg["modos"])
    assert body["restantes_hoy"] == body["limite"] == cfg["limite_diario"]
    assert body["ejemplos"]


# 3
def test_preguntar(client, openrouter):  # noqa: F811
    pid = verified_user(client, PHONE)
    r = _ask(client, pid, "¿Por qué me cuesta decidir?", modo="mentor")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["respuesta"]["texto"] == openrouter.reply and body["ia"] is True
    assert body["respuesta"]["rol"] == "destiny" and body["respuesta"]["modo"] == "mentor"
    assert body["restantes_hoy"] == _config()["limite_diario"] - 1
    history = client.get(_url(pid)).json()
    assert [(m["rol"], m["texto"]) for m in history["mensajes"]] == [
        ("persona", "¿Por qué me cuesta decidir?"),
        ("destiny", openrouter.reply),
    ]
    assert history["modo"] == "mentor"


# 4
def test_prompt_con_modo_estilo_y_datos_sin_datos_personales(client, openrouter):  # noqa: F811
    from app.personalization.style import load_config as styles

    pid = verified_user(client, PHONE, name="Germancito", birth_date=BIRTH[0], birth_time=BIRTH[1])
    client.put(f"/profiles/{pid}/style", json={"registro": "practico"})
    _ask(client, pid, "¿Qué onda mi semana?", modo="tecnico")
    messages = openrouter.requests[0]["body"]["messages"]
    system = messages[0]["content"]
    assert _config()["modos"]["tecnico"]["instruccion"] in system
    assert styles()["registro"]["estilos"]["practico"]["instruccion"] in system
    sun = compute_chart(date.fromisoformat(BIRTH[0]), time.fromisoformat(BIRTH[1]), True,
                        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"]).points["sol"]
    assert ZODIAC_SIGNS[int(sun // 30)] in system
    sent = json.dumps(messages, ensure_ascii=False)
    for forbidden in ("Germancito", "1990", "20/05", "14:30", "Buenos Aires", PHONE):
        assert forbidden not in sent, forbidden
    assert messages[-1] == {"role": "user", "content": "¿Qué onda mi semana?"}


# 5
def test_contexto_de_la_conversacion(client, openrouter):  # noqa: F811
    pid = verified_user(client, PHONE)
    _ask(client, pid, "Primera pregunta")
    _ask(client, pid, "Segunda pregunta")
    roles = [(m["role"], m["content"]) for m in openrouter.requests[1]["body"]["messages"][1:]]
    assert roles == [("user", "Primera pregunta"), ("assistant", openrouter.reply), ("user", "Segunda pregunta")]


# 6 y 11
def test_limite_diario_y_borrar_no_lo_reinicia(client, openrouter, monkeypatch):  # noqa: F811
    monkeypatch.setitem(_config(), "limite_diario", 2)
    pid = verified_user(client, PHONE)
    assert _ask(client, pid, "uno").status_code == 200
    assert _ask(client, pid, "dos").json()["restantes_hoy"] == 0
    calls = len(openrouter.requests)
    assert _ask(client, pid, "tres").status_code == 429
    assert client.delete(_url(pid)).status_code == 204
    assert _ask(client, pid, "cuatro").status_code == 429
    assert len(openrouter.requests) == calls
    assert client.get(_url(pid)).json()["restantes_hoy"] == 0


# 7
def test_crisis_respuesta_fija_sin_ia(client, openrouter):  # noqa: F811
    pid = verified_user(client, PHONE)
    body = _ask(client, pid, "a veces siento que no quiero vivir más").json()
    assert "135" in body["respuesta"]["texto"] and body["ia"] is False
    assert openrouter.requests == []
    assert body["restantes_hoy"] == _config()["limite_diario"]


# 8
@pytest.mark.parametrize("payload", [{"texto": "   "}, {"texto": "x" * 501}, {"texto": "hola", "modo": "oraculo"}])
def test_validaciones(client, payload):
    pid = verified_user(client, PHONE)
    assert client.post(_url(pid), json=payload).status_code == 422


# 9
def test_sin_key_respuesta_fija(client, sin_key):  # noqa: F811
    pid = verified_user(client, PHONE)
    body = _ask(client, pid, "hola").json()
    assert body["ia"] is False and body["respuesta"]["texto"] == _config()["sin_ia"]


def test_si_la_ia_falla_respuesta_fija(client, openrouter):  # noqa: F811
    openrouter.status = 500
    pid = verified_user(client, PHONE)
    body = _ask(client, pid, "hola").json()
    assert body["ia"] is False and body["respuesta"]["texto"] == _config()["sin_ia"]


# 10
def test_borrar_conversacion(client, openrouter):  # noqa: F811
    pid = verified_user(client, PHONE)
    _ask(client, pid, "Algo viejo")
    assert client.delete(_url(pid)).status_code == 204
    assert client.get(_url(pid)).json()["mensajes"] == []
    _ask(client, pid, "Algo nuevo")
    sent = json.dumps(openrouter.requests[-1]["body"]["messages"], ensure_ascii=False)
    assert "Algo viejo" not in sent
