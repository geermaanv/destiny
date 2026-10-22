"""Validaciones compartidas (spec R1, hallazgos del agente breaker)."""

import re
from datetime import date
from typing import Annotated
from zoneinfo import available_timezones

from fastapi import HTTPException
from pydantic import BeforeValidator

# Caracteres nulos (Postgres no los acepta) e invisibles (espacios de ancho cero, BOM).
_INVISIBLE = re.compile("[\x00​‌‍⁠﻿]")


def clean_text(value):
    if not isinstance(value, str):
        return value
    return _INVISIBLE.sub("", value).strip()


# Texto ya limpio; con min_length=1 en el Field, uno que queda vacío es inválido.
CleanStr = Annotated[str, BeforeValidator(clean_text)]

MIN_DAY = date(1900, 1, 1)
MAX_DAY = date(2100, 12, 31)
TIMEZONES = available_timezones()


def check_day(day: date | None) -> date | None:
    """Fechas fuera de 1900–2100 → 422 (antes, errores 500 por desbordes en los cálculos)."""
    if day is not None and not MIN_DAY <= day <= MAX_DAY:
        raise HTTPException(status_code=422, detail="La fecha tiene que estar entre 1900 y 2100")
    return day
