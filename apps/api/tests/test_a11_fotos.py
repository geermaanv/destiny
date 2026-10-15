"""Spec A11: fotos del perfil (hasta 4, la primera es la principal) con chequeo automático."""

import json

import pytest

from tests.helpers import add_photo, png, verified_user
from tests.test_a10_verificacion_opcional import active_user
from tests.test_x1_redaccion_con_ia import openrouter, sin_key  # noqa: F401


def photos(client, pid):
    r = client.get(f"/profiles/{pid}/photos")
    assert r.status_code == 200, r.text
    return r.json()["photos"]


def veredicto(fake, apta=True, motivo=None, persona=True):
    fake.moderation_reply = json.dumps({"apta": apta, "motivo": motivo, "persona": persona})


# 1
def test_subir_listar_y_ver(client):
    pid = active_user(client, photo=False)
    r = add_photo(client, pid)
    assert r.status_code == 201, r.text
    [foto] = r.json()["photos"]
    assert foto["principal"] is True and r.json()["max"] == 4
    assert client.get(foto["url"]).content == png()
    assert client.get(f"/profiles/{pid}/photo").content == png()
    assert client.get(f"/profiles/{pid}").json()["has_photo"] is True


# 2
def test_tope_de_4(client):
    pid = active_user(client, photo=False)
    for _ in range(4):
        assert add_photo(client, pid).status_code == 201
    assert add_photo(client, pid).status_code == 409
    assert len(photos(client, pid)) == 4


# 3
def test_formato_y_tamanio(client):
    pid = active_user(client, photo=False)
    r = client.post(f"/profiles/{pid}/photos", files={"photo": ("a.txt", b"hola", "text/plain")})
    assert r.status_code == 415
    grande = png() + b"\0" * (5 * 1024 * 1024)
    r = client.post(f"/profiles/{pid}/photos", files={"photo": ("g.png", grande, "image/png")})
    assert r.status_code == 413
    assert photos(client, pid) == []


# 4
def test_solo_el_duenio(client, new_client):
    pid = active_user(client)
    [foto] = photos(client, pid)
    otro = new_client()
    assert add_photo(otro, pid).status_code == 401
    assert otro.get(f"/profiles/{pid}/photos").status_code == 401
    assert otro.delete(f"/profiles/{pid}/photos/{foto['id']}").status_code == 401
    assert otro.post(f"/profiles/{pid}/photos/{foto['id']}/principal").status_code == 401


# 5
def test_elegir_otra_como_principal(client):
    pid = active_user(client, photo=False)
    add_photo(client, pid)
    otra = client.post(f"/profiles/{pid}/photos", files={"photo": ("b.png", png() + b"b", "image/png")})
    segunda = otra.json()["photos"][1]
    r = client.post(f"/profiles/{pid}/photos/{segunda['id']}/principal")
    assert r.status_code == 200
    assert r.json()["photos"][0]["id"] == segunda["id"] and r.json()["photos"][0]["principal"] is True
    assert client.get(f"/profiles/{pid}/photo").content == png() + b"b"


# 6
def test_borrar_la_principal(client):
    pid = active_user(client, photo=False)
    add_photo(client, pid)
    add_photo(client, pid)
    primera, segunda = photos(client, pid)
    r = client.delete(f"/profiles/{pid}/photos/{primera['id']}")
    assert [f["id"] for f in r.json()["photos"]] == [segunda["id"]]
    assert r.json()["photos"][0]["principal"] is True
    assert client.get(f"/photos/{primera['id']}").status_code == 404
    client.delete(f"/profiles/{pid}/photos/{segunda['id']}")
    assert client.get(f"/profiles/{pid}").json()["has_photo"] is False
    assert client.get(f"/profiles/{pid}/photo").status_code == 404


# 7
def test_la_ia_rechaza(client, openrouter):  # noqa: F811
    pid = active_user(client, photo=False)
    veredicto(openrouter, apta=False, motivo="desnudo")
    r = add_photo(client, pid)
    assert r.status_code == 422
    assert "no se puede usar" in r.json()["detail"].lower()
    assert photos(client, pid) == []


# 8
def test_principal_tiene_que_mostrar_una_persona(client, openrouter):  # noqa: F811
    pid = active_user(client, photo=False)
    veredicto(openrouter, persona=False)
    assert add_photo(client, pid).status_code == 422  # sería la principal
    veredicto(openrouter, persona=True)
    assert add_photo(client, pid).status_code == 201
    veredicto(openrouter, persona=False)
    r = add_photo(client, pid)  # paisaje como extra: va
    assert r.status_code == 201
    paisaje = r.json()["photos"][1]
    assert client.post(f"/profiles/{pid}/photos/{paisaje['id']}/principal").status_code == 409


# 9
@pytest.mark.parametrize("falla", ["sin_key", "error", "basura"])
def test_si_la_ia_falla_se_acepta(client, request, falla):
    if falla == "sin_key":
        request.getfixturevalue("sin_key")
    else:
        fake = request.getfixturevalue("openrouter")
        if falla == "error":
            fake.status = 500
        else:
            fake.moderation_reply = "no es json"
    pid = active_user(client, photo=False)
    assert add_photo(client, pid).status_code == 201

    from app.database import SessionLocal
    from app.models import ProfilePhoto

    with SessionLocal() as db:
        assert db.query(ProfilePhoto).one().moderacion == "sin_revisar"


# 10
def test_a_la_ia_va_solo_la_imagen(client, openrouter):  # noqa: F811
    pid = active_user(client, name="Anastasia", photo=False)
    veredicto(openrouter)
    assert add_photo(client, pid).status_code == 201
    [pedido] = openrouter.moderation
    body = pedido["body"]
    texto = json.dumps(body)
    assert "Anastasia" not in texto and pid not in texto and "1990" not in texto
    assert body["provider"]["data_collection"] == "deny"
    partes = body["messages"][-1]["content"]
    assert any(p["type"] == "image_url" and p["image_url"]["url"].startswith("data:image/png;base64,") for p in partes)


# 11
def test_descubrir_exige_foto(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    con_foto = verified_user(b, "5491111111111", name="Cami")
    sin_foto = verified_user(c, "5492222222222", name="Beto", photo=False)
    found = {x["profile_id"]: x for x in a.get("/discover", params={"viewer_id": viewer}).json()}
    assert sin_foto not in found
    assert found[con_foto]["photos"] and found[con_foto]["photos"][0] == found[con_foto]["photo_url"]


# 12
def test_sin_foto_igual_ve_descubrir(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera", photo=False)
    otra = verified_user(b, "5491111111111", name="Cami")
    r = a.get("/discover", params={"viewer_id": viewer})
    assert r.status_code == 200 and otra in [x["profile_id"] for x in r.json()]
