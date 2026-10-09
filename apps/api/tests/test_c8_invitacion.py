"""Spec C8-invitacion-whatsapp: adelanto por signo, mensaje en primera persona y revelación."""

from tests.helpers import create_profile, verify, verified_user


def test_invitacion_arma_mensaje_en_primera_persona(client):
    pid = verified_user(client, "5491111111111", name="Ana")
    r = client.post("/invitations", json={"inviter_id": pid, "friend_name": "Juan", "friend_sun_sign": "Géminis"})
    body = r.json()
    assert r.status_code == 201
    assert body["message"].startswith("¡Hola Juan! Te invito a Destiny")
    assert "(Géminis)" in body["message"]
    assert "sus soles" not in body["message"]
    assert "https://destiny.test/onboarding/invitacion?ref=" in body["message"]
    assert body["whatsapp_url"].startswith("https://wa.me/?text=")


def test_invitar_en_nombre_de_otro_esta_prohibido(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111")
    verified_user(b, "5492222222222")
    r = b.post("/invitations", json={"inviter_id": pid_a, "friend_name": "Juan", "friend_sun_sign": "Leo"})
    assert r.status_code == 403


def test_invitado_ve_el_adelanto_y_despues_la_revelacion(new_client):
    a, b = new_client(), new_client()
    pid_a = verified_user(a, "5491111111111", name="Ana")
    ref = a.post("/invitations", json={"inviter_id": pid_a, "friend_name": "Juan", "friend_sun_sign": "Leo"}).json()["ref_id"]
    assert b.get(f"/invitations/{ref}").json()["friend_name"] == "Juan"
    pid_b = create_profile(b, birth_date="1991-08-10", name="Juan")
    verify(b, pid_b, "5492222222222")
    reveal = b.get(f"/invitations/{ref}/reveal", params={"invitee_id": pid_b}).json()
    assert 0 <= reveal["percentage"] <= 100 and reveal["text"]


def test_invitaciones_viejas_con_gemini_siguen_funcionando():
    from app.astro import approximate_longitude_for_sign

    assert approximate_longitude_for_sign("Gemini") == approximate_longitude_for_sign("Géminis") == 75
