from pathlib import Path
import pandas as pd


carpeta_proyecto = Path(__file__).resolve().parent.parent

archivo_ipc = (
    carpeta_proyecto
    / "data"
    / "raw"
    / "serie_ipc_divisiones.csv"
)

def cargar_ipc():
    ipc = pd.read_csv(
        archivo_ipc,
        sep=";",
        decimal=",",
        na_values=["NA"],
        encoding="latin1",
        )

    ipc = ipc[
        (ipc["Codigo"] == "0") &
        (ipc["Region"] == "Nacional")
    ].copy()

    ipc["fecha"] = pd.to_datetime(
        ipc["Periodo"].astype(str),
        format="%Y%m"
    )

    ipc = ipc.sort_values("fecha")

    ipc["inflacion_mensual"] = (
        ipc["Indice_IPC"] / ipc["Indice_IPC"].shift(1) - 1
    ) * 100

    ipc = ipc[
        [
            "fecha",
            "Indice_IPC",
            "inflacion_mensual",
        ]
        ]

    return ipc


if __name__ == "__main__":
    ipc = cargar_ipc()

    print(ipc.head())
    print()
    print(ipc.tail())
    print()
    print(ipc.dtypes)

