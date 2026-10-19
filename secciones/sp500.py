import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from Fuentes.bolsa import cargar_sp500_mensual
from secciones.controles_periodo import mostrar_controles_periodo
from secciones.marcas_presidenciales import agregar_marcas_politicas


def mostrar():
    st.title("S&P 500 (USD)")
    st.subheader("S&P 500 en dólares estadounidenses corrientes")
    st.caption(
        "Cierre mensual del índice, expresado en puntos cotizados en USD "
        "corrientes, sin ajuste por inflación."
    )

    try:
        datos = cargar_sp500_mensual()
    except FileNotFoundError as error:
        st.warning(str(error))
        return

    fecha_minima = datos["fecha"].min()
    fecha_maxima = datos["fecha"].max()
    st.caption(
        f"Datos disponibles: {fecha_minima:%m/%Y} – {fecha_maxima:%m/%Y}"
    )

    fecha_inicio, fecha_fin = mostrar_controles_periodo(
        datos["fecha"],
        key="sp500_usd",
    )
    periodo_inicio = fecha_inicio.to_period("M")
    periodo_fin = fecha_fin.to_period("M")
    seleccion = datos[
        datos["fecha"].dt.to_period("M").between(periodo_inicio, periodo_fin)
    ]
    st.caption(
        f"Período seleccionado: {fecha_inicio:%m/%Y} – {fecha_fin:%m/%Y}"
    )

    figura = go.Figure(
        go.Scatter(
            x=seleccion["fecha"],
            y=seleccion["cierre"],
            mode="lines",
            name="S&P 500 (USD corrientes)",
            line={"color": "#4c78a8", "width": 1.5},
            hovertemplate="%{x|%Y-%m}<br>Índice: %{y:,.2f}<extra></extra>",
        )
    )
    figura.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Puntos del índice (USD corrientes)",
        hovermode="x unified",
        dragmode="zoom",
        xaxis_range=[
            fecha_inicio.isoformat(),
            (fecha_fin + pd.offsets.MonthEnd(1)).isoformat(),
        ],
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    agregar_marcas_politicas(figura)
    st.plotly_chart(
        figura,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )
