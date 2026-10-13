"""Genera la biblioteca de textos del tránsito del día (spec B4 v2) UNA sola vez con la IA.

72 textos: tipo de tránsito (Luna del día respecto del Sol natal) × signo de la Luna.
Escribe app/content/transitos_v1.json marcado como "pendiente de revisión de Pablo".
Después se edita a mano; la app nunca llama a la IA para esto.

Uso: .venv/bin/python scripts/generate_transit_texts.py   (necesita OPENROUTER_API_KEY y OPENROUTER_MODEL)

Con `--por-registro` (spec X2) agrega a la biblioteca existente las 4 versiones por registro
(directo, práctico, analítico, intuitivo: 288 textos) en la clave `por_registro`, sin tocar `textos`.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.astro import ZODIAC_SIGNS  # noqa: E402
from app.config import settings  # noqa: E402
from app.content.transits import ASPECTS  # noqa: E402
from app.llm import complete  # noqa: E402
from app.personalization.style import load_config  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "app" / "content" / "transitos_v1.json"

MEANING = {
    "conjunción": "la Luna pasa por tu mismo signo solar: energía y emociones van juntas",
    "sextil": "la Luna hace un ángulo amable con tu Sol: día fluido para conectar y proponer",
    "cuadratura": "la Luna hace tensión con tu Sol: emociones y voluntad pueden chocar",
    "trígono": "la Luna hace armonía con tu Sol: todo fluye más fácil",
    "oposición": "la Luna está enfrente de tu Sol (tu luna llena personal): emociones a flor de piel, foco en los otros",
    "sin aspecto mayor": "la Luna no hace un ángulo fuerte con tu Sol: día tranquilo, sin grandes empujones",
}

SYSTEM = (
    "Sos la voz editorial de Destiny, una app argentina de conexiones con astrología. Escribí en castellano "
    "rioplatense, con voseo, cálido y concreto, sin jerga difícil. Te doy el tránsito del día de una persona "
    "(la Luna del día respecto de su Sol natal) y el signo por el que pasa la Luna. Devolvé SOLO un JSON con "
    '{"titulo": "...", "texto": "..."}: titulo de 2 a 4 palabras; texto de 1 o 2 oraciones (máximo 220 '
    "caracteres) con un consejo práctico para el día, que combine el tránsito con el tono del signo lunar. "
    "Nada de predicciones cerradas, nada de miedo, no menciones que sos una IA. Texto plano, sin markdown."
)


def write_one(system: str, aspect: str, sign: str) -> dict | None:
    user = json.dumps({"transito": aspect, "significado": MEANING[aspect], "luna_en": sign}, ensure_ascii=False)
    for _ in range(3):
        result = complete(system, user, 400)
        try:
            data = json.loads(result.text.strip().removeprefix("```json").removesuffix("```")) if result else None
        except ValueError:
            data = None
        if data and data.get("titulo") and data.get("texto") and len(data["texto"]) <= 280:
            return {"titulo": data["titulo"].strip(), "texto": data["texto"].strip()}
    return None


def main_por_registro():
    library = json.loads(OUT.read_text())
    estilos = load_config()["registro"]["estilos"]
    jobs = [(r, a, s) for r in estilos for a in ASPECTS for s in ZODIAC_SIGNS]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda j: write_one(f"{SYSTEM} {estilos[j[0]]['instruccion']}", j[1], j[2]), jobs))
    por_registro = {}
    for (registro, aspect, sign), entry in zip(jobs, results):
        if entry:
            por_registro.setdefault(registro, {}).setdefault(aspect, {})[sign] = entry
        else:
            print(registro, aspect, sign, "FALTA")
    library["por_registro"] = por_registro
    library["por_registro_generado_con"] = settings.openrouter_model
    OUT.write_text(json.dumps(library, ensure_ascii=False, indent=1) + "\n")
    print(f"Escrito {OUT}: {sum(1 for e in results if e)}/{len(jobs)} textos por registro")


def main():
    if not (settings.openrouter_api_key and settings.openrouter_model):
        sys.exit("Faltan OPENROUTER_API_KEY / OPENROUTER_MODEL en apps/api/.env")
    textos = {}
    for aspect in ASPECTS:
        textos[aspect] = {}
        for sign in ZODIAC_SIGNS:
            user = json.dumps({"transito": aspect, "significado": MEANING[aspect], "luna_en": sign}, ensure_ascii=False)
            for _ in range(3):
                result = complete(SYSTEM, user, 400)
                try:
                    data = json.loads(result.text.strip().removeprefix("```json").removesuffix("```")) if result else None
                except ValueError:
                    data = None
                if data and data.get("titulo") and data.get("texto") and len(data["texto"]) <= 280:
                    textos[aspect][sign] = {"titulo": data["titulo"].strip(), "texto": data["texto"].strip()}
                    break
            print(aspect, sign, "ok" if sign in textos[aspect] else "FALTA")
    out = Path(__file__).resolve().parents[1] / "app" / "content" / "transitos_v1.json"
    library = {
        "version": "v1",
        "revisado_por_pablo": False,
        "generado_con": settings.openrouter_model,
        "fecha": date.today().isoformat(),
        "notas": "Textos del tránsito del día (spec B4 v2). Redactados una vez con IA; editar a mano lo que haga falta y marcar revisado_por_pablo: true cuando Pablo los apruebe.",
        "textos": textos,
    }
    out.write_text(json.dumps(library, ensure_ascii=False, indent=1) + "\n")
    print(f"Escrito {out}")


if __name__ == "__main__":
    if not (settings.openrouter_api_key and settings.openrouter_model):
        sys.exit("Faltan OPENROUTER_API_KEY / OPENROUTER_MODEL en apps/api/.env")
    main_por_registro() if "--por-registro" in sys.argv else main()
