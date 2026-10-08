import streamlit as st
import plotly.graph_objects as go

from Fuentes.tasas_interes import cargar_tasa
from secciones.marcas_presidenciales import agregar_marcas_presidenciales


def mostrar():
    st.title("Tasa de interés")
    st.subheader("Tasa de depósitos a plazo fijo - BCRA")

    try:
        datos = cargar_tasa()
    except FileNotFoundError as error:
        st.warning(str(error))
        return

    figura = go.Figure(
        go.Scatter(
            x=datos["fecha"],
            y=datos["tasa"],
            mode="lines",
            name="Tasa de depósitos a plazo fijo",
        )
    )
    figura.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Tasa nominal anual (%)",
        hovermode="x unified",
        dragmode="zoom",
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    agregar_marcas_presidenciales(figura)
    st.plotly_chart(
        figura,
        use_container_width=True,
        config={"displaylogo": False, "scrollZoom": True, "displayModeBar": True},
    )