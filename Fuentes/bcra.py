from pathlib import Path
import pandas as pd



carpeta_proyecto = Path(__file__).resolve().parent.parent

archivo_bcra = (
    carpeta_proyecto
    / "data"
    / "raw"
    / "tipo_cambio_bcra.xls"
)



def cargar_bcra():
    bcra  = pd.read_excel(
        archivo_bcra,
        sheet_name="Serie de TCNPM",
        usecols="B:C",
        skiprows=1
    )
    bcra  = bcra.dropna()

    bcra  = bcra.rename(
        columns={
            "Mes": "fecha",
            "Tipo de cambio nominal promedio mensual": "tipo_cambio"
        }
    )


    bcra ["fecha"] = pd.to_datetime(
        bcra ["fecha"],
        errors="coerce",
    )

    bcra ["tipo_cambio"] = pd.to_numeric(
        bcra ["tipo_cambio"],
        errors="coerce",
    )

    bcra  = bcra .dropna(
        subset=["fecha", "tipo_cambio"],
    )

    bcra  = bcra .sort_values("fecha")

    return bcra


if __name__ == "__main__":
    bcra = cargar_bcra()

    print(bcra.head())
    print()
    print(bcra.tail())
    print()
    print(bcra.dtypes)
