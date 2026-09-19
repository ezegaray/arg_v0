import streamlit as st
import plotly.graph_objects as go

from Fuentes.tipo_cambio import cargar_caso_a


def _mostrar_grafico(datos):
    figura = go.Figure()
    for columna, nombre in [
        ("oficial", "Oficial"),
        ("blue", "Blue"),
        ("caso_a", "Caso A"),
    ]:
        figura.add_trace(
            go.Scatter(
                x=datos["fecha"],
                y=datos[columna],
                mode="lines",
                name=nombre,
            )
        )

    figura.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Pesos por dólar",
        hovermode="x unified",
        dragmode="zoom",
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    st.plotly_chart(
        figura,
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )


def mostrar():

    st.title("Tipo de cambio")

    st.subheader("Tipo de cambio oficial, blue y Caso A")

    datos = cargar_caso_a()

    _mostrar_grafico(datos)

    st.caption(
        "💡 Usá la barra del gráfico para ampliar, desplazar, restablecer "
        "los ejes y mostrar u ocultar series desde la leyenda."
    )

    st.markdown(
        """
        **Caso A**

        Se construye una serie de tipo de cambio de referencia combinando la
        cotización oficial y la cotización blue. Se utiliza el tipo de cambio
        oficial hasta septiembre de 2012; dólar blue entre octubre de 2012 y
        noviembre de 2015; oficial entre diciembre de 2015 y septiembre de
        2019; blue entre octubre de 2019 y marzo de 2025; y nuevamente oficial
        desde abril de 2025.

        Los cambios de criterio considerados corresponden al 1/10/2012,
        17/12/2015, 28/10/2019 y 14/04/2025. Al trabajar con información
        mensual se utiliza la última cotización disponible de cada mes.

        Se trata de una convención analítica simplificada para este ejercicio
        y no pretende representar todas las restricciones, costos o alternativas
        de acceso al mercado cambiario existentes en cada período.
        """
    )

    st.markdown(
        """
        La Comunicación A3500 del Banco Central permite seguir la evolución
        del tipo de cambio de referencia del peso frente al dólar
        estadounidense. La perspectiva histórica permite observar períodos
        de relativa estabilidad cambiaria y otros caracterizados por ajustes
        nominales de mayor magnitud.

        Sin embargo, observar únicamente el tipo de cambio nominal no permite
        determinar cuánto cambió realmente el valor del dólar frente a los
        precios internos de la economía.
        """
    )

    st.markdown(
        """
        Para observar esa relación puede consultarse la sección
        <a href="?seccion=Poder%20de%20compra" target="_self">
        <strong>Poder de compra</strong>
        </a>,
        donde combinamos la evolución del tipo de cambio con el nivel de precios.
        """,
        unsafe_allow_html=True,
    )
