import streamlit as st
import plotly.graph_objects as go

from Indicadores.poder_compra_usd import cargar_poder_compra_usd
from secciones.marcas_presidenciales import agregar_marcas_presidenciales


def mostrar():
    st.title("Poder de compra")

    st.subheader("Poder de compra del dólar en Argentina")

    datos = cargar_poder_compra_usd()

    figura = go.Figure(
        go.Scatter(
            x=datos["fecha"],
            y=datos["poder_compra_usd"],
            mode="lines",
            name="Poder de compra del dólar",
        )
    )
    figura.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Índice (dic. 2016 = 100)",
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

    st.caption(
        "💡 Gráfico interactivo: podés seleccionar un período "
        "para explorar con mayor detalle la evolución de la serie."
    )

    st.markdown(
        """
        Desde comienzos de la década de 2000, el poder de compra del dólar
        atravesó etapas muy diferentes en la Argentina. Observar la serie en
        perspectiva permite distinguir períodos en los que la evolución del
        tipo de cambio superó a la de los precios internos y otros en los que
        ocurrió lo contrario. El índice toma diciembre de 2016 como base 100,
        por lo que valores superiores o inferiores permiten comparar la
        posición relativa del dólar respecto de ese momento.

        La perspectiva de largo plazo también permite evitar que movimientos
        de corto plazo dominen la interpretación. Al seleccionar períodos más
        pequeños en el gráfico pueden analizarse con mayor detalle distintas
        etapas económicas y observar con qué velocidad cambiaron las
        relaciones entre el tipo de cambio nominal y el nivel general de
        precios.
        """
    )