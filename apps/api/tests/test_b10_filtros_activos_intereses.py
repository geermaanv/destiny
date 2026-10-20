"""Spec B10: filtro de intereses (todos los marcados) e intereses en común en Círculo."""

from tests.test_a10_verificacion_opcional import active_user


def intereses(client, pid, name, lista):
    r = client.post(f"/profiles/{pid}/basic-info", json={"display_name": name, "interests": lista})
    assert r.status_code == 200, r.text


def discover(client, viewer, **params):
    r = client.get("/discover", params={"viewer_id": viewer, **params})
    assert r.status_code == 200, r.text
    return r.json()


# 1
def test_filtra_con_todos(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    los_dos = active_user(b, name="Ana")
    intereses(b, los_dos, "Ana", ["musica", "viajes", "cine"])
    uno = active_user(c, name="Beto")
    intereses(c, uno, "Beto", ["musica"])
    found = [x["profile_id"] for x in discover(a, viewer, intereses="musica,viajes")]
    assert los_dos in found and uno not in found


# 2
def test_interes_invalido(client):
    viewer = active_user(client)
    assert client.get("/discover", params={"viewer_id": viewer, "intereses": "gatos"}).status_code == 422


# 3
def test_intereses_en_comun_siempre(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    intereses(a, viewer, "Vera", ["viajes", "musica", "arte"])
    otra = active_user(b, name="Ana")
    intereses(b, otra, "Ana", ["cine", "musica", "viajes"])
    [c] = discover(a, viewer)
    assert c["common_interests"] == ["musica", "viajes"]


# 4
def test_desempate_por_intereses(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    intereses(a, viewer, "Vera", ["musica", "viajes", "arte"])
    # Mismos datos de nacimiento → mismo número global.
    pocos = active_user(b, name="Uno", birth_date="1992-08-03")
    intereses(b, pocos, "Uno", ["musica"])
    muchos = active_user(c, name="Dos", birth_date="1992-08-03")
    intereses(c, muchos, "Dos", ["musica", "viajes", "arte"])
    r = discover(a, viewer)
    assert r[0]["global_pct"] == r[1]["global_pct"]
    assert [x["profile_id"] for x in r] == [muchos, pocos]


# 5
def test_la_busqueda_ignora_el_filtro(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    otra = active_user(b, name="Ana")
    found = [x["profile_id"] for x in discover(a, viewer, q="ana", intereses="musica")]
    assert found == [otra]
