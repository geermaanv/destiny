"""Spec X1-redaccion-con-ia: explicaciones y rompehielos con IA vía OpenRouter (simulado)."""

import json

import httpx
import pytest

from tests.helpers import verified_user


class FakeOpenRouter:
    """Reemplaza a OpenRouter: registra cada pedido y responde lo que se le diga."""

    def __init__(self):
        self.requests: list[dict] = []
        self.reply: str | None = "Los une una forma de hablar muy parecida. Lo que más van a tener que cuidar es el compromiso."
        self.status = 200
        self.raise_timeout = False

    def handler(self, request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        self.requests.append({"url": str(request.url), "headers": dict(request.headers), "body": body})
        if self.raise_timeout:
            raise httpx.ReadTimeout("timeout", request=request)
        if self.status != 200:
            return httpx.Response(self.status, json={"error": "boom"})
        return httpx.Response(
            200,
            json={
                "model": body["model"],
                "choices": [{"message": {"content": self.reply}}],
                "usage": {"prompt_tokens": 321, "completion_tokens": 45},
            },
        )


@pytest.fixture
def openrouter(monkeypatch):
    from app import llm
    from app.config import settings

    fake = FakeOpenRouter()
    monkeypatch.setattr(settings, "openrouter_api_key", "test-or-key")
    monkeypatch.setattr(settings, "openrouter_model", "test/modelo-barato")
    monkeypatch.setattr(llm, "TRANSPORT", httpx.MockTransport(fake.handler))
    return fake


@pytest.fixture
def sin_key(monkeypatch):
    from app import llm
    from app.config import settings

    def no_network(request):
        raise AssertionError("no debería llamar a la red sin key")

    monkeypatch.setattr(settings, "openrouter_api_key", None)
    monkeypatch.setattr(llm, "TRANSPORT", httpx.MockTransport(no_network))


@pytest.fixture
def pareja(new_client):
    a, b = new_client(), new_client()
    ana = verified_user(a, "5491111111111", name="Ana", birth_date="1990-05-20")
    beto = verified_user(b, "5492222222222", name="Beto", birth_date="1985-11-03")
    return a, ana, b, beto


def _explain(client, viewer, candidate, context="pareja"):
    return client.get(f"/discover/{candidate}/explanation", params={"viewer_id": viewer, "context": context})


def test_sin_key_usa_plantilla_sin_llamar_a_la_red(sin_key, pareja):
    _, ana, b, beto = pareja
    r = _explain(b, beto, ana)
    assert r.status_code == 200 and r.json()["text"].startswith("Como pareja")


def test_con_key_llama_a_openrouter_con_el_modelo_configurado(openrouter, pareja):
    _, ana, b, beto = pareja
    _explain(b, beto, ana)
    req = openrouter.requests[0]
    assert req["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert req["headers"]["authorization"] == "Bearer test-or-key"
    assert req["body"]["model"] == "test/modelo-barato"


def test_no_se_mandan_datos_personales(openrouter, pareja):
    a, ana, b, beto = pareja
    _explain(b, beto, ana)
    a.post("/matches", json={"profile_a_id": ana, "profile_b_id": beto})
    for req in openrouter.requests:
        enviado = json.dumps(req["body"], ensure_ascii=False)
        for dato in ["Ana", "Beto", "1990", "1985", "05-20", "5491111111111", "Buenos Aires", "-34."]:
            assert dato not in enviado, dato


def test_se_usa_el_texto_de_la_ia(openrouter, pareja):
    _, ana, b, beto = pareja
    openrouter.reply = '  "Los une la forma de hablar."  '
    assert _explain(b, beto, ana).json()["text"] == "Los une la forma de hablar."


@pytest.mark.parametrize("falla", ["error", "timeout", "vacio"])
def test_si_la_ia_falla_se_usa_la_plantilla(openrouter, pareja, falla):
    _, ana, b, beto = pareja
    if falla == "error":
        openrouter.status = 500
    elif falla == "timeout":
        openrouter.raise_timeout = True
    else:
        openrouter.reply = "   "
    r = _explain(b, beto, ana)
    assert r.status_code == 200 and r.json()["text"].startswith("Como pareja")


def test_texto_largo_se_recorta_por_oracion(openrouter, pareja):
    _, ana, b, beto = pareja
    openrouter.reply = " ".join(["Esta es una oración bastante larga sobre lo que los une a los dos."] * 20)
    texto = _explain(b, beto, ana).json()["text"]
    assert len(texto) <= 420 and texto.endswith(".")


def test_misma_pareja_y_vinculo_usa_la_cache(openrouter, pareja):
    _, ana, b, beto = pareja
    primero = _explain(b, beto, ana).json()["text"]
    segundo = _explain(b, beto, ana).json()["text"]
    assert primero == segundo and len(openrouter.requests) == 1


def test_otro_vinculo_es_otra_llamada(openrouter, pareja):
    _, ana, b, beto = pareja
    _explain(b, beto, ana, "pareja")
    _explain(b, beto, ana, "laboral")
    assert len(openrouter.requests) == 2


def test_rompehielos_se_pide_una_vez_y_queda_como_primer_mensaje(openrouter, pareja):
    a, ana, b, beto = pareja
    openrouter.reply = "¿Vos también sos de las personas que hablan hasta tarde?"
    m = a.post("/matches", json={"profile_a_id": ana, "profile_b_id": beto}).json()
    b.post(f"/matches/{m['id']}/accept", json={"profile_id": beto})
    a.post("/matches", json={"profile_a_id": ana, "profile_b_id": beto})
    msgs = a.get(f"/chats/{m['id']}/messages").json()
    assert msgs[0]["sender"] == "system_icebreaker"
    assert msgs[0]["text"] == "¿Vos también sos de las personas que hablan hasta tarde?"
    assert len(openrouter.requests) == 1


def test_se_registra_modelo_y_tokens(openrouter, pareja):
    from app.database import SessionLocal
    from app.models import AIText

    _, ana, b, beto = pareja
    _explain(b, beto, ana)
    with SessionLocal() as db:
        row = db.query(AIText).one()
        assert row.model == "test/modelo-barato"
        assert (row.prompt_tokens, row.completion_tokens) == (321, 45)


def test_la_ia_recibe_fortalezas_y_debilidades_ya_calculadas(openrouter, pareja):
    _, ana, b, beto = pareja
    _explain(b, beto, ana, "laboral")
    facts = json.loads(openrouter.requests[0]["body"]["messages"][1]["content"])
    ejes = facts["ejes"]
    assert set(facts["niveles"]) == set(ejes)
    for eje, valor in ejes.items():
        assert facts["niveles"][eje] == ("alto" if valor >= 60 else "bajo" if valor < 40 else "medio")
    from app.synastry.engine import load_config

    cfg = load_config()
    pesos = cfg["tipos_de_relacion"]["tipos"]["laboral"]["pesos"]
    relevantes = [e for e in ejes if pesos[e] >= cfg["explicacion"]["peso_minimo_eje"]]
    assert facts["lo_que_mas_los_une"] == max(relevantes, key=ejes.get)
    assert facts["lo_que_tienen_que_trabajar"] == min(relevantes, key=ejes.get)


def test_pide_razonamiento_desactivado(openrouter, pareja):
    _, ana, b, beto = pareja
    _explain(b, beto, ana)
    assert openrouter.requests[0]["body"]["reasoning"] == {"enabled": False}
