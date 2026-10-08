import pandas as pd
import streamlit as st


MESES = (
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
)


def _selector(container, label, options, key, default):
    return container.selectbox(
        label,
        options,
        index=options.index(default),
        format_func=lambda value: (
            MESES[value - 1] if label.startswith("Mes") else str(value)
        ),
        key=key,
    )


def mostrar_controles_periodo(
    fechas,
    key,
    ultimos_meses=None,
    fecha_inicio_default=None,
):
    fechas = pd.to_datetime(fechas).dropna()
    if fechas.empty:
        raise ValueError("No hay fechas disponibles para seleccionar el período.")

    periodo_minimo = pd.Period(fechas.min(), freq="M")
    periodo_maximo = pd.Period(fechas.max(), freq="M")
    if fecha_inicio_default is not None:
        periodo_inicio_default = max(
            periodo_minimo,
            min(pd.Period(fecha_inicio_default, freq="M"), periodo_maximo),
        )
    elif ultimos_meses is None:
        periodo_inicio_default = periodo_minimo
    else:
        periodo_inicio_default = max(
            periodo_minimo,
            periodo_maximo - (ultimos_meses - 1),
        )

    opciones_anio_inicio = list(
        range(periodo_minimo.year, periodo_maximo.year + 1)
    )
    columnas = st.columns(4)
    anio_inicio = _selector(
        columnas[0],
        "Año inicial",
        opciones_anio_inicio,
        f"{key}_anio_inicio",
        periodo_inicio_default.year,
    )
    mes_inicio_minimo = (
        periodo_minimo.month if anio_inicio == periodo_minimo.year else 1
    )
    mes_inicio_maximo = (
        periodo_maximo.month if anio_inicio == periodo_maximo.year else 12
    )
    opciones_mes_inicio = list(range(mes_inicio_minimo, mes_inicio_maximo + 1))
    mes_inicio_default = (
        periodo_inicio_default.month
        if anio_inicio == periodo_inicio_default.year
        else mes_inicio_minimo
    )
    mes_inicio = _selector(
        columnas[1],
        "Mes inicial",
        opciones_mes_inicio,
        key=f"{key}_mes_inicio_{anio_inicio}",
        default=mes_inicio_default,
    )

    anio_fin_minimo = anio_inicio
    opciones_anio_fin = list(range(anio_fin_minimo, periodo_maximo.year + 1))
    anio_fin_default = periodo_maximo.year
    anio_fin = _selector(
        columnas[2],
        "Año final",
        opciones_anio_fin,
        f"{key}_anio_fin_{anio_inicio}",
        anio_fin_default,
    )
    mes_fin_minimo = mes_inicio if anio_fin == anio_inicio else 1
    mes_fin_maximo = periodo_maximo.month if anio_fin == periodo_maximo.year else 12
    opciones_mes_fin = list(range(mes_fin_minimo, mes_fin_maximo + 1))
    mes_fin_default = mes_fin_maximo
    mes_fin = _selector(
        columnas[3],
        "Mes final",
        opciones_mes_fin,
        f"{key}_mes_fin_{anio_inicio}_{mes_inicio}_{anio_fin}",
        mes_fin_default,
    )

    return (
        pd.Timestamp(year=anio_inicio, month=mes_inicio, day=1),
        pd.Timestamp(year=anio_fin, month=mes_fin, day=1),
    )
