from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_RENDIMIENTOS = (
    CARPETA_PROYECTO
    / "data"
    / "processed"
    / "rendimientos_ahorro_inversion_real_desde_merval_mensual.csv"
)
ARCHIVO_SALIDA = (
    CARPETA_PROYECTO
    / "data"
    / "processed"
    / "indice_real_base_100_desde_merval.csv"
)
CARPETA_GRAFICOS = (
    CARPETA_PROYECTO
    / "data"
    / "diagnostico_rendimientos_reales"
    / "desde_merval_final"
)
ARCHIVO_GRAFICO = CARPETA_GRAFICOS / "indice_real_base_100.png"
ARCHIVO_SALIDA_BASE_1996 = (
    CARPETA_PROYECTO
    / "data"
    / "processed"
    / "indice_real_base_1000_desde_1996.csv"
)
ARCHIVO_GRAFICO_BASE_1996 = (
    CARPETA_GRAFICOS / "indice_real_base_1000_desde_1996.png"
)

BASE = pd.Period("2016-12", freq="M")
BASE_1996 = pd.Period("1996-10", freq="M")
VALOR_BASE_1996 = 1000.0
ALTERNATIVAS = {
    "rend_plazo_fijo": "Plazo fijo",
    "rend_dolar": "Dolar",
    "rend_merval": "Merval",
    "rend_sp500_pesos": "S&P 500 en pesos",
}


def _construir_indice(serie, base, valor_base=100.0):
    serie = serie.sort_index()
    indice = pd.Series(index=serie.index, dtype="float64")
    if base not in serie.index or pd.isna(serie.loc[base]):
        return indice

    indice.loc[base] = valor_base
    periodos = list(serie.index)
    posicion_base = periodos.index(base)

    for posicion in range(posicion_base + 1, len(periodos)):
        periodo_anterior = periodos[posicion - 1]
        periodo_actual = periodos[posicion]
        if (
            periodo_actual == periodo_anterior + 1
            and pd.notna(indice.loc[periodo_anterior])
            and pd.notna(serie.loc[periodo_anterior])
        ):
            indice.loc[periodo_actual] = indice.loc[periodo_anterior] * (
                1 + serie.loc[periodo_anterior]
            )

    for posicion in range(posicion_base - 1, -1, -1):
        periodo_actual = periodos[posicion]
        periodo_siguiente = periodos[posicion + 1]
        if (
            periodo_siguiente == periodo_actual + 1
            and pd.notna(indice.loc[periodo_siguiente])
            and pd.notna(serie.loc[periodo_actual])
        ):
            indice.loc[periodo_actual] = indice.loc[periodo_siguiente] / (
                1 + serie.loc[periodo_actual]
            )
    return indice


def construir_indice_real():
    rendimientos = pd.read_csv(ARCHIVO_RENDIMIENTOS)
    rendimientos["periodo"] = pd.PeriodIndex(rendimientos["periodo"], freq="M")
    rendimientos = rendimientos.set_index("periodo").sort_index()
    indice = pd.DataFrame(index=rendimientos.index)
    for columna, nombre in ALTERNATIVAS.items():
        indice[nombre] = _construir_indice(rendimientos[columna], BASE)
    indice.index.name = "periodo"
    return indice.reset_index()


def guardar_indice_real():
    datos = construir_indice_real()
    ARCHIVO_SALIDA.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(ARCHIVO_SALIDA, index=False)

    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)
    figura, eje = plt.subplots(figsize=(13, 6))
    fechas = datos["periodo"].dt.to_timestamp()
    for alternativa in ALTERNATIVAS.values():
        eje.plot(fechas, datos[alternativa], label=alternativa, linewidth=1)
    eje.axhline(100, color="black", linewidth=0.7, linestyle="--")
    eje.set_title("Índice real base 100: diciembre de 2016")
    eje.set_xlabel("Año")
    eje.set_ylabel("Índice real")
    eje.xaxis.set_major_locator(mdates.YearLocator(5))
    eje.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    eje.legend()
    figura.autofmt_xdate()
    figura.tight_layout()
    figura.savefig(ARCHIVO_GRAFICO, dpi=150)
    plt.close(figura)
    return datos


def guardar_indice_real_base_1996():
    rendimientos = pd.read_csv(ARCHIVO_RENDIMIENTOS)
    rendimientos["periodo"] = pd.PeriodIndex(rendimientos["periodo"], freq="M")
    rendimientos = rendimientos.set_index("periodo").sort_index()
    indice = pd.DataFrame(index=rendimientos.index)
    for columna, nombre in ALTERNATIVAS.items():
        indice[nombre] = _construir_indice(
            rendimientos[columna],
            BASE_1996,
            VALOR_BASE_1996,
        )
    indice.index.name = "periodo"
    datos = indice.reset_index()

    ARCHIVO_SALIDA_BASE_1996.parent.mkdir(parents=True, exist_ok=True)
    datos.to_csv(ARCHIVO_SALIDA_BASE_1996, index=False)

    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)
    figura, eje = plt.subplots(figsize=(13, 6))
    fechas = datos["periodo"].dt.to_timestamp()
    for alternativa in ALTERNATIVAS.values():
        eje.plot(fechas, datos[alternativa], label=alternativa, linewidth=1)
    eje.axhline(
        VALOR_BASE_1996,
        color="black",
        linewidth=0.7,
        linestyle="--",
    )
    eje.set_title("Índice real base 1.000: octubre de 1996")
    eje.set_xlabel("Año")
    eje.set_ylabel("Índice real")
    eje.xaxis.set_major_locator(mdates.YearLocator(5))
    eje.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    eje.legend()
    figura.autofmt_xdate()
    figura.tight_layout()
    figura.savefig(ARCHIVO_GRAFICO_BASE_1996, dpi=150)
    plt.close(figura)
    return datos


if __name__ == "__main__":
    datos = guardar_indice_real()
    print(f"archivo={ARCHIVO_SALIDA}")
    print(f"grafico={ARCHIVO_GRAFICO}")
    print("primeras_5:")
    print(datos.head(5).to_string(index=False))
    print("ultimas_5:")
    print(datos.tail(5).to_string(index=False))
    datos_base_1996 = guardar_indice_real_base_1996()
    print(f"archivo_base_1996={ARCHIVO_SALIDA_BASE_1996}")
    print(f"grafico_base_1996={ARCHIVO_GRAFICO_BASE_1996}")
    print("base_1996:")
    print(
        datos_base_1996.loc[datos_base_1996["periodo"].eq(BASE_1996)].to_string(
            index=False
        )
    )