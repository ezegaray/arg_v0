import pandas as pd

from Fuentes.bcra import cargar_bcra
from Fuentes.inflacion import cargar_inflacion


FECHA_MINIMA_ANALITICA = pd.Timestamp("1996-10-01")
FECHA_INICIO_SERIE = pd.Timestamp("2002-03-01")


def cargar_poder_compra_usd():
    bcra = cargar_bcra()
    inflacion = cargar_inflacion()
    inflacion["mes"] = inflacion["fecha"].dt.to_period("M")

    datos = pd.merge(
        bcra,
        inflacion[
            [
                "mes",
                "Indice_IPC",
            ]
        ],
        on="mes",
        how="inner",
    )

    datos = datos.sort_values("fecha")
    fecha_inicio = max(FECHA_MINIMA_ANALITICA, FECHA_INICIO_SERIE)
    datos = datos[datos["fecha"] >= fecha_inicio].copy()

    # Diciembre de 2016 = 100
    fecha_base = pd.Timestamp("2016-12-01")

    fila_base = datos[
        datos["fecha"] == fecha_base
    ].iloc[0]

    valor_base = (
        fila_base["tipo_cambio"]
        / fila_base["Indice_IPC"]
    )

    datos["poder_compra_usd"] = (
        (
            datos["tipo_cambio"]
            / datos["Indice_IPC"]
        )
        / valor_base
        * 100
    )

    return datos