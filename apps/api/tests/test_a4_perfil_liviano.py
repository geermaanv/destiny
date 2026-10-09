"""Spec A4-perfil-liviano: nombre obligatorio, foto o avatar, energía, intereses, frase y barrio."""

import struct
import zlib

from tests.helpers import create_profile, verified_user


def _png() -> bytes:
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(b"\x00\xff\x00\x00"))
        + chunk(b"IEND", b"")
    )


def test_perfil_completo_se_guarda(client):
    pid = create_profile(client)
    r = client.post(
        f"/profiles/{pid}/basic-info",
        json={
            "display_name": "  Luz ",
            "energy_period": "noche",
            "interests": ["musica", "viajes", "musica"],
            "bio": "Fan de los atardeceres",
            "neighborhood": "Palermo",
            "avatar": "luna",
        },
    )
    body = r.json()
    assert r.status_code == 200
    assert body["display_name"] == "Luz"
    assert body["interests"] == ["musica", "viajes"]
    assert body["avatar"] == "luna" and body["neighborhood"] == "Palermo"


def test_nombre_es_obligatorio(client):
    pid = create_profile(client)
    assert client.post(f"/profiles/{pid}/basic-info", json={"display_name": "   "}).status_code == 422


def test_intereses_fuera_de_la_lista_o_mas_de_5_se_rechazan(client):
    pid = create_profile(client)
    assert client.post(f"/profiles/{pid}/basic-info", json={"display_name": "a", "interests": ["x"]}).status_code == 422
    seis = ["musica", "deporte", "arte", "cine", "viajes", "cocina"]
    assert client.post(f"/profiles/{pid}/basic-info", json={"display_name": "a", "interests": seis}).status_code == 422


def test_frase_hasta_140_caracteres(client):
    pid = create_profile(client)
    assert client.post(f"/profiles/{pid}/basic-info", json={"display_name": "a", "bio": "x" * 141}).status_code == 422


def test_foto_subir_ver_y_borrar(client):
    pid = create_profile(client)
    r = client.post(f"/profiles/{pid}/photo", files={"photo": ("p.png", _png(), "image/png")})
    assert r.status_code == 200 and r.json()["has_photo"] is True
    foto = client.get(f"/profiles/{pid}/photo")
    assert foto.status_code == 200 and foto.headers["content-type"] == "image/png"
    assert client.delete(f"/profiles/{pid}/photo").json()["has_photo"] is False


def test_foto_que_no_es_imagen_se_rechaza(client):
    pid = create_profile(client)
    r = client.post(f"/profiles/{pid}/photo", files={"photo": ("a.txt", b"hola", "text/plain")})
    assert r.status_code == 415


def test_edad_y_signo_se_calculan_solos(new_client):
    a, b = new_client(), new_client()
    verified_user(a, "5491111111111", name="Ana", birth_date="1990-05-20")
    viewer = verified_user(b, "5492222222222", name="Beto")
    candidato = b.get("/discover", params={"viewer_id": viewer}).json()[0]
    assert candidato["sun_sign"] == "Tauro"
    assert candidato["age"] >= 36


def test_perfiles_sin_nombre_no_aparecen_en_descubrir(new_client):
    a, b, c = new_client(), new_client(), new_client()
    pid_sin_nombre = create_profile(a)
    from tests.helpers import verify

    verify(a, pid_sin_nombre, "5491111111111")
    verified_user(b, "5492222222222", name="Beto")
    viewer = verified_user(c, "5493333333333", name="Caro")
    nombres = [x["display_name"] for x in c.get("/discover", params={"viewer_id": viewer}).json()]
    assert nombres == ["Beto"]
    assert c.get("/home/frequency-count", params={"profile_id": viewer}).json()["count"] == 1


def test_geminis_en_castellano(client):
    pid = create_profile(client, birth_date="1990-06-05")
    assert client.get(f"/profiles/{pid}").json()["sun_sign"] == "Géminis"
