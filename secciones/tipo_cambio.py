import streamlit as st

from Fuentes.bcra import cargar_bcra


def mostrar():

    st.title("Tipo de cambio")

    st.subheader("Tipo de cambio de referencia A3500 - BCRA")

    datos = cargar_bcra()

    st.line_chart(
        datos,
        x="fecha",
        y="tipo_cambio",
        x_label="Fecha",
        y_label="Pesos por dólar",
    )

    st.caption(
        "💡 Podés seleccionar una parte del gráfico "
        "para ampliar el período que quieras analizar."
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
