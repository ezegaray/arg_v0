import streamlit as st
import plotly.express as px

from Indicadores.poder_compra_usd import cargar_poder_compra_usd
from Fuentes.bcra import cargar_bcra
from Fuentes.inflacion import cargar_inflacion


# --------------------------------------------------
# Carga de datos
# --------------------------------------------------

@st.cache_data
def obtener_bcra():
    return cargar_bcra()


@st.cache_data
def obtener_inflacion():
    return cargar_inflacion()


tc = obtener_bcra()
inflacion = obtener_inflacion()

@st.cache_data
def obtener_poder_compra_usd():
    return cargar_poder_compra_usd()

poder_compra_usd = obtener_poder_compra_usd()

# --------------------------------------------------
# Encabezado
# --------------------------------------------------

st.title("Tablero interactivo de indicadores económicos")
st.write("v1")


# --------------------------------------------------
# Tipo de cambio
# --------------------------------------------------

st.subheader("TC - A3500")

fig_tc = px.line(
    tc,
    x="fecha",
    y="tipo_cambio",
)

fig_tc.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Pesos por dólar",
)

st.plotly_chart(
    fig_tc,
    width="stretch",
    config={
        "displaylogo": False,
        "displayModeBar": True,
    },
)


# --------------------------------------------------
# Inflación
# --------------------------------------------------

st.subheader("IPC - Indec")

fecha_min = inflacion["fecha"].min().date()
fecha_max = inflacion["fecha"].max().date()

rango_fechas = st.date_input(
    "Período",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max,
)


if len(rango_fechas) == 2:
    desde, hasta = rango_fechas

    inflacion_filtrada = inflacion[
        (inflacion["fecha"].dt.date >= desde)
        & (inflacion["fecha"].dt.date <= hasta)
    ].copy()
else:
    inflacion_filtrada = inflacion.copy()


fig = px.line(
    inflacion_filtrada,
    x="fecha",
    y="Indice_IPC",
)

fig.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Índice",
)


st.plotly_chart(
    fig,
    width="stretch",
    config={
        "displaylogo": False,
        "displayModeBar": True,
    },
)



# --------------------------------------------------
# Poder de compra local de USD 100
# --------------------------------------------------

st.subheader("Poder de compra local de USD 100")

fig_pc = px.line(
    poder_compra_usd,
    x="fecha",
    y="poder_compra_usd",
)

fig_pc.update_layout(
    xaxis_title="Fecha",
    yaxis_title="Índice (dic-2016 = 100)",
)

st.plotly_chart(
    fig_pc,
    width="stretch",
    config={
        "displaylogo": False,
        "displayModeBar": True,
    },
)

st.caption(
    "Índice del poder de compra local de USD 100 al tipo de cambio oficial. "
    "Diciembre de 2016 = 100."
)