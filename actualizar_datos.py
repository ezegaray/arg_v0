from pathlib import Path
from urllib.request import urlretrieve
import argparse
import pandas as pd



# --------------------------------------------------
# Carpetas del proyecto
# --------------------------------------------------

carpeta_proyecto = Path(__file__).resolve().parent
carpeta_raw = carpeta_proyecto / "data" / "raw"
carpeta_processed = carpeta_proyecto / "data" / "processed"

carpeta_raw.mkdir(
    parents=True,
    exist_ok=True,
)



# --------------------------------------------------
# BCRA - Tipo de cambio A3500
# --------------------------------------------------

def actualizar_bcra():
    url = (
        "https://www.bcra.gob.ar/archivos/Pdfs/"
        "PublicacionesEstadisticas/com3500.xls"
    )

    archivo_destino = (
        carpeta_raw
        / "tipo_cambio_bcra.xls"
    )

    urlretrieve(
        url,
        archivo_destino,
    )

    procesar_tas1(archivo_destino)

    print(
        f"Archivo BCRA actualizado: "
        f"{archivo_destino}"
    )



# --------------------------------------------------
# INDEC - IPC
# --------------------------------------------------

def actualizar_ipc():
    url = (
        "https://www.indec.gob.ar/ftp/cuadros/"
        "economia/serie_ipc_divisiones.csv"
    )

    archivo_destino = (
        carpeta_raw
        / "serie_ipc_divisiones.csv"
    )

    urlretrieve(
        url,
        archivo_destino,
    )

    print(
        f"Archivo IPC actualizado: "
        f"{archivo_destino}"
    )


# --------------------------------------------------
# BCRA - Tasas de interés
# --------------------------------------------------


def actualizar_tas1():
    url = (
        "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/"
        "tas1_ser.txt"
    )

    archivo_destino = (
        carpeta_raw
        / "tas1_ser.txt"
    )

    urlretrieve(
        url,
        archivo_destino,
    )

    print(
        f"Archivo tasas BCRA actualizado: "
        f"{archivo_destino}"
    )


def procesar_tas1(archivo_origen):
    archivo_destino = carpeta_processed / "tasa_plazo_fijo.csv"
    carpeta_processed.mkdir(
        parents=True,
        exist_ok=True,
    )

    bloques = []
    lector = pd.read_csv(
        archivo_origen,
        sep=";",
        header=None,
        names=["codigo", "fecha", "valor"],
        usecols=[0, 1, 2],
        dtype={"codigo": "string", "fecha": "string"},
        chunksize=200_000,
    )

    for bloque in lector:
        bloque = bloque[bloque["codigo"].eq("2324")].copy()
        if bloque.empty:
            continue

        bloque["fecha"] = pd.to_datetime(
            bloque["fecha"],
            format="%d/%m/%Y",
            errors="coerce",
        )
        bloque["tasa"] = pd.to_numeric(
            bloque["valor"],
            errors="coerce",
        )
        bloque = bloque.dropna(subset=["fecha", "tasa"])

        if not bloque.empty:
            bloques.append(bloque[["fecha", "tasa"]])

    datos = pd.concat(bloques, ignore_index=True)
    datos = datos.sort_values("fecha").reset_index(drop=True)
    datos.to_csv(archivo_destino, index=False, date_format="%Y-%m-%d")



