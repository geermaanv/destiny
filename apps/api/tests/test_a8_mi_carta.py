"""Spec A8: Mi carta por dimensiones (identidad, amor, vocación, emociones)."""

import json
from datetime import date, time

import pytest

from app.astro import ZODIAC_SIGNS
from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import openrouter, sin_key  # noqa: F401

BIRTH = ("1990-05-20", "14:30")


def _chart(birth_date=BIRTH[0], birth_time=BIRTH[1], known=True):
    return compute_chart(
        date.fromisoformat(birth_date), time.fromisoformat(birth_time), known,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    )


def _dims(client, pid):
    r = client.get(f"/profiles/{pid}/natal/dimensions")
    assert r.status_code == 200, r.text
    return r.json()


def _by_key(body):
    return {d["clave"]: d for d in body["dimensiones"]}


def _angle(a, b):
    return abs((a - b + 180) % 360 - 180)


# 1
def test_cuatro_dimensiones_en_orden(client):
    from app.natal.dimensions import load_config

    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    body = _dims(client, pid)
    cfg = load_config()
    assert [d["clave"] for d in body["dimensiones"]] == list(cfg["dimensiones"])
    assert [d["clave"] for d in body["dimensiones"]] == ["identidad", "amor", "vocacion", "emociones"]
    for d in body["dimensiones"]:
        assert d["nombre"] and d["pregunta"].startswith("¿") and len(d["preguntas"]) >= 2
    assert body["aproximado"] is False


# 2
def test_identidad_con_sol_y_ascendente(client):
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    c = _chart()
    fundamentos = _by_key(_dims(client, pid))["identidad"]["fundamentos"]
    sol_signo = next(f for f in fundamentos if f["tipo"] == "signo" and f["punto"] == "sol")
    assert sol_signo["signo"] == ZODIAC_SIGNS[int(c.points["sol"] // 30)]
    sol_casa = next(f for f in fundamentos if f["tipo"] == "casa" and f["punto"] == "sol")
    assert sol_casa["casa"] == c.house_of(c.points["sol"])
    asc = next(f for f in fundamentos if f["tipo"] == "signo" and f["punto"] == "asc")
    assert asc["signo"] == ZODIAC_SIGNS[int(c.points["asc"] // 30)]


# 3
def test_aspectos_iguales_a_los_de_la_carta(client):
    from app.natal.dimensions import load_config

    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    cfg = load_config()
    c = _chart()
    points = cfg["puntos_de_aspecto"]
    body = _by_key(_dims(client, pid))
    for key, dim in cfg["dimensiones"].items():
        expected = set()
        for target in dim["aspectos_a"]:
            if target not in c.points:
                continue
            for other in points:
                if other == target or other not in c.points:
                    continue
                if other in dim["aspectos_a"] and dim["aspectos_a"].index(other) < dim["aspectos_a"].index(target):
                    continue  # el par ya se contó desde el otro punto
                sep = _angle(c.points[target], c.points[other])
                found = [(abs(sep - a["angulo"]), name) for name, a in cfg["aspectos"].items() if abs(sep - a["angulo"]) <= a["orbe"]]
                if found:
                    expected.add((target, other, min(found)[1]))
        actual = {(f["punto"], f["otro"], f["aspecto"]) for f in body[key]["fundamentos"] if f["tipo"] == "aspecto"}
        assert actual == expected, key


# 4
def test_sin_hora_exacta_no_hay_angulos_ni_casas(client):
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=None)
    body = _dims(client, pid)
    assert body["aproximado"] is True
    dims = _by_key(body)
    for d in dims.values():
        for f in d["fundamentos"]:
            assert f["tipo"] != "casa"
            assert f["punto"] not in ("asc", "mc", "desc", "ic") and f.get("otro") not in ("asc", "mc")
    assert "Ascendente" in " ".join(dims["identidad"]["faltan_por_hora"])
    assert dims["vocacion"]["faltan_por_hora"]


# 5
def test_biblioteca_completa_y_usada(client):
    from app.content.carta import load_library
    from app.natal.dimensions import load_config

    lib = load_library()
    for dim in load_config()["dimensiones"].values():
        for ind in dim["indicadores"]:
            if ind.get("signo"):
                for sign in ZODIAC_SIGNS:
                    text = lib["signo"][ind["punto"]][sign]
                    assert text.strip() and len(text) <= 280, (ind["punto"], sign)
            if ind.get("casa"):
                for house in range(1, 13):
                    text = lib["casa"][ind["punto"]][str(house)]
                    assert text.strip() and len(text) <= 280, (ind["punto"], house)
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    for f in _by_key(_dims(client, pid))["identidad"]["fundamentos"]:
        if f["tipo"] == "signo":
            assert f["texto"] == lib["signo"][f["punto"]][f["signo"]]
        if f["tipo"] == "casa":
            assert f["texto"] == lib["casa"][f["punto"]][str(f["casa"])]


# 6
def test_sintesis_sin_key_usa_plantilla(client, sin_key):  # noqa: F811
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    fundamentos = _by_key(_dims(client, pid))["amor"]["fundamentos"]
    r = client.get(f"/profiles/{pid}/natal/dimensions/amor/synthesis")
    assert r.status_code == 200
    assert r.json()["ia"] is False
    assert fundamentos[0]["texto"][:40] in r.json()["texto"]


# 7
def test_sintesis_con_ia_estilo_privacidad_y_cache(openrouter, client):  # noqa: F811
    from app.personalization.style import load_config as styles

    pid = verified_user(client, "5491111111111", name="Germancito", birth_date=BIRTH[0], birth_time=BIRTH[1])
    client.put(f"/profiles/{pid}/style", json={"registro": "practico"})
    r = client.get(f"/profiles/{pid}/natal/dimensions/identidad/synthesis")
    assert r.status_code == 200 and r.json()["ia"] is True
    assert r.json()["texto"] == openrouter.reply
    messages = openrouter.requests[0]["body"]["messages"]
    assert styles()["registro"]["estilos"]["practico"]["instruccion"] in messages[0]["content"]
    sent = json.dumps(messages, ensure_ascii=False)
    assert "Germancito" not in sent and "1990" not in sent and "Buenos Aires" not in sent
    client.get(f"/profiles/{pid}/natal/dimensions/identidad/synthesis")
    assert len(openrouter.requests) == 1
    client.put(f"/profiles/{pid}/style", json={"registro": "intuitivo"})
    client.get(f"/profiles/{pid}/natal/dimensions/identidad/synthesis")
    assert len(openrouter.requests) == 2


# 8
def test_solo_la_propia_persona(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    assert b.get(f"/profiles/{pid}/natal/dimensions").status_code == 403
    assert anon.get(f"/profiles/{pid}/natal/dimensions").status_code == 401
    assert a.get(f"/profiles/{pid}/natal/dimensions/astrologia/synthesis").status_code == 404


# 9
def test_indicadores_parametrizables(client, monkeypatch):
    from app.natal.dimensions import load_config

    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    monkeypatch.setitem(load_config()["dimensiones"]["identidad"], "indicadores", [{"punto": "luna", "signo": True}])
    monkeypatch.setitem(load_config()["dimensiones"]["identidad"], "aspectos_a", [])
    fundamentos = _by_key(_dims(client, pid))["identidad"]["fundamentos"]
    assert [(f["tipo"], f["punto"]) for f in fundamentos] == [("signo", "luna")]


# 10 (v2): Tu carta en el registro, antes de verificar
def test_perfil_sin_verificar_ve_su_carta_sin_sesion(new_client, sin_key):  # noqa: F811
    from tests.helpers import create_profile

    onboarding = new_client()
    pid = create_profile(onboarding, birth_date=BIRTH[0], birth_time=BIRTH[1])
    r = onboarding.get(f"/profiles/{pid}/natal/dimensions")
    assert r.status_code == 200, r.text
    c = _chart()
    sky = {p["punto"]: p["lon"] for p in r.json()["cielo"]}
    assert sky["sol"] == pytest.approx(c.points["sol"]) and "asc" in sky
    assert onboarding.get(f"/profiles/{pid}/natal/dimensions/identidad/synthesis").status_code == 200


def test_perfil_verificado_sigue_siendo_solo_del_duenio(new_client):
    owner, anon = new_client(), new_client()
    pid = verified_user(owner, "5491111111111")
    assert anon.get(f"/profiles/{pid}/natal/dimensions").status_code == 401
