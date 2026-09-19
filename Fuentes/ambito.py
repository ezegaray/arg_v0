import json
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

import pandas as pd


carpeta_proyecto = Path(__file__).resolve().parent.parent
archivo_raw = carpeta_proyecto / "data" / "raw" / "dolar_blue_ambito.json"
archivo_procesado = carpeta_proyecto / "data" / "dolar_blue.csv"

URL_BASE = "https://mercados.ambito.com/dolar/informal/historico-general"
FECHA_INICIAL = date(2002, 1, 1)
COLUMNAS = ["fecha", "compra", "venta"]


def descargar_datos(desde, hasta=None):
    """Descarga las filas de Ámbito para un intervalo inclusivo."""
    hasta = hasta or date.today()
    url = f"{URL_BASE}/{desde:%Y-%m-%d}/{hasta:%Y-%m-%d}"
    solicitud = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.ambito.com/contenidos/dolar-informal-historico.html",
        },
    )

    with urlopen(solicitud, timeout=60) as respuesta:
        datos = json.load(respuesta)

    if not datos or datos[0] != ["Fecha", "Compra", "Venta"]:
        raise ValueError("La respuesta de Ámbito no tiene el formato esperado.")

    return datos


def _leer_raw():
    if not archivo_raw.exists():
        return None

    with archivo_raw.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)

    return datos if datos and datos[0] == ["Fecha", "Compra", "Venta"] else None


def _guardar_raw(datos):
    archivo_raw.parent.mkdir(parents=True, exist_ok=True)
    with archivo_raw.open("w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


def actualizar_datos():
    """Descarga el histórico inicial o agrega el período desde la última fecha."""
    datos_raw = _leer_raw()
    if datos_raw is None:
        datos_raw = descargar_datos(FECHA_INICIAL)
    else:
        datos_existentes = limpiar_datos(datos_raw)
        ultima_fecha = datos_existentes["fecha"].max().date()
        datos_nuevos = descargar_datos(ultima_fecha)
        filas_existentes = {tuple(fila) for fila in datos_raw[1:]}
        filas_nuevas = [
            fila
            for fila in datos_nuevos[1:]
            if tuple(fila) not in filas_existentes
        ]
        datos_raw = datos_raw + filas_nuevas

    _guardar_raw(datos_raw)
    datos = limpiar_datos(datos_raw)
    datos.to_csv(archivo_procesado, index=False, date_format="%Y-%m-%d")
    return datos


def _convertir_numero(valores):
    valores = valores.astype("string").str.strip()
    con_miles = valores.str.contains(".", regex=False) & valores.str.contains(",")
    valores = valores.where(~con_miles, valores.str.replace(".", "", regex=False))
    return pd.to_numeric(valores.str.replace(",", ".", regex=False), errors="coerce")


def limpiar_datos(datos):
    datos = pd.DataFrame(datos[1:], columns=COLUMNAS).copy()
    datos["fecha"] = pd.to_datetime(
        datos["fecha"],
        format="%d/%m/%Y",
        errors="coerce",
    )
    datos["compra"] = _convertir_numero(datos["compra"])
    datos["venta"] = _convertir_numero(datos["venta"])
    datos = datos.dropna(subset=COLUMNAS)

    datos = (
        datos.sort_index()
        .drop_duplicates(subset="fecha", keep="first")
        .sort_values("fecha")
        .reset_index(drop=True)
    )
    datos["tipo_cambio"] = (datos["compra"] + datos["venta"]) / 2
    return datos[["fecha", "compra", "venta", "tipo_cambio"]]


def cargar_dolar_blue():
    if not archivo_procesado.exists():
        raise FileNotFoundError(
            "Falta data/dolar_blue.csv. Primero ejecutá actualizar_ambito()."
        )

    return pd.read_csv(
        archivo_procesado,
        parse_dates=["fecha"],
        dtype={
            "compra": "float64",
            "venta": "float64",
            "tipo_cambio": "float64",
        },
    )


def construir_serie_mensual(datos):
    """Devuelve el último registro efectivamente disponible de cada mes."""
    datos = datos.sort_values("fecha").copy()
    mensual = datos.assign(mes=datos["fecha"].dt.to_period("M"))
    mensual = mensual.groupby("mes", as_index=False).tail(1)
    return mensual.sort_values("mes").reset_index(drop=True)