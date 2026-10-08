from pathlib import Path
import pandas as pd



carpeta_proyecto = Path(__file__).resolve().parent.parent

archivo_procesado = carpeta_proyecto / "data" / "processed" / "tipo_cambio_bcra.csv"



def cargar_bcra():
    if not archivo_procesado.exists():
        raise FileNotFoundError(
            "Falta data/processed/tipo_cambio_bcra.csv. "
            "Primero ejecutá actualizar_bcra()."
        )

    bcra = pd.read_csv(
        archivo_procesado,
        parse_dates=["fecha", "fecha_observacion"],
        dtype={"tipo_cambio": "float64"},
    )
    bcra["mes"] = pd.PeriodIndex(bcra["mes"], freq="M")
    return bcra.sort_values("mes").reset_index(drop=True)


if __name__ == "__main__":
    bcra = cargar_bcra()

    print(bcra.head())
    print()
    print(bcra.tail())
    print()
    print(bcra.dtypes)
