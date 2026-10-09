"""Spec B6-calendario-memoria: mes, detalle del día, notas y próximos 10 eventos."""

from tests.helpers import verified_user


def test_mes_completo(client):
    pid = verified_user(client, "5491111111111")
    dias = client.get("/calendar/2026/2", params={"profile_id": pid}).json()
    assert len(dias) == 28 and dias[0]["date"] == "2026-02-01"


def test_proximos_10_eventos_desde_la_fecha(client):
    pid = verified_user(client, "5491111111111")
    eventos = client.get("/calendar/upcoming", params={"profile_id": pid, "from": "2026-10-08"}).json()
    assert len(eventos) == 10
    assert eventos[0]["start"] >= "2026-10-08"
    assert all(e["title"] and e["text"] for e in eventos)
    inicios = [e["start"] for e in eventos]
    assert inicios == sorted(inicios)
    assert all(e["start"] <= e["end"] for e in eventos)


def test_notas_del_dia_y_marca_en_eventos(client):
    pid = verified_user(client, "5491111111111")
    evento = client.get("/calendar/upcoming", params={"profile_id": pid, "from": "2026-10-08"}).json()[0]
    client.post(f"/calendar/day/{evento['start']}/annotations", json={"profile_id": pid, "text": "Cena con amigos"})
    dia = client.get(f"/calendar/day/{evento['start']}", params={"profile_id": pid}).json()
    assert dia["annotations"][0]["text"] == "Cena con amigos"
    assert dia["transits"][0]["title"]
    actualizado = client.get("/calendar/upcoming", params={"profile_id": pid, "from": "2026-10-08"}).json()[0]
    assert actualizado["has_notes"] is True


def test_calendario_de_otro_esta_prohibido(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    assert b.get("/calendar/upcoming", params={"profile_id": pid_a}).status_code == 403
