import pandas as pd

url = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls"

datos = pd.read_excel(
    url,
    sheet_name="Serie de TCNPM",
    usecols="B:C",
    skiprows=1
)
datos = datos.dropna()

datos = datos.rename(
    columns={
        "Mes": "fecha",
        "Tipo de cambio nominal promedio mensual": "tipo_cambio"
    }
)


datos["fecha"] = pd.to_datetime(
    datos["fecha"],
    errors="coerce",
)

datos["tipo_cambio"] = pd.to_numeric(
    datos["tipo_cambio"],
    errors="coerce",
)

datos = datos.dropna(
    subset=["fecha", "tipo_cambio"],
)

datos = datos.sort_values("fecha")