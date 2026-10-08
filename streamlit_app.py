import streamlit as st

from secciones import poder_compra
from secciones import tipo_cambio
from secciones import inflacion
from secciones import ahorro_inversion
from secciones import tasas_interes


st.set_page_config(
    page_title="Coyuntura Argentina - Tablero web interactivo",
    layout="wide",
)


## NAVEGACION 
#############

secciones = [
    "Ahorro e inversión",
    "Poder de compra",
    "Inflación",
    "Tipo de cambio",
    "Tasa de interés",
]

pagina_url = st.query_params.get(
    "seccion",
    "Portada",
)

if pagina_url != "Portada" and pagina_url not in secciones:
    pagina_url = "Portada"


st.sidebar.title("Reporte económico")

if st.sidebar.button("🏠 Inicio", use_container_width=True):
    st.query_params["seccion"] = "Portada"
    st.rerun()


st.sidebar.markdown("### Secciones")

grupos_secciones = {
    "Análisis": ["Ahorro e inversión", "Poder de compra"],
    "Indicadores / series": ["Inflación", "Tipo de cambio", "Tasa de interés"],
}
for grupo, opciones in grupos_secciones.items():
    st.sidebar.markdown(f"### {grupo}")
    for opcion in opciones:
        if st.sidebar.button(
            opcion,
            key=f"navegacion_{opcion}",
            type="primary" if pagina_url == opcion else "secondary",
            use_container_width=True,
        ):
            st.query_params["seccion"] = opcion
            st.rerun()

seccion = None if pagina_url == "Portada" else pagina_url



## SECCIONES? 
#############


# Si el usuario cambia de sección desde la barra lateral,
# actualizamos también la URL.
if pagina_url == "Portada":

    st.title("Coyuntura Argentina")

    st.write(
        """
        Tablero web interactivo para explorar la evolución de distintas
        variables de la economía argentina.
        """
    )

    st.subheader("Secciones")

    st.markdown(
        """
        **Análisis**

        - **Ahorro e inversión:** análisis de alternativas de inversión
          y conservación del poder adquisitivo.
        - **Poder de compra:** evolución del valor relativo del dólar frente
          al nivel de precios.

        **Indicadores / Series**

        - **Inflación:** evolución de precios e indicadores relacionados.
        - **Tipo de cambio:** series históricas del mercado cambiario.
        - **Tasa de interés:** tasas de depósitos a plazo fijo.
        """
    )

    # Si desde Inicio el usuario elige una sección,
    # actualizamos la URL y navegamos hacia ella.
    if seccion is not None:
        st.query_params["seccion"] = seccion
        st.rerun()


else:

    if seccion != pagina_url:
        st.query_params["seccion"] = seccion
        st.rerun()

    if seccion == "Poder de compra":
        poder_compra.mostrar()

    elif seccion == "Tipo de cambio":
        tipo_cambio.mostrar()

    elif seccion == "Inflación":
        inflacion.mostrar()

    elif seccion == "Ahorro e inversión":
        ahorro_inversion.mostrar()

    elif seccion == "Tasa de interés":
        tasas_interes.mostrar()