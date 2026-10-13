"""Síntesis de cada dimensión de Mi carta (spec A8), redactada con IA en el estilo de la persona.

La IA recibe solo la dimensión y los textos de los fundamentos ya calculados (nunca nombre,
fecha, lugar ni teléfono). Sin key o si falla, plantilla con los dos primeros fundamentos.
"""

import json

from app.explainer import Written
from app.llm import complete, is_configured
from app.natal.dimensions import load_config

GUIDELINE = (
    "Sos la voz editorial de Destiny, una app argentina de autoconocimiento y conexiones con astrología. "
    "Escribí en castellano rioplatense, con voseo, cálido y concreto, sin jerga astrológica difícil. "
    "Te doy una dimensión de la vida de una persona y los rasgos que salen de su carta natal (ya calculados). "
    "Escribí una síntesis de 2 a 4 oraciones (máximo 80 palabras) que integre esos rasgos y responda la pregunta "
    "de la dimensión, hablándole a la persona. No agregues rasgos que no estén en los datos. Nada de predicciones "
    "ni diagnósticos: es una lectura simbólica para reflexionar. No menciones que sos una IA. "
    "Texto plano, sin markdown. Respondé solo con el texto."
)


def template_synthesis(dimension: dict) -> str:
    return " ".join(f["texto"] for f in dimension["fundamentos"][:2])


def synthesize(dimension: dict, approximate: bool, style_instructions: str) -> Written:
    max_chars = load_config()["sintesis"]["max_caracteres"]
    if is_configured():
        facts = {
            "dimension": dimension["nombre"],
            "pregunta": dimension["pregunta"],
            "rasgos": [f["texto"] for f in dimension["fundamentos"]],
            "aproximado_sin_hora_exacta": approximate,
        }
        result = complete(f"{GUIDELINE} {style_instructions}".strip(), json.dumps(facts, ensure_ascii=False), max_chars)
        if result:
            return Written(result.text, result)
    return Written(template_synthesis(dimension), None)
