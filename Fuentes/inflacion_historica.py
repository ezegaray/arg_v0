from pathlib import Path
import pandas as pd


carpeta_proyecto = Path(__file__).resolve().parent.parent

archivo_inflacion_historica = (
    carpeta_proyecto
    / "data"
    / "raw"
    / "Argentina_inflation.csv"
)


def cargar_inflacion_historica():
    inflacion_historica = pd.read_csv(
        archivo_inflacion_historica
    )

    inflacion_historica["fecha"] = pd.to_datetime(
        inflacion_historica["date"].str.replace("m", "-"),
        format="%Y-%m"
    )

    inflacion_historica = inflacion_historica.sort_values("fecha")

    inflacion_historica["inflacion_mensual"] = (
        inflacion_historica["index"]
        / inflacion_historica["index"].shift(1)
        - 1
    ) * 100

    inflacion_historica = inflacion_historica[
        [
            "fecha",
            "index",
            "inflacion_mensual",
        ]
    ]
    
    return inflacion_historica


if __name__ == "__main__":
    inflacion_historica = cargar_inflacion_historica()

    print(inflacion_historica.head())
    print()
    print(inflacion_historica.tail())
    print()
    print(inflacion_historica.dtypes)