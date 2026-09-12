import streamlit as st

from Indicadores.poder_compra_usd import cargar_poder_compra_usd


def mostrar():
    st.title("Poder de compra")

    st.subheader("Poder de compra del dólar en Argentina")

    datos = cargar_poder_compra_usd()

    st.line_chart(
        datos,
        x="fecha",
        y="poder_compra_usd",
        x_label="Fecha",
        y_label="Índice (dic. 2016 = 100)",
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