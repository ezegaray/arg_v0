from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from Fuentes.inflacion import cargar_inflacion
from Indicadores.analisis_horizontes import (
    ALTERNATIVAS,
    _estadisticas,
    _tabla_anual,
    _tabla_horizonte,
)
from Indicadores.rendimientos_ahorro_inversion import construir_rendimientos


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_PROCESSED = CARPETA_PROYECTO / "data" / "processed"
CARPETA_GRAFICOS = CARPETA_PROYECTO / "data" / "diagnostico_rendimientos_reales"


def _rendimientos_reales():
    nominales = construir_rendimientos()
    nominales["periodo"] = pd.PeriodIndex(nominales["periodo"], freq="M")
    nominales = nominales.set_index("periodo")

    inflacion = cargar_inflacion().copy()
    inflacion["periodo"] = inflacion["fecha"].dt.to_period("M")
    inflacion = inflacion.drop_duplicates("periodo", keep="last").set_index("periodo")
    inflacion_mensual = inflacion["inflacion_mensual"] / 100

    datos = nominales.join(inflacion_mensual.rename("inflacion_mensual"), how="left")
    columnas = list(ALTERNATIVAS)
    datos[columnas] = (1 + datos[columnas]).div(
        1 + datos["inflacion_mensual"], axis=0
    ) - 1
    datos[columnas] = datos[columnas].where(datos["inflacion_mensual"].notna(), pd.NA)
    return datos.reset_index(), inflacion


def _filtrar_desde(datos, inicio):
    return datos.loc[datos["periodo"] >= pd.Period(inicio, freq="M")].copy()


def _graficar_real(horizonte, tabla, columnas, carpeta, sufijo):
    carpeta.mkdir(parents=True, exist_ok=True)
    temporal = carpeta / f"rendimientos_reales_{sufijo}_temporal.png"
    dispersion = carpeta / f"rendimientos_reales_{sufijo}_dispersion.png"

    figura, eje = plt.subplots(figsize=(12, 6))
    for columna in columnas:
        nombre = columna
        if columna.startswith("cagr_"):
            nombre = "rend_" + columna.removeprefix("cagr_")
        eje.plot(
            tabla["periodo"].astype(str),
            tabla[columna] * 100,
            label=ALTERNATIVAS.get(nombre, columna),
            linewidth=1,
        )
    eje.axhline(0, color="black", linewidth=0.7)
    eje.set_title(f"Rendimientos reales {horizonte}")
    eje.set_xlabel("Periodo")
    eje.set_ylabel("Rendimiento (%)")
    eje.legend()
    eje.tick_params(axis="x", rotation=45)
    figura.tight_layout()
    figura.savefig(temporal, dpi=150)
    plt.close(figura)

    figura, eje = plt.subplots(figsize=(10, 6))
    valores = [tabla[columna].dropna() * 100 for columna in columnas]
    etiquetas = []
    for columna in columnas:
        nombre = "rend_" + columna.removeprefix("cagr_") if columna.startswith("cagr_") else columna
        etiquetas.append(ALTERNATIVAS.get(nombre, columna))
    eje.boxplot(valores, tick_labels=etiquetas)
    eje.axhline(0, color="black", linewidth=0.7)
    eje.set_title(f"Dispersión de rendimientos reales {horizonte}")
    eje.set_ylabel("Rendimiento (%)")
    eje.tick_params(axis="x", rotation=15)
    figura.tight_layout()
    figura.savefig(dispersion, dpi=150)
    plt.close(figura)


def _generar_para_inicio(datos, inicio, sufijo):
    datos = _filtrar_desde(datos, inicio)
    doce_meses = _tabla_horizonte(datos, 12)
    tres_anios = _tabla_horizonte(datos, 36, 3)
    cinco_anios = _tabla_horizonte(datos, 60, 5)
    diez_anios = _tabla_horizonte(datos, 120, 10)
    anual = _tabla_anual(datos)

    prefijo = "rendimientos_ahorro_inversion_real"
    if sufijo:
        prefijo += f"_{sufijo}"
    salidas = {
        f"{prefijo}_mensual.csv": datos,
        f"{prefijo}_12m.csv": doce_meses,
        f"{prefijo}_3a.csv": tres_anios,
        f"{prefijo}_5a.csv": cinco_anios,
        f"{prefijo}_10a.csv": diez_anios,
        f"{prefijo}_anual.csv": anual,
    }
    for nombre, tabla in salidas.items():
        tabla.to_csv(CARPETA_PROCESSED / nombre, index=False)

    columnas = list(ALTERNATIVAS)
    columnas_3a = [columna for columna in tres_anios if columna.startswith("cagr_")]
    columnas_5a = [columna for columna in cinco_anios if columna.startswith("cagr_")]
    columnas_10a = [columna for columna in diez_anios if columna.startswith("cagr_")]
    estadisticas = _estadisticas(
        [
            ("mensual_real", datos, columnas),
            ("12m_real", doce_meses, columnas),
            ("3a_real", tres_anios, columnas_3a),
            ("5a_real", cinco_anios, columnas_5a),
            ("10a_real", diez_anios, columnas_10a),
        ]
    )
    archivo_estadisticas = f"{prefijo}_estadisticas.csv"
    estadisticas.to_csv(CARPETA_PROCESSED / archivo_estadisticas, index=False)
    salidas[archivo_estadisticas] = estadisticas

    carpeta_graficos = CARPETA_GRAFICOS / (sufijo or "desde_merval")
    _graficar_real("mensual", datos, columnas, carpeta_graficos, "mensual")
    _graficar_real("12m", doce_meses, columnas, carpeta_graficos, "12m")
    _graficar_real("3a CAGR", tres_anios, columnas_3a, carpeta_graficos, "3a")
    _graficar_real("5a CAGR", cinco_anios, columnas_5a, carpeta_graficos, "5a")
    _graficar_real("10a CAGR", diez_anios, columnas_10a, carpeta_graficos, "10a")
    return salidas, estadisticas


def generar_analisis_reales():
    datos, inflacion = _rendimientos_reales()
    inicio_merval = datos.loc[datos["rend_merval"].notna(), "periodo"].min()
    resultados = {
        "alineacion_ipc": datos[["periodo"]].merge(
            inflacion.reset_index()[["periodo", "inflacion_mensual"]],
            on="periodo",
            how="left",
        ),
        "desde_merval": _generar_para_inicio(datos, inicio_merval, "desde_merval"),
        "desde_2000": _generar_para_inicio(datos, "2000-01", "desde_2000"),
    }
    resultados["alineacion_ipc"]["alineado_por_periodo"] = (
        resultados["alineacion_ipc"]["inflacion_mensual"].notna()
    )
    resultados["alineacion_ipc"].to_csv(
        CARPETA_PROCESSED / "rendimientos_ahorro_inversion_real_alineacion_ipc.csv",
        index=False,
    )
    return resultados


if __name__ == "__main__":
    generar_analisis_reales()