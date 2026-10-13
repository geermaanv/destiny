"""Genera la biblioteca de textos de Mi carta (spec A8) UNA sola vez con la IA.

Un texto por indicador × signo y por indicador × casa, según config/dimensiones_v1.json.
Escribe app/content/carta_v1.json marcado como "pendiente de revisión de Pablo"; después se edita a mano.
La app nunca llama a la IA para estos textos (solo para la síntesis, que se cachea).

Uso: .venv/bin/python scripts/generate_carta_texts.py   (necesita OPENROUTER_API_KEY y OPENROUTER_MODEL)
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.astro import ZODIAC_SIGNS  # noqa: E402
from app.config import settings  # noqa: E402
from app.llm import complete  # noqa: E402
from app.natal.dimensions import load_config  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "app" / "content" / "carta_v1.json"
HOUSES = {
    1: "la identidad y la forma de presentarse", 2: "los recursos, el dinero y lo que se valora",
    3: "la comunicación, el aprendizaje y el entorno cercano", 4: "el hogar, la familia y las raíces",
    5: "la creatividad, el placer y el romance", 6: "la rutina, el trabajo diario y la salud",
    7: "la pareja y los vínculos de a dos", 8: "la intimidad, las crisis y lo compartido",
    9: "los viajes, los estudios y las creencias", 10: "la carrera, la vocación y la imagen pública",
    11: "los amigos, los grupos y los proyectos a futuro", 12: "el mundo interior, el descanso y lo oculto",
}
SYSTEM = (
    "Sos la voz editorial de Destiny, una app argentina de autoconocimiento con astrología. Escribí en castellano "
    "rioplatense, con voseo, cálido y concreto, sin jerga difícil. Te doy un rasgo de la carta natal de una persona. "
    'Devolvé SOLO un JSON {"texto": "..."}: 1 o 2 oraciones (máximo 220 caracteres) hablándole a la persona sobre '
    "qué dice ese rasgo de ella en el área indicada. Lectura simbólica para reflexionar: nada de predicciones, "
    "diagnósticos ni miedo. No menciones que sos una IA. Texto plano, sin markdown."
)


def write_one(user: dict) -> str | None:
    payload = json.dumps(user, ensure_ascii=False)
    for _ in range(3):
        result = complete(SYSTEM, payload, 400)
        try:
            data = json.loads(result.text.strip().removeprefix("```json").removesuffix("```")) if result else None
        except ValueError:
            data = None
        if data and data.get("texto") and len(data["texto"].strip()) <= 280:
            return data["texto"].strip()
    return None


def main():
    if not (settings.openrouter_api_key and settings.openrouter_model):
        sys.exit("Faltan OPENROUTER_API_KEY / OPENROUTER_MODEL en apps/api/.env")
    cfg = load_config()
    jobs = []
    for key, dim in cfg["dimensiones"].items():
        for ind in dim["indicadores"]:
            point = ind["punto"]
            info = cfg["puntos"][point]
            base = {"area": dim["nombre"], "pregunta": dim["pregunta"], "punto": info["nombre"], "que_representa": info["palabra"]}
            if ind.get("signo"):
                jobs += [("signo", point, sign, base | {"signo": sign}) for sign in ZODIAC_SIGNS]
            if ind.get("casa"):
                jobs += [("casa", point, str(h), base | {"casa": h, "tema_de_la_casa": HOUSES[h]}) for h in HOUSES]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda j: write_one(j[3]), jobs))
    library = {
        "version": "v1",
        "revisado_por_pablo": False,
        "generado_con": settings.openrouter_model,
        "fecha": date.today().isoformat(),
        "notas": "Textos de Mi carta (spec A8). Redactados una vez con IA; editar a mano lo que haga falta y marcar revisado_por_pablo: true cuando Pablo los apruebe.",
        "signo": {},
        "casa": {},
    }
    missing = 0
    for (kind, point, slot, _), text in zip(jobs, results):
        if text is None:
            missing += 1
            print("FALTA", kind, point, slot)
            continue
        library[kind].setdefault(point, {})[slot] = text
    OUT.write_text(json.dumps(library, ensure_ascii=False, indent=1) + "\n")
    print(f"Escrito {OUT}: {len(jobs) - missing}/{len(jobs)} textos")


if __name__ == "__main__":
    main()
