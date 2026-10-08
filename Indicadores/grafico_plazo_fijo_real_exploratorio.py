from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from Indicadores.analisis_horizontes import _tabla_horizonte
from Indicadores.analisis_horizontes_reales import _rendimientos_reales
from Indicadores.indice_real_base_100 import BASE, _construir_indice
from secciones.marcas_presidenciales import PRESIDENCIAS


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
ARCHIVO_GRAFICO = (
    CARPETA_PROYECTO
    / "data"
    / "diagnostico_rendimientos_reales"
    / "plazo_fijo_real_indice_y_horizontes.png"
)
PERIODO_INICIO_EJE = pd.Period("1996-01", freq="M")


def generar_grafico():
    rendimientos, _ = _rendimientos_reales()
    rendimientos["periodo"] = pd.PeriodIndex(rendimientos["periodo"], freq="M")
    plazo_fijo = rendimientos.set_index("periodo")["rend_plazo_fijo"].sort_index()

    indice = _construir_indice(plazo_fijo, BASE).rename("capital_real")
    tabla_12m = _tabla_horizonte(rendimientos, 12)
    tabla_3a = _tabla_horizonte(rendimientos, 36, 3)
    tabla_5a = _tabla_horizonte(rendimientos, 60, 5)
    tabla_10a = _tabla_horizonte(rendimientos, 120, 10)

    horizontes = {
        "Rendimiento real mensual anualizado (TNA equivalente)": (
            plazo_fijo * 12
        ),
        "Rendimiento real móvil a 12 meses": tabla_12m.set_index("periodo")[
            "rend_plazo_fijo"
        ],
        "CAGR real móvil a 3 años": tabla_3a.set_index("periodo")[
            "cagr_plazo_fijo"
        ],
        "CAGR real móvil a 5 años": tabla_5a.set_index("periodo")[
            "cagr_plazo_fijo"
        ],
        "CAGR real móvil a 10 años": tabla_10a.set_index("periodo")[
            "cagr_plazo_fijo"
        ],
    }
    horizontes = {
        nombre: serie.set_axis(pd.PeriodIndex(serie.index, freq="M")).dropna()
        for nombre, serie in horizontes.items()
    }
    series_completas = {"Capital real": indice.dropna(), **horizontes}
    periodo_fin = max(serie.index.max() for serie in series_completas.values())

    figura, (eje_indice, eje_horizontes) = plt.subplots(
        2,
        1,
        figsize=(14, 9),
        sharex=True,
        gridspec_kw={"height_ratios": [1, 1.25]},
    )
    indice_visible = indice.loc[indice.index >= PERIODO_INICIO_EJE]
    eje_indice.plot(
        indice_visible.index.to_timestamp(),
        indice_visible,
        color="#08306b",
        linewidth=1.8,
        label="Plazo fijo",
    )
    eje_indice.axhline(100, color="0.4", linewidth=0.8, linestyle="--")
    eje_indice.set_title(
        "Evolución del capital real — Plazo fijo\n"
        "Base: diciembre de 2016 = 100",
        loc="left",
    )
    eje_indice.set_ylabel("Índice de capital real")
    eje_indice.grid(axis="y", alpha=0.2)

    estilos = [
        ("#c62828", "-", 1.0),
        ("#08306b", "-", 1.25),
        ("#2171b5", "-", 1.25),
        ("#6baed6", "-", 1.25),
        ("#9ecae1", "--", 1.8),
    ]
    for (nombre, serie), (color, estilo, ancho) in zip(
        horizontes.items(), estilos
    ):
        serie_visible = serie.loc[serie.index >= PERIODO_INICIO_EJE]
        eje_horizontes.plot(
            serie_visible.index.to_timestamp(),
            serie_visible * 100,
            color=color,
            linewidth=ancho,
            linestyle=estilo,
            label=nombre,
        )
    eje_horizontes.axhline(0, color="black", linewidth=0.8)
    eje_horizontes.set_title("Rendimiento real según horizonte", loc="left")
    eje_horizontes.set_ylabel("Tasa anual (%)")
    eje_horizontes.set_xlabel("Año")
    eje_horizontes.grid(axis="y", alpha=0.2)
    handles, etiquetas = eje_horizontes.get_legend_handles_labels()

    for indice_marca, (fecha, etiqueta) in enumerate(PRESIDENCIAS):
        periodo_marca = pd.Period(fecha, freq="M")
        if PERIODO_INICIO_EJE <= periodo_marca <= periodo_fin:
            for eje in (eje_indice, eje_horizontes):
                eje.axvline(
                    pd.Timestamp(fecha),
                    color="0.45",
                    linewidth=0.8,
                    linestyle=":",
                    alpha=0.65,
                    zorder=0,
                )
            eje_indice.annotate(
                etiqueta,
                xy=(pd.Timestamp(fecha), 0.98),
                xycoords=("data", "axes fraction"),
                xytext=(3, -3 - (indice_marca % 2) * 16),
                textcoords="offset points",
                rotation=90,
                va="top",
                ha="left",
                fontsize=8,
                color="0.35",
                bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none", "pad": 1},
            )

    eje_horizontes.xaxis.set_major_locator(mdates.YearLocator(2))
    eje_horizontes.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    eje_horizontes.set_xlim(
        PERIODO_INICIO_EJE.start_time,
        periodo_fin.end_time,
    )
    figura.suptitle("Plazo fijo — análisis de rendimientos reales", y=0.99)
    figura.legend(
        handles,
        etiquetas,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.01),
        ncol=2,
        frameon=False,
        fontsize=9,
    )
    figura.subplots_adjust(
        left=0.09,
        right=0.99,
        bottom=0.16,
        top=0.88,
        hspace=0.24,
    )

    ARCHIVO_GRAFICO.parent.mkdir(parents=True, exist_ok=True)
    figura.savefig(ARCHIVO_GRAFICO, dpi=160, bbox_inches="tight")
    plt.close(figura)
    return ARCHIVO_GRAFICO, PERIODO_INICIO_EJE, periodo_fin


if __name__ == "__main__":
    archivo, inicio, fin = generar_grafico()
    print(f"grafico={archivo}")
    print(f"periodo_eje={inicio} a {fin}")
