import pandas as pd

from Fuentes.bcra import cargar_bcra
from Fuentes.inflacion import cargar_inflacion


def cargar_poder_compra_usd():
    bcra = cargar_bcra()
    inflacion = cargar_inflacion()

    datos = pd.merge(
        bcra,
        inflacion[
            [
                "fecha",
                "Indice_IPC",
            ]
        ],
        on="fecha",
        how="inner",
    )

    datos = datos.sort_values("fecha")

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