from pathlib import Path

import pandas as pd
import yfinance as yf


CARPETA_PROCESSED = Path(__file__).resolve().parent.parent / "data" / "processed"
ARCHIVO_SP500_MENSUAL = CARPETA_PROCESSED / "sp500_mensual.csv"

SERIES = {
    "^GSPC": "sp500_mensual.csv",
    "^MERV": "merval_mensual.csv",
}


def cargar_sp500_mensual():
    if not ARCHIVO_SP500_MENSUAL.exists():
        raise FileNotFoundError(
            "Falta data/processed/sp500_mensual.csv. "
            "Primero ejecutá actualizar_bolsas()."
        )

    datos = pd.read_csv(
        ARCHIVO_SP500_MENSUAL,
        parse_dates=["fecha"],
        dtype={"cierre": "float64"},
    )
    datos = (
        datos.dropna(subset=["fecha", "cierre"])
        .drop_duplicates(subset=["fecha"], keep="last")
        .sort_values("fecha")
        .reset_index(drop=True)
    )
    if datos.empty:
        raise ValueError("La serie mensual del S&P 500 no contiene observaciones.")
    return datos


def descargar_serie(ticker):
    """Descarga el histórico diario y construye el último cierre de cada mes."""
    datos = yf.download(
        ticker,
        period="max",
        interval="1d",
        auto_adjust=False,
        progress=False,
        group_by="column",
    )

    if datos.empty:
        raise ValueError(f"Yahoo Finance no devolvió datos para {ticker}.")

    cierre = datos["Close"]
    if isinstance(cierre, pd.DataFrame):
        cierre = cierre.iloc[:, 0]

    diario = (
        cierre.rename("cierre")
        .rename_axis("fecha")
        .reset_index()
    )
    diario["fecha"] = pd.to_datetime(diario["fecha"], errors="coerce")
    diario["cierre"] = pd.to_numeric(diario["cierre"], errors="coerce")
    diario = (
        diario.dropna(subset=["fecha", "cierre"])
        .drop_duplicates(subset=["fecha"], keep="last")
        .sort_values("fecha")
        .reset_index(drop=True)
    )

    mensual = diario.assign(mes=diario["fecha"].dt.to_period("M"))
    mensual = (
        mensual.groupby("mes", as_index=False)
        .tail(1)
        .sort_values("fecha")
        .reset_index(drop=True)
    )
    return diario[["fecha", "cierre"]], mensual[["fecha", "cierre"]]


def actualizar_bolsas():
    """Descarga y guarda las series mensuales bursátiles de Yahoo Finance."""
    CARPETA_PROCESSED.mkdir(parents=True, exist_ok=True)
    resultados = {}

    for ticker, nombre_archivo in SERIES.items():
        diario, mensual = descargar_serie(ticker)
        destino = CARPETA_PROCESSED / nombre_archivo
        mensual.to_csv(destino, index=False, date_format="%Y-%m-%d")
        resultados[ticker] = {
            "archivo": destino,
            "diario": diario,
            "mensual": mensual,
        }

    return resultados