"""Compara modelos de OpenRouter para las explicaciones y rompehielos (spec X1).

Usa los mismos prompts que la app y casos sintéticos (cartas de ejemplo, sin datos
de personas reales). Escribe docs/referencias/comparacion-modelos-ia.md con los
textos, el tiempo de respuesta y el costo estimado.

Uso: .venv/bin/python scripts/compare_llm_models.py [modelo1 modelo2 ...]
(necesita OPENROUTER_API_KEY en apps/api/.env)
"""

import json
import sys
import time
from datetime import date, time as dtime
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import explainer, icebreaker  # noqa: E402
from app.config import settings  # noqa: E402
from app.llm import OPENROUTER_URL, clean  # noqa: E402
from app.synastry import ai_facts  # noqa: E402
from app.synastry.chart import compute_chart  # noqa: E402
from app.synastry.engine import synastry  # noqa: E402

DEFAULT_MODELS = [
    "qwen/qwen3.7-flash",
    "mistralai/mistral-small-3.2-24b-instruct",
    "openai/gpt-5-nano",
    "google/gemini-2.5-flash-lite",
    "anthropic/claude-haiku-5.5",
    "deepseek/deepseek-v3.2",
]

BA = (-34.6131, -58.3772, "America/Argentina/Buenos_Aires")
CASES = [
    ("Pareja", "pareja", (date(1990, 5, 20), dtime(14, 30)), (date(1988, 11, 3), dtime(21, 45))),
    ("Amistad", "amistad", (date(1995, 2, 11), dtime(9, 10)), (date(1994, 8, 27), dtime(18, 0))),
    ("Trabajo", "laboral", (date(1979, 7, 4), dtime(7, 50)), (date(1986, 12, 15), dtime(23, 20))),
]


def facts_for(context, a, b):
    ca = compute_chart(a[0], a[1], True, *BA)
    cb = compute_chart(b[0], b[1], True, *BA)
    return ai_facts(synastry(ca, cb, context))


def prices():
    data = httpx.get("https://openrouter.ai/api/v1/models", timeout=20).json()["data"]
    return {m["id"]: (float(m["pricing"]["prompt"]), float(m["pricing"]["completion"])) for m in data}


def call(model, system, user, max_chars):
    started = time.monotonic()
    r = httpx.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {settings.openrouter_api_key}", "X-Title": "Destiny (comparacion)"},
        json={"model": model, "max_tokens": 300, "temperature": 0.7, "reasoning": {"enabled": False},
              "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]},
        timeout=60,
    )
    elapsed = time.monotonic() - started
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}: {r.text[:200]}", "seconds": elapsed}
    data = r.json()
    text = clean(data["choices"][0]["message"]["content"] or "")
    usage = data.get("usage") or {}
    return {"text": text, "seconds": elapsed, "in": usage.get("prompt_tokens", 0), "out": usage.get("completion_tokens", 0),
            "too_long": len(text) > max_chars}


def main():
    if not settings.openrouter_api_key:
        sys.exit("Falta OPENROUTER_API_KEY en apps/api/.env")
    models = sys.argv[1:] or DEFAULT_MODELS
    price = prices()
    rows, summary = [], []
    for model in models:
        if model not in price:
            summary.append((model, None, None, None, "no existe en OpenRouter"))
            continue
        cost, secs, errors = 0.0, [], 0
        for title, context, a, b in CASES:
            facts = json.dumps(facts_for(context, a, b), ensure_ascii=False)
            for kind, mod in (("Explicación", explainer), ("Rompehielos", icebreaker)):
                res = call(model, mod.EDITORIAL_GUIDELINE, facts, mod.MAX_CHARS)
                if "error" in res:
                    errors += 1
                    rows.append((model, title, kind, f"⚠️ {res['error']}", res["seconds"]))
                    continue
                pin, pout = price[model]
                cost += res["in"] * pin + res["out"] * pout
                secs.append(res["seconds"])
                flag = " ⚠️ (más largo que el máximo)" if res["too_long"] else ""
                rows.append((model, title, kind, res["text"] + flag, res["seconds"]))
        per_1000 = cost / max(1, len(CASES) * 2 - errors) * 1000
        summary.append((model, per_1000, sum(secs) / len(secs) if secs else None, errors, ""))

    out = Path(__file__).resolve().parents[3] / "docs" / "referencias" / "comparacion-modelos-ia.md"
    lines = [
        "# Comparación de modelos de IA (OpenRouter) para explicaciones y rompehielos",
        "",
        f"Generado por `apps/api/scripts/compare_llm_models.py` el {date.today().isoformat()}, con los mismos prompts "
        "que usa la app (spec X1) y 3 casos sintéticos (pareja, amistad, trabajo). Precios de la API pública de OpenRouter.",
        "",
        "| Modelo | USD cada 1000 textos | Segundos promedio | Errores |",
        "|---|---|---|---|",
    ]
    for model, per_1000, avg, errors, note in summary:
        if per_1000 is None:
            lines.append(f"| `{model}` | — | — | {note} |")
        else:
            lines.append(f"| `{model}` | {per_1000:.4f} | {avg if avg is None else round(avg, 1)} | {errors} |")
    for model in models:
        lines += ["", f"## `{model}`", ""]
        for m, title, kind, text, secs in rows:
            if m == model:
                lines.append(f"- **{title} · {kind}** ({secs:.1f} s): {text}")
    out.write_text("\n".join(lines) + "\n")
    print(f"Escrito {out}")
    for model, per_1000, avg, errors, note in summary:
        print(model, per_1000, avg, errors, note)


if __name__ == "__main__":
    main()
