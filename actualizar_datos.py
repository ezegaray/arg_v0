from pathlib import Path
from urllib.request import urlretrieve
import argparse



# --------------------------------------------------
# Carpetas del proyecto
# --------------------------------------------------

carpeta_proyecto = Path(__file__).resolve().parent
carpeta_raw = carpeta_proyecto / "data" / "raw"

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



