from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_PROCESSED = CARPETA_PROYECTO / "data" / "processed"
CARPETA_GRAFICOS = (
    CARPETA_PROYECTO / "data" / "diagnostico_rendimientos_reales" / "desde_2000"
)
ARCHIVO_ESTADISTICAS = (
    CARPETA_PROCESSED / "rendimientos_ahorro_inversion_real_desde_2000_estadisticas.csv"
)
ARCHIVO_12M = (
    CARPETA_PROCESSED / "rendimientos_ahorro_inversion_real_desde_2000_12m.csv"
)

ALTERNATIVAS = ["Plazo fijo", "Dolar", "Merval", "S&P 500 en pesos"]
HORIZONTES = ["12m_real", "3a_real", "5a_real", "10a_real"]
ETIQUETAS_HORIZONTES = ["12 meses", "3 años", "5 años", "10 años"]


def _leer_estadisticas():
    estadisticas = pd.read_csv(ARCHIVO_ESTADISTICAS)
    return estadisticas[estadisticas["horizonte"].isin(HORIZONTES)].copy()


def generar_graficos_resumen():
    estadisticas = _leer_estadisticas()
    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    desvio = estadisticas.pivot(
        index="horizonte",
        columns="alternativa",
        values="desvio_estandar",
    ).reindex(HORIZONTES)
    negativas = estadisticas.pivot(
        index="horizonte",
        columns="alternativa",
        values="porcentaje_negativo",
    ).reindex(HORIZONTES)

    figura, eje = plt.subplots(figsize=(11, 6))
    desvio.mul(100).plot(kind="bar", ax=eje)
    eje.set_title("Dispersión del rendimiento real según horizonte")
    eje.set_xlabel("Horizonte")
    eje.set_ylabel("Desvío estándar (%)")
    eje.set_xticklabels(ETIQUETAS_HORIZONTES, rotation=0)
    eje.legend(title="Alternativa")
    figura.tight_layout()
    archivo_desvio = CARPETA_GRAFICOS / "resumen_desvio_estandar_real.png"
    figura.savefig(archivo_desvio, dpi=150)
    plt.close(figura)

    figura, eje = plt.subplots(figsize=(11, 6))
    negativas[ALTERNATIVAS].plot(kind="bar", ax=eje)
    eje.set_title("Frecuencia histórica de rendimiento real negativo")
    eje.set_xlabel("Horizonte")
    eje.set_ylabel("Ventanas negativas (%)")
    eje.set_xticklabels(ETIQUETAS_HORIZONTES, rotation=0)
    eje.legend(title="Alternativa")
    figura.tight_layout()
    archivo_negativas = CARPETA_GRAFICOS / "resumen_frecuencia_negativa_real.png"
    figura.savefig(archivo_negativas, dpi=150)
    plt.close(figura)

    doce_meses = pd.read_csv(ARCHIVO_12M)
    picos = {}
    for columna, nombre in [
        ("rend_dolar", "Dolar"),
        ("rend_sp500_pesos", "S&P 500 en pesos"),
    ]:
        fila = doce_meses.loc[doce_meses[columna].idxmax()]
        picos[nombre] = {
            "periodo": fila["periodo"],
            "rendimiento_real_12m": fila[columna],
        }
    return archivo_desvio, archivo_negativas, picos


if __name__ == "__main__":
    archivos, negativos, picos = generar_graficos_resumen()
    print(f"grafico_desvio={archivos}")
    print(f"grafico_negativos={negativos}")
    for alternativa, pico in picos.items():
        print(
            f"pico_12m_{alternativa}: periodo={pico['periodo']} "
            f"rendimiento={pico['rendimiento_real_12m']:.10f}"
        )