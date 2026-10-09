"""Spec B5-motor-sinastria: carta completa y los 10 niveles del cuadro, con tablas en configuración."""

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


def test_doce_casas_desde_el_ascendente(cartas):
    a, _ = cartas
    assert len(a.houses) == 12
    assert a.houses[0] == pytest.approx(a.points["asc"])
    assert a.house_of(a.points["asc"] + 1) == 1


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
    assert synastry(a, b, "cualquiera")["tipo_de_relacion"] == load_config()["nivel_7_y_10_tipos_de_relacion"]["por_defecto"]


def test_sin_hora_exacta_no_usa_casas_y_es_aproximado(cartas):
    _, b = cartas
    estimada = compute_chart(date(1990, 5, 20), time(12, 0), False, -34.6131, -58.3772, "America/Argentina/Buenos_Aires")
    r = synastry(estimada, b, "pareja")
    assert r["aproximado"] is True
    assert all(r["detalle"][eje]["casas"] is None for eje in SCORED_AXES)


def test_detalle_por_nivel_para_explicar(cartas):
    a, b = cartas
    d = synastry(a, b, "pareja")["detalle"]["atraccion"]
    assert {"matriz_signos", "aspectos", "casas", "puntaje_base", "multiplicador_eje5", "aspectos_encontrados"} <= set(d)
    assert 0.85 <= d["multiplicador_eje5"] <= 1.15


def test_configuracion_completa():
    cfg = load_config()
    for eje, matriz in cfg["nivel_3_matriz_signos"]["matrices"].items():
        assert len(matriz) == 12 and all(len(fila) == 12 for fila in matriz), eje
    for tipo in cfg["nivel_7_y_10_tipos_de_relacion"]["tipos"].values():
        assert sum(tipo["pesos"].values()) == pytest.approx(1.0)
    assert set(cfg["normalizacion"]["centro"]) == set(SCORED_AXES)


def test_cambiar_una_tabla_cambia_el_resultado_sin_tocar_codigo(cartas, monkeypatch):
    a, b = cartas
    antes = synastry(a, b, "pareja")["ejes"]["comunicacion"]
    cfg = load_config()
    original = cfg["nivel_4_aspectos"]["trigono"]["puntos"]["comunicacion"]
    monkeypatch.setitem(cfg["nivel_4_aspectos"]["trigono"]["puntos"], "comunicacion", original + 20)
    assert synastry(a, b, "pareja")["ejes"]["comunicacion"] != antes
