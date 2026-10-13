"""Spec B4 v3: Tu día completo (clima, tránsitos, áreas y lectura)."""

import json
from datetime import date, time

import astronomy
import pytest

from app.astro import ZODIAC_SIGNS, moon_longitude, moon_phase_name
from app.synastry.chart import compute_chart
from tests.helpers import BUENOS_AIRES, verified_user
from tests.test_x1_redaccion_con_ia import FakeOpenRouter  # noqa: F401
from tests.test_x1_redaccion_con_ia import openrouter, sin_key  # noqa: F401

DAY = "2026-10-12"
BIRTH = ("1990-05-20", "14:30")


def _natal(known=True):
    return compute_chart(
        date.fromisoformat(BIRTH[0]), time.fromisoformat(BIRTH[1]), known,
        BUENOS_AIRES["lat"], BUENOS_AIRES["lon"], BUENOS_AIRES["timezone"],
    )


def _detail(client, pid, day=DAY):
    r = client.get("/home/my-day/detail", params={"profile_id": pid, "date": day})
    assert r.status_code == 200, r.text
    return r.json()


def _angle(a, b):
    return abs((a - b + 180) % 360 - 180)


# 1
def test_solo_la_propia_persona(new_client):
    a, b, anon = new_client(), new_client(), new_client()
    pid = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    params = {"profile_id": pid, "date": DAY}
    assert b.get("/home/my-day/detail", params=params).status_code == 403
    assert anon.get("/home/my-day/detail", params=params).status_code == 401


# 2 y 3
def test_luna_signo_fase_y_casa(client, sin_key):  # noqa: F811
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    body = _detail(client, pid)
    d = date.fromisoformat(DAY)
    moon = moon_longitude(d)
    phase = moon_phase_name(astronomy.MoonPhase(astronomy.Time.Make(d.year, d.month, d.day, 12, 0, 0)))
    natal = _natal()
    house = (int(moon // 30) - int(natal.points["asc"] // 30)) % 12 + 1
    assert body["luna"]["signo"] == ZODIAC_SIGNS[int(moon // 30)]
    assert body["luna"]["fase"] == phase
    assert body["luna"]["casa"] == house and body["luna"]["tema_casa"]
    assert body["aproximado"] is False


def test_sin_hora_exacta_no_hay_casa(client, sin_key):  # noqa: F811
    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=None)
    body = _detail(client, pid)
    assert body["luna"].get("casa") is None and body["aproximado"] is True
    assert all(t["punto"] not in ("asc", "mc") for t in body["transitos"])


# 4
def test_transitos_reales_y_ordenados(client, sin_key):  # noqa: F811
    from app.day.detail import load_config

    pid = verified_user(client, "5491111111111", birth_date=BIRTH[0], birth_time=BIRTH[1])
    body = _detail(client, pid)
    cfg = load_config()
    natal = _natal()
    sky = compute_chart(date.fromisoformat(DAY), time(12, 0), False, None, None, "UTC")
    assert 0 < len(body["transitos"]) <= 3
    for t in body["transitos"]:
        sep = _angle(sky.points[t["planeta"]], natal.points[t["punto"]])
        angle = cfg["aspectos"][t["aspecto"]]["angulo"]
        assert abs(sep - angle) == pytest.approx(t["orbe"], abs=1e-6)
        assert t["orbe"] <= cfg["orbes"][t["planeta"]] and t["texto"]
    strengths = [t["fuerza"] for t in body["transitos"]]
    assert strengths == sorted(strengths, reverse=True)


# 5
def test_cuatro_areas(client, sin_key):  # noqa: F811
    pid = verified_user(client, "5491111111111")
    areas = _detail(client, pid)["areas"]
    assert [a["clave"] for a in areas] == ["amor", "trabajo", "emociones", "energia"]
    assert all(a["estado"] in ("fluye", "cuidado", "tranquilo") and a["nombre"] for a in areas)


# 6
def test_lectura_sin_key_es_plantilla(client, sin_key):  # noqa: F811
    pid = verified_user(client, "5491111111111")
    body = _detail(client, pid)
    assert body["lectura"]["ia"] is False and body["lectura"]["texto"] and body["pregunta"].startswith("¿")


def test_lectura_con_ia_estilo_privacidad_y_cache(client, openrouter):  # noqa: F811
    from app.personalization.style import load_config as styles

    pid = verified_user(client, "5491111111111", name="Germancito", birth_date=BIRTH[0], birth_time=BIRTH[1])
    client.put(f"/profiles/{pid}/style", json={"registro": "practico"})
    body = _detail(client, pid)
    assert body["lectura"] == {"texto": openrouter.reply, "ia": True}
    messages = openrouter.requests[0]["body"]["messages"]
    assert styles()["registro"]["estilos"]["practico"]["instruccion"] in messages[0]["content"]
    sent = json.dumps(messages, ensure_ascii=False)
    assert "Germancito" not in sent and "1990" not in sent and "Buenos Aires" not in sent
    _detail(client, pid)
    assert len(openrouter.requests) == 1


# 7
def test_orbes_parametrizables(client, sin_key, monkeypatch):  # noqa: F811
    from app.day.detail import load_config

    pid = verified_user(client, "5491111111111")
    monkeypatch.setitem(load_config(), "orbes", {p: 0.0 for p in load_config()["orbes"]})
    body = _detail(client, pid)
    assert body["transitos"] == []
    assert all(a["estado"] == "tranquilo" for a in body["areas"])
