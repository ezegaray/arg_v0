import streamlit as st


from bcra import datos



st.title("Reporte de coyuntura económica Argentina")
st.write("Primera versión del proyecto.")





st.write("Tipo de objeto:", str(type(datos)))
st.write("Tipos de las columnas:")

st.write(datos.dtypes.astype(str))





st.write(datos.head())


st.subheader("Tipo de cambio nominal promedio mensual")

st.line_chart(
    datos,
    x="fecha",
    y="tipo_cambio",
)

