import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from Indicadores.analisis_horizontes import _tabla_horizonte
from Indicadores.analisis_horizontes_reales import _rendimientos_reales
from Indicadores.indice_real_base_100 import _construir_indice
from secciones.marcas_presidenciales import agregar_marcas_politicas


_PERIODO_INICIO_EJE = pd.Period("1996-01", freq="M")
_OPCIONES_HORIZONTE = {
    "Mensual anualizado": "Rendimiento real mensual anualizado (TNA equivalente)",
    "12 meses": "Rendimiento real móvil a 12 meses",
    "3 años": "CAGR real móvil a 3 años",
    "5 años": "CAGR real móvil a 5 años",
    "10 años": "CAGR real móvil a 10 años",
}
_HORIZONTES_INICIALES = {
    "Mensual anualizado": False,
    "12 meses": True,
    "3 años": True,
    "5 años": False,
    "10 años": True,
}
_INSTRUMENTOS = {
    "Plazo fijo": "rend_plazo_fijo",
    "Dólar": "rend_dolar",
    "Merval": "rend_merval",
    "S&P 500 en pesos": "rend_sp500_pesos",
}


def _construir_grafico_real(rendimientos, instrumento, horizontes_seleccionados):
    rendimientos = rendimientos.copy()
    rendimientos["periodo"] = pd.PeriodIndex(rendimientos["periodo"], freq="M")
    rendimiento = (
        rendimientos.set_index("periodo")[instrumento]
        .sort_index()
        .astype("float64")
    )

    rendimiento_visible = rendimiento.loc[
        rendimiento.index >= _PERIODO_INICIO_EJE
    ]
    periodo_base = rendimiento_visible.first_valid_index()
    if periodo_base is None:
        raise ValueError(
            f"No hay rendimientos reales de {instrumento} desde "
            f"{_PERIODO_INICIO_EJE}."
        )
    indice = _construir_indice(rendimiento, periodo_base).dropna()
    horizontes = {
        _OPCIONES_HORIZONTE["Mensual anualizado"]: rendimiento * 12,
        "Rendimiento real móvil a 12 meses": _tabla_horizonte(
            rendimientos, 12
        ).set_index("periodo")[instrumento],
        "CAGR real móvil a 3 años": _tabla_horizonte(
            rendimientos, 36, 3
        ).set_index("periodo")[f"cagr_{instrumento.removeprefix('rend_')}"],
        "CAGR real móvil a 5 años": _tabla_horizonte(
            rendimientos, 60, 5
        ).set_index("periodo")[f"cagr_{instrumento.removeprefix('rend_')}"],
        "CAGR real móvil a 10 años": _tabla_horizonte(
            rendimientos, 120, 10
        ).set_index("periodo")[f"cagr_{instrumento.removeprefix('rend_')}"],
    }
    horizontes = {
        nombre: serie.set_axis(pd.PeriodIndex(serie.index, freq="M")).dropna()
        for nombre, serie in horizontes.items()
    }

    indice = indice.loc[indice.index >= _PERIODO_INICIO_EJE]
    horizontes = {
        nombre: serie.loc[serie.index >= _PERIODO_INICIO_EJE]
        for nombre, serie in horizontes.items()
    }
    periodo_fin = max(
        [indice.index.max(), *(serie.index.max() for serie in horizontes.values())]
    )
    fecha_fin = periodo_fin.end_time

    figura = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.48, 0.52],
        subplot_titles=(
            f"Capital real — base: {periodo_base.to_timestamp():%m/%Y} = 100 "
            "(primer período visible)",
            "Rendimiento real según horizonte",
        ),
    )
    figura.add_trace(
        go.Scatter(
            x=indice.index.to_timestamp(),
            y=indice,
            name=f"Capital real — {_nombre_instrumento(instrumento)}",
            mode="lines",
            line={"color": "#a8e6ff", "width": 2},
            hovertemplate="%{x|%Y-%m}<br>Índice: %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figura.add_hline(
        y=100,
        line={"color": "rgba(230, 230, 230, 0.4)", "dash": "dash", "width": 1},
        row=1,
        col=1,
    )

    estilos = {
        _OPCIONES_HORIZONTE["Mensual anualizado"]: ("#ef5350", "solid", 1.2),
        _OPCIONES_HORIZONTE["12 meses"]: ("#b3ecff", "solid", 1.7),
        _OPCIONES_HORIZONTE["3 años"]: ("#48b4df", "solid", 1.7),
        _OPCIONES_HORIZONTE["5 años"]: ("#207dad", "solid", 1.7),
        _OPCIONES_HORIZONTE["10 años"]: ("#1a6b90", "dot", 2),
    }
    for nombre_opcion in _OPCIONES_HORIZONTE:
        nombre_serie = _OPCIONES_HORIZONTE[nombre_opcion]
        if nombre_opcion not in horizontes_seleccionados:
            continue
        serie = horizontes[nombre_serie]
        color, dash, ancho = estilos[nombre_serie]
        figura.add_trace(
            go.Scatter(
                x=serie.index.to_timestamp(),
                y=serie * 100,
                name=nombre_serie,
                mode="lines",
                line={"color": color, "dash": dash, "width": ancho},
                hovertemplate="%{x|%Y-%m}<br>Tasa: %{y:.2f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )
    figura.add_hline(
        y=0,
        line={"color": "rgba(230, 230, 230, 0.75)", "width": 1},
        row=2,
        col=1,
    )
    figura.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        zerolinecolor="rgba(255, 255, 255, 0.25)",
        color="#f5f5f5",
    )
    figura.update_xaxes(
        range=[_PERIODO_INICIO_EJE.start_time, fecha_fin],
        title_text="Año",
        dtick="M24",
        tickformat="%Y",
        row=2,
        col=1,
    )
    figura.update_yaxes(
        title_text="Índice real",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        zerolinecolor="rgba(255, 255, 255, 0.25)",
        color="#f5f5f5",
        row=1,
        col=1,
    )
    figura.update_yaxes(
        title_text="Tasa anual (%)",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        zerolinecolor="rgba(255, 255, 255, 0.25)",
        color="#f5f5f5",
        row=2,
        col=1,
    )
    figura.update_layout(
        height=780,
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font={"color": "#f5f5f5"},
        hovermode="x unified",
        dragmode="zoom",
        legend={"orientation": "h", "yanchor": "top", "y": -0.14},
        margin={"t": 90, "b": 110, "l": 65, "r": 30},
    )
    agregar_marcas_politicas(figura)
    return figura


def _nombre_instrumento(instrumento):
    return next(
        nombre
        for nombre, columna in _INSTRUMENTOS.items()
        if columna == instrumento
    )


def mostrar():
    st.title("Ahorro e inversión")

    st.subheader("Rendimiento real por instrumento")
    instrumento = st.selectbox(
        "Instrumento",
        options=list(_INSTRUMENTOS),
        key="ahorro_inversion_instrumento",
    )
    columna_rendimiento = _INSTRUMENTOS[instrumento]
    st.caption("El índice de capital parte de 100 en el primer período visible.")
    columnas_controles = st.columns(len(_OPCIONES_HORIZONTE))
    horizontes_seleccionados = [
        opcion
        for columna, opcion in zip(columnas_controles, _OPCIONES_HORIZONTE)
        if columna.checkbox(
            opcion,
            value=_HORIZONTES_INICIALES[opcion],
            key=f"horizonte_{columna_rendimiento}_{opcion}",
        )
    ]
    rendimientos, _ = _rendimientos_reales()
    st.plotly_chart(
        _construir_grafico_real(
            rendimientos,
            columna_rendimiento,
            horizontes_seleccionados,
        ),
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )