import streamlit as st

from Fuentes.tasas_interes import cargar_tasa


def mostrar():
    st.title("Tasa de interés")
    st.subheader("Tasa de depósitos a plazo fijo - BCRA")

    try:
        datos = cargar_tasa()
    except FileNotFoundError as error:
        st.warning(str(error))
        return

    st.line_chart(
        datos,
        x="fecha",
        y="tasa",
        x_label="Fecha",
        y_label="Tasa nominal anual (%)",
    )