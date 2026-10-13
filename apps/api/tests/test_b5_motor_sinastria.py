"""Carta natal y resultado del motor para la app (spec B5, motor reemplazado por el oficial de la spec A7)."""

from datetime import date, time

import pytest

from app.synastry.chart import compute_chart
from app.synastry.engine import SCORED_AXES, load_config, synastry

SIGNS = ["Aries", "Tauro", "Géminis", "Cáncer", "Leo", "Virgo", "Libra", "Escorpio", "Sagitario", "Capricornio", "Acuario", "Piscis"]


def _sign(lon):
    return SIGNS[int(lon // 30)], round(lon % 30)


@pytest.fixture(scope="module")
def cartas():
    a = compute_chart(date(1990, 5, 20), time(14, 30), True, -34.6131, -58.3772, "America/Argentina/Buenos_Aires")
    b = compute_chart(date(1988, 11, 3), time(21, 45), True, -32.9468, -60.6393, "America/Argentina/Cordoba")
    return a, b


def test_carta_coincide_con_efemerides(cartas):
    a, _ = cartas
    assert _sign(a.points["sol"]) == ("Tauro", 29)
    assert _sign(a.points["venus"])[0] == "Aries"
    assert _sign(a.points["marte"])[0] == "Piscis"
    assert _sign(a.points["saturno"])[0] == "Capricornio"
    assert _sign(a.points["pluton"])[0] == "Escorpio"
    assert _sign(a.points["asc"])[0] == "Virgo"


def test_usa_la_hora_local_del_lugar(cartas):
    a, _ = cartas
    utc_como_si_fuera_local = compute_chart(date(1990, 5, 20), time(14, 30), True, -34.6131, -58.3772, "UTC")
    assert abs(a.points["luna"] - utc_como_si_fuera_local.points["luna"]) > 1  # 3 h de diferencia mueven la Luna


def test_doce_casas_por_signo_entero(cartas):
    a, _ = cartas
    assert len(a.houses) == 12
    assert a.houses[0] == 30 * int(a.points["asc"] // 30)  # la casa 1 es el signo entero del ascendente
    assert a.house_of(a.points["asc"]) == 1


def test_sin_lugar_no_hay_casas_ni_ascendente():
    c = compute_chart(date(1990, 5, 20), time(14, 30), True, None, None, None)
    assert c.houses is None and "asc" not in c.points


def test_resultado_reproducible_y_en_rango(cartas):
    a, b = cartas
    r1, r2 = synastry(a, b, "pareja"), synastry(a, b, "pareja")
    assert r1 == r2
    assert 0 <= r1["total"] <= 100
    assert set(r1["ejes"]) == set(SCORED_AXES)
    assert all(0 <= v <= 100 for v in r1["ejes"].values())


def test_el_tipo_de_relacion_cambia_el_total_pero_no_los_ejes(cartas):
    a, b = cartas
    pareja, laboral = synastry(a, b, "pareja"), synastry(a, b, "laboral")
    assert pareja["ejes"] == laboral["ejes"]
    assert pareja["total"] != laboral["total"]


def test_tipo_desconocido_usa_el_por_defecto(cartas):
    a, b = cartas
    assert synastry(a, b, "cualquiera")["tipo_de_relacion"] == load_config()["tipos_de_relacion"]["por_defecto"]


def test_sin_hora_exacta_no_usa_casas_y_es_aproximado(cartas):
    _, b = cartas
    estimada = compute_chart(date(1990, 5, 20), time(12, 30), False, -34.6131, -58.3772, "America/Argentina/Buenos_Aires")
    assert estimada.houses is None and "asc" not in estimada.points
    r = synastry(estimada, b, "pareja")
    assert r["aproximado"] is True and r["modalidad"] == "completa_aproximada"


def test_detalle_por_nivel_para_explicar(cartas):
    a, b = cartas
    d = synastry(a, b, "pareja")["detalle"]["atraccion"]
    assert {"puntaje_base", "modificador_e5", "aspectos_encontrados"} <= set(d)
    assert -10 <= d["modificador_e5"] <= 10
