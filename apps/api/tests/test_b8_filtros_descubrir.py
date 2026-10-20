"""Spec B8: buscar y filtrar en Descubrir (sistema, compatibilidad mínima, edad, género y "Mostrame")."""

from tests.helpers import complete_personality
from tests.test_a10_verificacion_opcional import active_user


def prefs(client, pid, gender, show_me=None, appear_in=None, **extra):
    body = {"gender": gender, "show_me": show_me or [], "appear_in": appear_in or [], **extra}
    r = client.post(f"/profiles/{pid}/preferences", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def discover(client, viewer, **params):
    r = client.get("/discover", params={"viewer_id": viewer, **params})
    assert r.status_code == 200, r.text
    return {x["profile_id"]: x for x in r.json()}


# 1
def test_guardar_preferencias(client):
    pid = active_user(client)
    out = prefs(client, pid, "no_binario", ["mujer", "no_binario"], ["mujer"], gender_detail="género fluido", show_gender=True)
    me = client.get(f"/profiles/{pid}").json()
    assert me["gender"] == "no_binario" and me["gender_detail"] == "género fluido"
    assert me["show_me"] == ["mujer", "no_binario"] and me["appear_in"] == ["mujer"] and me["show_gender"] is True
    assert out["gender"] == "no_binario"
    for malo in [{"gender": "otro"}, {"gender": "mujer", "show_me": ["gatos"]}, {"gender": "mujer", "gender_detail": "x" * 41}]:
        assert client.post(f"/profiles/{pid}/preferences", json=malo).status_code == 422


# 2
def test_mostrame_es_mutuo_en_pareja(new_client):
    a, b, c = new_client(), new_client(), new_client()
    el = active_user(a, name="Hugo")
    prefs(a, el, "hombre", ["mujer"])
    ella = active_user(b, name="Ana")
    prefs(b, ella, "mujer", ["hombre"])
    lesbiana = active_user(c, name="Lola")
    prefs(c, lesbiana, "mujer", ["mujer"])
    found = discover(a, el, context="pareja")
    assert ella in found and lesbiana not in found
    assert el not in discover(c, lesbiana, context="pareja")


# 3
def test_no_binario_elige_donde_aparecer(new_client):
    a, b, c = new_client(), new_client(), new_client()
    busca_mujeres = active_user(a, name="Hugo")
    prefs(a, busca_mujeres, "hombre", ["mujer"])
    nb = active_user(b, name="Alex")
    prefs(b, nb, "no_binario", ["hombre", "mujer", "no_binario"], ["mujer"])
    nb2 = active_user(c, name="Sam")
    prefs(c, nb2, "no_binario", ["hombre", "mujer", "no_binario"], ["hombre"])
    found = discover(a, busca_mujeres, context="pareja")
    assert nb in found and nb2 not in found


# 4
def test_fuera_de_pareja_no_filtra_genero(new_client):
    a, b = new_client(), new_client()
    el = active_user(a, name="Hugo")
    prefs(a, el, "hombre", ["mujer"])
    otro = active_user(b, name="Beto")
    prefs(b, otro, "hombre", ["mujer"])
    assert otro in discover(a, el, context="amistad")
    assert otro not in discover(a, el, context="pareja")


# 5
def test_sin_mostrame_ve_a_todos_y_sin_genero_no_aparece_para_quien_filtra(new_client):
    a, b, c = new_client(), new_client(), new_client()
    abierto = active_user(a, name="Vera")  # sin preferencias
    ella = active_user(b, name="Ana")
    prefs(b, ella, "mujer", ["hombre", "mujer"])
    sin_genero = active_user(c, name="Cami")
    found = discover(a, abierto, context="pareja")
    assert sin_genero in found
    assert abierto not in discover(b, ella, context="pareja")  # no sabemos su género


# 6
def test_edad(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    joven = active_user(b, name="Juli", birth_date="2004-03-10")
    grande = active_user(c, name="Gabi", birth_date="1970-03-10")
    found = discover(a, viewer, edad_min=18, edad_max=30)
    assert joven in found and grande not in found
    r = a.get("/discover", params={"viewer_id": viewer, "edad_min": 40, "edad_max": 30})
    assert r.status_code == 422


# 7
def test_compatibilidad_minima(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    uno = active_user(b, name="Uno", birth_date="1985-01-15")
    dos = active_user(c, name="Dos", birth_date="1992-08-03")
    todos = discover(a, viewer)
    pcts = sorted([todos[uno]["compatibility_pct"], todos[dos]["compatibility_pct"]])
    assert pcts[0] < pcts[1], "los casos de prueba necesitan dos porcentajes distintos"
    alto = discover(a, viewer, min_pct=pcts[1])
    assert len(alto) == 1 and all(x["compatibility_pct"] >= pcts[1] for x in alto.values())


# 8
def test_sistema_personalidad(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    con_test = active_user(b, name="Tomi")
    sin_test = active_user(c, name="Nico")
    r = a.get("/discover", params={"viewer_id": viewer, "sistemas": "personalidad"})
    assert r.status_code == 409
    complete_personality(a, viewer)
    complete_personality(b, con_test)
    found = discover(a, viewer, sistemas="personalidad")
    assert con_test in found and sin_test not in found
    assert found[con_test]["compatibility_pct"] == round(found[con_test]["personality"]["total"])
    assert found[con_test]["astrology_pct"] == discover(a, viewer)[con_test]["systems"]["astrologia"]["total"]


# 9
def test_busqueda_por_nombre(new_client):
    a, b, c = new_client(), new_client(), new_client()
    viewer = active_user(a, name="Vera")
    jose = active_user(b, name="José Luis", birth_date="1960-01-01")
    otra = active_user(c, name="Marta")
    found = discover(a, viewer, q="jose", edad_max=30, min_pct=100)
    assert list(found) == [jose]
    assert otra not in found


# 10
def test_genero_publico_solo_si_se_elige(new_client):
    a, b = new_client(), new_client()
    viewer = active_user(a, name="Vera")
    ana = active_user(b, name="Ana")
    prefs(b, ana, "mujer", ["hombre"], gender_detail="mujer trans")
    assert discover(a, viewer, context="amistad")[ana]["gender_label"] is None
    prefs(b, ana, "mujer", ["hombre"], gender_detail="mujer trans", show_gender=True)
    assert discover(a, viewer, context="amistad")[ana]["gender_label"] == "mujer trans"
