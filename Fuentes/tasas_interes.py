from pathlib import Path

import pandas as pd


carpeta_proyecto = Path(__file__).resolve().parent.parent
archivo_procesado = carpeta_proyecto / "data" / "processed" / "tasa_plazo_fijo.csv"
CODIGO_TASA = "2324"


def cargar_tasa():
    if not archivo_procesado.exists():
        raise FileNotFoundError(
            "Falta data/processed/tasa_plazo_fijo.csv. "
            "Primero ejecutá actualizar_tas1()."
        )

    return pd.read_csv(
        archivo_procesado,
        parse_dates=["fecha"],
        dtype={"tasa": "float64"},
    )