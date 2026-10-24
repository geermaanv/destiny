"""Spec B13: nivel y frase junto al número global (rangos de Pablo, textos ajustados)."""

import json
from pathlib import Path

import pytest

from tests.helpers import verified_user
from tests.test_a10_verificacion_opcional import active_user

CONFIG = json.loads(
    (Path(__file__).resolve().parents[1] / "app" / "content" / "niveles_compatibilidad_v1.json").read_text()
)


# 1
@pytest.mark.parametrize(
    "pct, nivel",
    [
        (0, "baja"), (29, "baja"), (30, "moderada"), (49, "moderada"), (50, "alta"),
        (64, "alta"), (65, "muy_alta"), (84, "muy_alta"), (85, "excepcional"), (100, "excepcional"),
    ],
)
def test_bordes_de_cada_nivel(pct, nivel):
    from app.compat_summary import level_for

    assert level_for(pct)["id"] == nivel


# 2
def test_textos_desde_la_configuracion():
    from app.compat_summary import level_for

    for item in CONFIG["niveles"]:
        nivel = level_for(item["desde"])
        assert nivel == {"id": item["id"], "nombre": item["nombre"], "texto": item["texto"]}
    textos = json.dumps(CONFIG["niveles"], ensure_ascii=False).lower()
    assert "almas gemelas" not in textos and "otra vida" not in textos


# 3
def test_tarjeta_de_circulo(new_client):
    from app.compat_summary import level_for

    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana", birth_date="1992-08-03")
    r = a.get("/discover", params={"viewer_id": viewer})
    assert r.status_code == 200, r.text
    card = next(x for x in r.json() if x["profile_id"] == otra)
    assert card["nivel"] == level_for(card["global_pct"])


# 4
def test_compatibilidad_del_chat(new_client):
    from app.compat_summary import level_for

    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    pid_b = verified_user(b, "5492222222222", name="Beto", birth_date="1992-08-03")
    m = a.post("/matches", json={"profile_a_id": pid_a, "profile_b_id": pid_b}).json()
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": pid_b})
    s = a.get(f"/matches/{m['id']}/compatibility/summary").json()
    assert s["nivel"] == level_for(s["global_pct"])
