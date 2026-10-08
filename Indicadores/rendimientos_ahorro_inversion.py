from pathlib import Path

import pandas as pd

from Fuentes.tipo_cambio import cargar_caso_a
from Indicadores.plazo_fijo_vs_dolar import _cargar_tasa_mensual


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_CCL = CARPETA_PROYECTO / "data" / "processed" / "dolar_ccl_mensual.csv"
ARCHIVO_MERVAL = CARPETA_PROYECTO / "data" / "processed" / "merval_mensual.csv"
ARCHIVO_SP500 = CARPETA_PROYECTO / "data" / "processed" / "sp500_mensual.csv"
ARCHIVO_SALIDA = (
    CARPETA_PROYECTO / "data" / "processed" / "rendimientos_ahorro_inversion.csv"
)


def _leer_indice(archivo):
    datos = pd.read_csv(archivo, parse_dates=["fecha"])
    datos["mes"] = datos["fecha"].dt.to_period("M")
    return (
        datos.sort_values("fecha")
        .drop_duplicates("mes", keep="last")
        .set_index("mes")["cierre"]
        .sort_index()
    )


def _rendimiento_mensual(niveles):
    niveles = niveles.sort_index()
    siguiente_mes = niveles.index.to_series().shift(-1)
    siguiente_valor = niveles.shift(-1)
    es_mes_consecutivo = siguiente_mes.eq(niveles.index.to_series() + 1)
    rendimiento = siguiente_valor.div(niveles).sub(1)
    return rendimiento.where(es_mes_consecutivo)


def construir_rendimientos():
    tasa = _cargar_tasa_mensual().set_index("mes_inicial")["tna"]
    plazo_fijo = tasa.div(100).div(12)

    caso_a = cargar_caso_a().set_index("mes")["caso_a"]
    ccl = _leer_indice(ARCHIVO_CCL)
    dolar = _rendimiento_mensual(caso_a)
    merval = _rendimiento_mensual(_leer_indice(ARCHIVO_MERVAL))
    sp500_usd = _rendimiento_mensual(_leer_indice(ARCHIVO_SP500))
    fecha_corte = pd.Period("2013-01", freq="M")
    tipo_cambio = pd.concat(
        [
            _rendimiento_mensual(caso_a).loc[
                lambda serie: serie.index < fecha_corte
            ],
            _rendimiento_mensual(ccl).loc[
                lambda serie: serie.index >= fecha_corte
            ],
        ]
    ).sort_index()
    sp500_pesos = (1 + sp500_usd) * (1 + tipo_cambio) - 1

    datos = pd.concat(
        [plazo_fijo, dolar, merval, sp500_pesos],
        axis=1,
        keys=[
            "rend_plazo_fijo",
            "rend_dolar",
            "rend_merval",
            "rend_sp500_pesos",
        ],
    ).sort_index()
    datos.index.name = "periodo"
    return datos.reset_index()


def guardar_rendimientos():
    datos = construir_rendimientos()
    datos.to_csv(ARCHIVO_SALIDA, index=False)
    return datos


if __name__ == "__main__":
    guardar_rendimientos()