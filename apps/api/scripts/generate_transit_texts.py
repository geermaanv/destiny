"""Genera la biblioteca de textos del tránsito del día (spec B4 v2) UNA sola vez con la IA.

72 textos: tipo de tránsito (Luna del día respecto del Sol natal) × signo de la Luna.
Escribe app/content/transitos_v1.json marcado como "pendiente de revisión de Pablo".
Después se edita a mano; la app nunca llama a la IA para esto.

Uso: .venv/bin/python scripts/generate_transit_texts.py   (necesita OPENROUTER_API_KEY y OPENROUTER_MODEL)
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.astro import ZODIAC_SIGNS  # noqa: E402
from app.config import settings  # noqa: E402
from app.content.transits import ASPECTS  # noqa: E402
from app.llm import complete  # noqa: E402

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
    main()
