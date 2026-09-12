import streamlit as st

from secciones import poder_compra
from secciones import tipo_cambio
from secciones import inflacion
from secciones import ahorro_inversion


st.set_page_config(
    page_title="Coyuntura Argentina - Tablero web interactivo",
    layout="wide",
)


## NAVEGACION 
#############

secciones = [
    "Poder de compra",
    "Tipo de cambio",
    "Inflación",
    "Ahorro e inversión",
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

if pagina_url == "Portada":
    indice_inicial = None
else:
    indice_inicial = secciones.index(pagina_url)


seccion = st.sidebar.radio(
    "Secciones",
    secciones,
    index=indice_inicial,
    label_visibility="collapsed",
)



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
        - **Poder de compra:** evolución del valor relativo del dólar frente
          al nivel de precios.
        - **Tipo de cambio:** series históricas del mercado cambiario.
        - **Inflación:** evolución de precios e indicadores relacionados.
        - **Ahorro e inversión:** comparación de alternativas de inversión
          y conservación del poder adquisitivo.
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