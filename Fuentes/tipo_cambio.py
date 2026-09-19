import pandas as pd

from Fuentes.ambito import cargar_dolar_blue, construir_serie_mensual
from Fuentes.bcra import cargar_bcra


FECHA_CORTE = pd.Timestamp("2012-10-01")
FECHA_CORTE_2 = pd.Timestamp("2015-12-01")
FECHA_CORTE_3 = pd.Timestamp("2019-10-01")
FECHA_CORTE_4 = pd.Timestamp("2025-04-01")


def _cargar_oficial_mensual():
    oficial = cargar_bcra().copy()
    oficial["mes"] = oficial["fecha"].dt.to_period("M")
    oficial = oficial.rename(
        columns={
            "fecha": "fecha_oficial",
            "tipo_cambio": "oficial",
        }
    )
    return oficial[["mes", "fecha_oficial", "oficial"]]


def _cargar_blue_mensual():
    blue = construir_serie_mensual(cargar_dolar_blue()).copy()
    blue["mes"] = blue["fecha"].dt.to_period("M")
    blue = blue.rename(
        columns={
            "fecha": "fecha_blue",
            "tipo_cambio": "blue",
        }
    )
    return blue[["mes", "fecha_blue", "blue"]]


def _fuente_caso_a(meses):
    return pd.Series(
        "oficial",
        index=meses.index,
        dtype="string",
    ).where(
        ~(
            ((meses >= FECHA_CORTE.to_period("M")) & (meses < FECHA_CORTE_2.to_period("M")))
            | ((meses >= FECHA_CORTE_3.to_period("M")) & (meses < FECHA_CORTE_4.to_period("M")))
        ),
        "blue",
    )


def cargar_caso_a():
    """Construye las series mensuales oficial, blue y Caso A en memoria."""
    datos = _cargar_oficial_mensual().merge(
        _cargar_blue_mensual(),
        on="mes",
        how="outer",
    ).sort_values("mes").reset_index(drop=True)

    datos["fuente"] = _fuente_caso_a(datos["mes"])
    datos["caso_a"] = datos["oficial"].where(
        datos["fuente"].eq("oficial"),
        datos["blue"],
    )
    datos["fecha"] = datos["mes"].dt.to_timestamp()
    datos["fecha_observacion"] = datos["fecha_oficial"].where(
        datos["fuente"].eq("oficial"),
        datos["fecha_blue"],
    )
    return datos[
        [
            "mes",
            "fecha",
            "fecha_observacion",
            "fecha_oficial",
            "fecha_blue",
            "oficial",
            "blue",
            "caso_a",
            "fuente",
        ]
    ]