import pandas as pd

from Fuentes.inflacion_historica import cargar_inflacion_historica
from Fuentes.indec_ipc import cargar_ipc


def cargar_inflacion():
    historica = cargar_inflacion_historica()
    indec = cargar_ipc()

    # Base histórica correspondiente a diciembre de 2016
    base_2016_12 = historica.loc[
        historica["fecha"] == "2016-12-01",
        "index"
    ].iloc[0]

    historica["Indice_IPC"] = (
        historica["index"] / base_2016_12 * 100
    )

    historica = historica[
        historica["fecha"] < "2016-12-01"
    ].copy()

    historica["fuente"] = "InflacionVerdadera"
    indec["fuente"] = "INDEC"

    historica = historica[
        [
            "fecha",
            "Indice_IPC",
            "inflacion_mensual",
            "fuente",
        ]
    ]

    indec = indec[
        [
            "fecha",
            "Indice_IPC",
            "inflacion_mensual",
            "fuente",
        ]
    ]

    inflacion = pd.concat(
        [historica, indec],
        ignore_index=True
    )

    inflacion = inflacion.sort_values("fecha")

    inflacion["inflacion_mensual"] = (
        inflacion["Indice_IPC"]
        / inflacion["Indice_IPC"].shift(1)
        - 1
    ) * 100

    return inflacion