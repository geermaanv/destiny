"""Biblioteca de textos de Mi carta (spec A8).

`carta_v1.json`: un texto por indicador × signo y por indicador × casa. Generada una vez con
`scripts/generate_carta_texts.py`; editable a mano; Pablo la revisa (`revisado_por_pablo`).
"""

import json
from functools import lru_cache
from pathlib import Path

LIBRARY_PATH = Path(__file__).parent / "carta_v1.json"


@lru_cache(maxsize=1)
def load_library() -> dict:
    return json.loads(LIBRARY_PATH.read_text())
