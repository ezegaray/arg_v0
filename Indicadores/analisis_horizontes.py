from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from Indicadores.rendimientos_ahorro_inversion import construir_rendimientos


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_PROCESSED = CARPETA_PROYECTO / "data" / "processed"
CARPETA_GRAFICOS = CARPETA_PROYECTO / "data" / "diagnostico_rendimientos"

ALTERNATIVAS = {
    "rend_plazo_fijo": "Plazo fijo",
    "rend_dolar": "Dolar",
    "rend_merval": "Merval",
    "rend_sp500_pesos": "S&P 500 en pesos",
}


def _nombre_alternativa(columna):
    nombre_base = columna
    if columna.startswith("cagr_"):
        nombre_base = "rend_" + columna.removeprefix("cagr_")
    return ALTERNATIVAS.get(nombre_base, columna)


def _ventana_compuesta(serie, meses):
    serie = serie.sort_index()
    resultados = {}
    for posicion in range(meses - 1, len(serie)):
        periodo_final = serie.index[posicion]
        periodos = pd.period_range(
            end=periodo_final,
            periods=meses,
            freq="M",
        )
        ventana = serie.reindex(periodos)
        if ventana.isna().any() or not ventana.index.equals(periodos):
            continue
        resultados[periodo_final] = (1 + ventana).prod() - 1
    return pd.Series(resultados, dtype="float64")


def _tabla_horizonte(datos, meses, cagr_anios=None):
    resultados = {}
    for columna in ALTERNATIVAS:
        acumulado = _ventana_compuesta(datos.set_index("periodo")[columna], meses)
        if cagr_anios is None:
            resultados[columna] = acumulado
        else:
            resultados[f"{columna}_acumulado"] = acumulado
            resultados[f"cagr_{columna.removeprefix('rend_')}"] = (
                (1 + acumulado) ** (1 / cagr_anios) - 1
            )
    tabla = pd.DataFrame(resultados).sort_index()
    tabla.index.name = "periodo"
    return tabla.reset_index()


def _tabla_anual(datos):
    datos = datos.copy()
    datos["anio"] = datos["periodo"].dt.year
    resultados = {}
    for anio, grupo in datos.groupby("anio"):
        periodos = pd.period_range(f"{anio}-01", f"{anio}-12", freq="M")
        fila = {}
        for columna in ALTERNATIVAS:
            valores = grupo.set_index("periodo")[columna].reindex(periodos)
            fila[columna] = (1 + valores).prod() - 1 if valores.notna().all() else pd.NA
        resultados[anio] = fila
    tabla = pd.DataFrame.from_dict(resultados, orient="index")
    tabla.index.name = "anio"
    return tabla.dropna(how="all").reset_index()


def _estadisticas(tablas):
    filas = []
    for horizonte, tabla, columnas in tablas:
        for columna in columnas:
            valores = tabla[columna].dropna()
            nombre_base = columna
            if columna.startswith("cagr_"):
                nombre_base = "rend_" + columna.removeprefix("cagr_")
            elif columna.endswith("_acumulado"):
                nombre_base = columna.removesuffix("_acumulado")
            filas.append(
                {
                    "horizonte": horizonte,
                    "alternativa": ALTERNATIVAS.get(nombre_base, columna),
                    "medida": "CAGR" if columna.startswith("cagr_") else "rendimiento",
                    "observaciones": len(valores),
                    "fecha_minima": tabla.loc[valores.index, "periodo"].min(),
                    "fecha_maxima": tabla.loc[valores.index, "periodo"].max(),
                    "media": valores.mean(),
                    "mediana": valores.median(),
                    "desvio_estandar": valores.std(),
                    "minimo": valores.min(),
                    "maximo": valores.max(),
                    "percentil_25": valores.quantile(0.25),
                    "percentil_75": valores.quantile(0.75),
                    "porcentaje_negativo": (valores < 0).mean() * 100,
                }
            )
    return pd.DataFrame(filas)


def _graficar(horizonte, tabla, columnas, sufijo):
    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)
    temporal = CARPETA_GRAFICOS / f"rendimientos_{sufijo}_temporal.png"
    dispersion = CARPETA_GRAFICOS / f"rendimientos_{sufijo}_dispersion.png"

    figura, eje = plt.subplots(figsize=(12, 6))
    for columna in columnas:
        eje.plot(
            tabla["periodo"].astype(str),
            tabla[columna] * 100,
            label=_nombre_alternativa(columna),
            linewidth=1,
        )
    eje.axhline(0, color="black", linewidth=0.7)
    eje.set_title(f"Rendimientos {horizonte}")
    eje.set_xlabel("Periodo")
    eje.set_ylabel("Rendimiento (%)")
    eje.legend()
    eje.tick_params(axis="x", rotation=45)
    figura.tight_layout()
    figura.savefig(temporal, dpi=150)
    plt.close(figura)

    figura, eje = plt.subplots(figsize=(10, 6))
    valores = [tabla[columna].dropna() * 100 for columna in columnas]
    eje.boxplot(
        valores,
        tick_labels=[_nombre_alternativa(columna) for columna in columnas],
    )
    eje.axhline(0, color="black", linewidth=0.7)
    eje.set_title(f"Dispersión de rendimientos {horizonte}")
    eje.set_ylabel("Rendimiento (%)")
    eje.tick_params(axis="x", rotation=15)
    figura.tight_layout()
    figura.savefig(dispersion, dpi=150)
    plt.close(figura)


def generar_analisis():
    datos = construir_rendimientos()
    datos["periodo"] = pd.PeriodIndex(datos["periodo"], freq="M")

    mensual = datos.copy()
    doce_meses = _tabla_horizonte(datos, 12)
    tres_anios = _tabla_horizonte(datos, 36, 3)
    cinco_anios = _tabla_horizonte(datos, 60, 5)
    diez_anios = _tabla_horizonte(datos, 120, 10)
    anual = _tabla_anual(datos)

    salidas = {
        "rendimientos_ahorro_inversion_12m.csv": doce_meses,
        "rendimientos_ahorro_inversion_3a.csv": tres_anios,
        "rendimientos_ahorro_inversion_5a.csv": cinco_anios,
        "rendimientos_ahorro_inversion_10a.csv": diez_anios,
        "rendimientos_ahorro_inversion_anual.csv": anual,
    }
    for nombre, tabla in salidas.items():
        tabla.to_csv(CARPETA_PROCESSED / nombre, index=False)

    columnas_mensual = list(ALTERNATIVAS)
    columnas_12m = columnas_mensual
    columnas_3a = [columna for columna in tres_anios if columna.startswith("cagr_")]
    columnas_5a = [columna for columna in cinco_anios if columna.startswith("cagr_")]
    columnas_10a = [columna for columna in diez_anios if columna.startswith("cagr_")]
    estadisticas = _estadisticas(
        [
            ("mensual", mensual, columnas_mensual),
            ("12m", doce_meses, columnas_12m),
            ("3a", tres_anios, columnas_3a),
            ("5a", cinco_anios, columnas_5a),
            ("10a", diez_anios, columnas_10a),
        ]
    )
    estadisticas.to_csv(
        CARPETA_PROCESSED / "rendimientos_ahorro_inversion_estadisticas.csv",
        index=False,
    )

    _graficar("mensuales", mensual, columnas_mensual, "mensual")
    _graficar("a 12 meses", doce_meses, columnas_12m, "12m")
    _graficar("a 3 años (CAGR)", tres_anios, columnas_3a, "3a")
    _graficar("a 5 años (CAGR)", cinco_anios, columnas_5a, "5a")
    _graficar("a 10 años (CAGR)", diez_anios, columnas_10a, "10a")

    return salidas, estadisticas


if __name__ == "__main__":
    generar_analisis()