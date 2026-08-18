from pathlib import Path
from urllib.request import urlretrieve


url = "https://www.bcra.gob.ar/archivos/Pdfs/PublicacionesEstadisticas/com3500.xls"

carpeta_proyecto = Path(__file__).resolve().parent

archivo_destino = (
    carpeta_proyecto
    / "data"
    / "raw"
    / "tipo_cambio_bcra.xls"
)

archivo_destino.parent.mkdir(
    parents=True,
    exist_ok=True,
)

urlretrieve(
    url,
    archivo_destino,
)

print(f"Archivo actualizado: {archivo_destino}")