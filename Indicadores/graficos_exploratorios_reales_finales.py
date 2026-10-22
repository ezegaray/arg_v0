from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_PROCESSED = CARPETA_PROYECTO / "data" / "processed"
CARPETA_SALIDA = (
    CARPETA_PROYECTO
    / "data"
    / "diagnostico_rendimientos_reales"
    / "desde_merval_final"
)
ARCHIVO_ESTADISTICAS_MUESTRAS_COMUNES = (
    CARPETA_PROCESSED
    / "estadisticas_boxplots_rendimientos_reales_muestras_comunes.csv"
)

ALTERNATIVAS = {
    "rend_plazo_fijo": "Plazo fijo",
    "rend_dolar": "Dólar",
    "rend_merval": "Merval",
    "rend_sp500_pesos": "S&P 500 en pesos",
}
HORIZONTES = {
    "mensual": ("rendimientos_ahorro_inversion_real_desde_merval_mensual.csv", "rend"),
    "12 meses": ("rendimientos_ahorro_inversion_real_desde_merval_12m.csv", "rend"),
    "3 años": ("rendimientos_ahorro_inversion_real_desde_merval_3a.csv", "cagr"),
    "5 años": ("rendimientos_ahorro_inversion_real_desde_merval_5a.csv", "cagr"),
    "10 años": ("rendimientos_ahorro_inversion_real_desde_merval_10a.csv", "cagr"),
}


def _leer_horizontes():
    tablas = {}
    for horizonte, (nombre, tipo) in HORIZONTES.items():
        datos = pd.read_csv(CARPETA_PROCESSED / nombre)
        datos["periodo"] = pd.PeriodIndex(datos["periodo"], freq="M")
        columnas = {}
        for columna in ALTERNATIVAS:
            nombre_columna = (
                columna if tipo == "rend" else f"cagr_{columna.removeprefix('rend_')}"
            )
            columnas[columna] = nombre_columna
        tablas[horizonte] = (datos, columnas)
    return tablas


def filtrar_muestras_comunes(tablas):
    tablas_comunes = {}
    for horizonte, (datos, columnas) in tablas.items():
        columnas_instrumentos = list(columnas.values())
        valores = datos[columnas_instrumentos].to_numpy(dtype="float64")
        validos = np.isfinite(valores).all(axis=1)
        tablas_comunes[horizonte] = (
            datos.loc[validos].copy(),
            columnas,
        )
    return tablas_comunes


def construir_estadisticas_muestras_comunes(tablas):
    tablas_comunes = filtrar_muestras_comunes(tablas)
    filas = []
    for horizonte, (datos, columnas) in tablas_comunes.items():
        periodos = datos["periodo"]
        for instrumento, columna in columnas.items():
            valores = datos[columna] * 100
            filas.append(
                {
                    "instrumento": ALTERNATIVAS[instrumento],
                    "horizonte": horizonte,
                    "fecha_inicio": periodos.min(),
                    "fecha_fin": periodos.max(),
                    "observaciones": len(valores),
                    "media": valores.mean(),
                    "mediana": valores.median(),
                    "desvio_estandar": valores.std(),
                    "minimo": valores.min(),
                    "maximo": valores.max(),
                    "pct_positivos": valores.gt(0).mean() * 100,
                    "pct_negativos": valores.lt(0).mean() * 100,
                }
            )
    return pd.DataFrame(filas)


def guardar_estadisticas_muestras_comunes(tablas):
    estadisticas = construir_estadisticas_muestras_comunes(tablas)
    CARPETA_PROCESSED.mkdir(parents=True, exist_ok=True)
    estadisticas.to_csv(ARCHIVO_ESTADISTICAS_MUESTRAS_COMUNES, index=False)
    return estadisticas


def _boxplot(ax, valores, posiciones, etiquetas, colores):
    for valor, posicion, etiqueta, color in zip(
        valores, posiciones, etiquetas, colores
    ):
        ax.boxplot(
            valor,
            positions=[posicion],
            widths=0.18,
            patch_artist=True,
            boxprops={"facecolor": color, "edgecolor": color, "alpha": 0.72},
            medianprops={"color": "#ffffff", "linewidth": 1.5},
            whiskerprops={"color": color},
            capprops={"color": color},
            flierprops={
                "marker": ".",
                "markersize": 2,
                "markerfacecolor": "#c9d1d9",
                "markeredgecolor": "#c9d1d9",
                "alpha": 0.35,
            },
        )


def _estilizar_boxplot(figura, eje, xlabel, ylabel, titulo, titulo_leyenda):
    color_texto = "#f5f5f5"
    figura.patch.set_alpha(0)
    eje.set_facecolor("none")
    eje.set_xlabel(xlabel, color=color_texto)
    eje.set_ylabel(ylabel, color=color_texto)
    eje.set_title(titulo, color=color_texto)
    eje.tick_params(colors=color_texto)
    eje.grid(axis="y", color="#ffffff", alpha=0.14, linewidth=0.7)
    eje.set_axisbelow(True)
    for borde in eje.spines.values():
        borde.set_color("#77808b")
        borde.set_alpha(0.55)
    eje.axhline(0, color="#d8dee4", linewidth=0.8, linestyle="--", alpha=0.75)
    leyenda = eje.legend(title=titulo_leyenda)
    if leyenda:
        leyenda.get_frame().set_facecolor("#0e1117")
        leyenda.get_frame().set_alpha(0.75)
        leyenda.get_frame().set_edgecolor("#77808b")
        for texto in leyenda.get_texts():
            texto.set_color(color_texto)
        if leyenda.get_title():
            leyenda.get_title().set_color(color_texto)
    figura.tight_layout()


def construir_boxplot_por_horizonte(tablas):
    alternativas = list(ALTERNATIVAS)
    colores = ["#f39c12", "#2ecc71", "#3498db", "#e74c3c"]
    posiciones = []
    valores = []
    etiquetas = []
    centros = []
    for indice, (horizonte, (datos, columnas)) in enumerate(tablas.items()):
        centro = indice * 1.2
        centros.append(centro)
        for desplazamiento, alternativa in zip([-0.3, -0.1, 0.1, 0.3], alternativas):
            posiciones.append(centro + desplazamiento)
            valores.append(datos[columnas[alternativa]].dropna() * 100)
            etiquetas.append(ALTERNATIVAS[alternativa])

    figura, eje = plt.subplots(figsize=(13, 7))
    _boxplot(eje, valores, posiciones, etiquetas, colores * len(tablas))
    for color, etiqueta in zip(colores, ALTERNATIVAS.values()):
        eje.plot([], [], color=color, linewidth=6, label=etiqueta)
    eje.set_xticks(centros, list(tablas))
    _estilizar_boxplot(
        figura,
        eje,
        "Horizonte",
        "Rendimiento real (%)",
        "Rendimientos reales por horizonte y alternativa",
        "Instrumento",
    )
    return figura


def generar_boxplot_por_horizonte(tablas):
    figura = construir_boxplot_por_horizonte(tablas)
    destino = CARPETA_SALIDA / "boxplot_real_agrupado_por_horizonte.png"
    figura.savefig(destino, dpi=150, transparent=True)
    plt.close(figura)
    return destino


def construir_boxplot_por_instrumento(tablas):
    alternativas = list(ALTERNATIVAS)
    colores = ["#9b8afb", "#f472b6", "#facc15", "#22d3ee", "#a3e635"]
    posiciones = []
    valores = []
    etiquetas = []
    centros = []
    for indice, alternativa in enumerate(alternativas):
        centro = indice * 1.4
        centros.append(centro)
        for desplazamiento, (horizonte, (datos, columnas)) in zip(
            [-0.4, -0.2, 0, 0.2, 0.4], tablas.items()
        ):
            posiciones.append(centro + desplazamiento)
            valores.append(datos[columnas[alternativa]].dropna() * 100)
            etiquetas.append(horizonte)

    figura, eje = plt.subplots(figsize=(13, 7))
    _boxplot(eje, valores, posiciones, etiquetas, colores * len(alternativas))
    for color, etiqueta in zip(colores, tablas):
        eje.plot([], [], color=color, linewidth=6, label=etiqueta)
    eje.set_xticks(centros, [ALTERNATIVAS[alternativa] for alternativa in alternativas])
    _estilizar_boxplot(
        figura,
        eje,
        "Instrumento",
        "Rendimiento real (%)",
        "Rendimientos reales por alternativa y horizonte",
        "Horizonte",
    )
    return figura


def generar_boxplot_por_instrumento(tablas):
    figura = construir_boxplot_por_instrumento(tablas)
    destino = CARPETA_SALIDA / "boxplot_real_agrupado_por_instrumento.png"
    figura.savefig(destino, dpi=150, transparent=True)
    plt.close(figura)
    return destino


def regenerar_temporales(tablas):
    destinos = []
    for horizonte, (datos, columnas) in tablas.items():
        figura, eje = plt.subplots(figsize=(13, 6))
        fechas = datos["periodo"].dt.to_timestamp()
        for alternativa, columna in columnas.items():
            eje.plot(
                fechas,
                datos[columna] * 100,
                linewidth=1,
                label=ALTERNATIVAS[alternativa],
            )
        eje.axhline(0, color="black", linewidth=0.7)
        eje.set_title(f"Rendimiento real: {horizonte}")
        eje.set_xlabel("Año")
        eje.set_ylabel("Rendimiento real (%)")
        eje.xaxis.set_major_locator(mdates.YearLocator(5))
        eje.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        eje.legend()
        figura.autofmt_xdate()
        figura.tight_layout()
        destino = CARPETA_SALIDA / f"temporal_real_{horizonte.replace(' ', '_')}.png"
        figura.savefig(destino, dpi=150)
        plt.close(figura)
        destinos.append(destino)
    return destinos


def generar_graficos():
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    tablas = _leer_horizontes()
    tablas_comunes = filtrar_muestras_comunes(tablas)
    guardar_estadisticas_muestras_comunes(tablas_comunes)
    box_horizonte = generar_boxplot_por_horizonte(tablas_comunes)
    box_instrumento = generar_boxplot_por_instrumento(tablas_comunes)
    temporales = regenerar_temporales(tablas)

    tabla_12m = tablas["12 meses"][0]
    picos = {}
    for columna, nombre in [
        ("rend_dolar", "Dolar"),
        ("rend_sp500_pesos", "S&P 500 en pesos"),
    ]:
        fila = tabla_12m.loc[tabla_12m[columna].idxmax()]
        picos[nombre] = (fila["periodo"], fila[columna])
    return box_horizonte, box_instrumento, temporales, picos


if __name__ == "__main__":
    box_horizonte, box_instrumento, temporales, picos = generar_graficos()
    print(f"boxplot_por_horizonte={box_horizonte}")
    print(f"boxplot_por_instrumento={box_instrumento}")
    print(f"estadisticas_muestras_comunes={ARCHIVO_ESTADISTICAS_MUESTRAS_COMUNES}")
    for temporal in temporales:
        print(f"temporal={temporal}")
    for alternativa, (periodo, valor) in picos.items():
        print(f"pico_{alternativa}: periodo={periodo} valor={valor:.10f}")