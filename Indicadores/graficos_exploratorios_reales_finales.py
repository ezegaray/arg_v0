from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_PROCESSED = CARPETA_PROYECTO / "data" / "processed"
CARPETA_SALIDA = (
    CARPETA_PROYECTO
    / "data"
    / "diagnostico_rendimientos_reales"
    / "desde_merval_final"
)

ALTERNATIVAS = {
    "rend_plazo_fijo": "Plazo fijo",
    "rend_dolar": "Dolar",
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


def _boxplot(ax, valores, posiciones, etiquetas, colores):
    for valor, posicion, etiqueta, color in zip(
        valores, posiciones, etiquetas, colores
    ):
        ax.boxplot(
            valor,
            positions=[posicion],
            widths=0.18,
            patch_artist=True,
            boxprops={"facecolor": color, "alpha": 0.7},
            medianprops={"color": "black", "linewidth": 1.2},
            whiskerprops={"color": color},
            capprops={"color": color},
            flierprops={"marker": ".", "markersize": 2, "alpha": 0.35},
        )


def generar_boxplot_por_horizonte(tablas):
    alternativas = list(ALTERNATIVAS)
    colores = ["#2f6690", "#d1495b", "#edae49", "#00798c"]
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
        eje.plot([], [], color=color, linewidth=8, label=etiqueta)
    eje.set_xticks(centros, list(tablas))
    eje.set_xlabel("Horizonte")
    eje.set_ylabel("Rendimiento real (%)")
    eje.set_title("Rendimientos reales por horizonte y alternativa")
    eje.axhline(0, color="black", linewidth=0.7)
    eje.legend(title="Alternativa")
    figura.tight_layout()
    destino = CARPETA_SALIDA / "boxplot_real_agrupado_por_horizonte.png"
    figura.savefig(destino, dpi=150)
    plt.close(figura)
    return destino


def generar_boxplot_por_instrumento(tablas):
    alternativas = list(ALTERNATIVAS)
    colores = ["#264653", "#2a9d8f", "#e9c46a", "#f4a261", "#e76f51"]
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
        eje.plot([], [], color=color, linewidth=8, label=etiqueta)
    eje.set_xticks(centros, [ALTERNATIVAS[alternativa] for alternativa in alternativas])
    eje.set_xlabel("Alternativa")
    eje.set_ylabel("Rendimiento real (%)")
    eje.set_title("Rendimientos reales por alternativa y horizonte")
    eje.axhline(0, color="black", linewidth=0.7)
    eje.legend(title="Horizonte")
    figura.tight_layout()
    destino = CARPETA_SALIDA / "boxplot_real_agrupado_por_instrumento.png"
    figura.savefig(destino, dpi=150)
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
    box_horizonte = generar_boxplot_por_horizonte(tablas)
    box_instrumento = generar_boxplot_por_instrumento(tablas)
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
    for temporal in temporales:
        print(f"temporal={temporal}")
    for alternativa, (periodo, valor) in picos.items():
        print(f"pico_{alternativa}: periodo={periodo} valor={valor:.10f}")