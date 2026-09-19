import pandas as pd

from Fuentes.tasas_interes import cargar_tasa
from Fuentes.tipo_cambio import cargar_caso_a


def _cargar_tasa_mensual():
    tasa = cargar_tasa().copy()
    tasa["mes"] = tasa["fecha"].dt.to_period("M")
    return (
        tasa.sort_values("fecha")
        .groupby("mes", as_index=False)
        .tail(1)[["mes", "tasa"]]
        .rename(columns={"mes": "mes_inicial", "tasa": "tna"})
    )


def cargar_comparacion():
    """Construye la comparación independiente mes a mes, sin capitalización."""
    caso_a = cargar_caso_a()
    caso_a = caso_a[
        ["mes", "caso_a", "fuente", "fecha_observacion"]
    ].rename(
        columns={
            "mes": "mes_inicial",
            "caso_a": "tc_caso_a_inicial",
            "fuente": "fuente_caso_a_inicial",
            "fecha_observacion": "fecha_caso_a_inicial",
        }
    )
    caso_a["mes_final"] = caso_a["mes_inicial"] + 1

    caso_a_final = cargar_caso_a()[
        ["mes", "caso_a", "fuente", "fecha_observacion"]
    ].rename(
        columns={
            "mes": "mes_final",
            "caso_a": "tc_caso_a_final",
            "fuente": "fuente_caso_a_final",
            "fecha_observacion": "fecha_caso_a_final",
        }
    )

    datos = caso_a.merge(caso_a_final, on="mes_final", how="inner")
    datos = datos.merge(_cargar_tasa_mensual(), on="mes_inicial", how="inner")
    datos = datos.dropna(
        subset=["tc_caso_a_inicial", "tc_caso_a_final", "tna"]
    ).copy()

    datos["periodo"] = datos["mes_inicial"].astype("string")
    datos["valor_final_pf"] = 1 + datos["tna"] / 100 / 12
    datos["valor_final_dolar"] = (
        datos["tc_caso_a_final"] / datos["tc_caso_a_inicial"]
    )
    datos["rendimiento_pf"] = datos["valor_final_pf"] - 1
    datos["rendimiento_dolar"] = datos["valor_final_dolar"] - 1
    datos["diferencia"] = datos["rendimiento_pf"] - datos["rendimiento_dolar"]
    return datos[
        [
            "periodo",
            "mes_inicial",
            "mes_final",
            "tna",
            "tc_caso_a_inicial",
            "tc_caso_a_final",
            "fuente_caso_a_inicial",
            "fuente_caso_a_final",
            "fecha_caso_a_inicial",
            "fecha_caso_a_final",
            "valor_final_pf",
            "valor_final_dolar",
            "rendimiento_pf",
            "rendimiento_dolar",
            "diferencia",
        ]
    ].sort_values("mes_inicial").reset_index(drop=True)