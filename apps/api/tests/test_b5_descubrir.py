"""Spec B5-pantalla-descubrir + motor: lista curada por contexto, ejes y explicación."""

from tests.helpers import create_profile, verified_user


def test_descubrir_exige_estar_verificado(new_client):
    a = new_client()
    pid = create_profile(a)
    assert a.get("/discover", params={"viewer_id": pid}).status_code == 401


def test_lista_ordenada_por_compatibilidad_con_ejes(new_client):
    viewer_client = new_client()
    for i, fecha in enumerate(["1985-01-10", "1992-07-22", "1979-11-30"]):
        verified_user(new_client(), f"54911000000{i}", name=f"P{i}", birth_date=fecha)
    viewer = verified_user(viewer_client, "5499999999999", name="Yo")
    lista = viewer_client.get("/discover", params={"viewer_id": viewer, "context": "pareja"}).json()
    assert len(lista) == 3
    totales = [c["compatibility_pct"] for c in lista]
    assert totales == sorted(totales, reverse=True)
    assert set(lista[0]["axes"]) == {"atraccion", "afecto", "comunicacion", "compromiso"}
    assert lista[0]["preview"].startswith("Fuerte en ")
    assert lista[0]["relationship"] == "pareja"


def test_contexto_invalido_se_rechaza(new_client):
    a = new_client()
    pid = verified_user(a, "5491111111111")
    assert a.get("/discover", params={"viewer_id": pid, "context": "otro"}).status_code == 422


def test_no_se_ve_uno_mismo(new_client):
    a = new_client()
    pid = verified_user(a, "5491111111111", name="Ana")
    assert a.get("/discover", params={"viewer_id": pid}).json() == []


def test_explicacion_nombra_los_ejes_relevantes_del_contexto(new_client):
    a, b = new_client(), new_client()
    otro = verified_user(a, "5491111111111", name="Ana")
    yo = verified_user(b, "5492222222222", name="Beto")
    texto = b.get(f"/discover/{otro}/explanation", params={"viewer_id": yo, "context": "laboral"}).json()["text"]
    assert texto.startswith("Para trabajar juntos")
    assert "química" not in texto  # en laboral la atracción no pesa
