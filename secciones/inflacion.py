import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from Fuentes.inflacion import cargar_inflacion
from secciones.controles_periodo import mostrar_controles_periodo
from secciones.marcas_presidenciales import agregar_marcas_presidenciales


def _mostrar_grafico(
    datos,
    columna,
    titulo_eje,
    fecha_inicio,
    fecha_fin,
    tipo="line",
    escala_y=None,
):
    figura = go.Figure()
    constructor = figura.add_bar if tipo == "bar" else figura.add_scatter
    parametros = {
        "x": datos["fecha"],
        "y": datos[columna],
        "name": titulo_eje,
    }
    if tipo == "line":
        parametros.update(mode="lines")
    constructor(**parametros)
    figura.update_layout(
        xaxis_title="Fecha",
        yaxis_title=titulo_eje,
        hovermode="x unified",
        dragmode="zoom",
        xaxis_range=[
            fecha_inicio.isoformat(),
            (fecha_fin + pd.offsets.MonthEnd(1)).isoformat(),
        ],
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
    )
    if escala_y is not None:
        figura.update_yaxes(type=escala_y)
    agregar_marcas_presidenciales(figura)
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

    st.title("Inflación")

    vista = st.radio(
        "Vista",
        [
            "Variación mensual",
            "Inflación últimos 12 meses",
            "Nivel del IPC",
        ],
        horizontal=True,
        index=1,
        key="inflacion_vista_v2",
    )

    ipc = cargar_inflacion()
    ipc["inflacion_12m"] = (
        ipc["Indice_IPC"]
        .div(ipc["Indice_IPC"].shift(12))
        .sub(1)
        * 100
    )
    fecha_minima = ipc["fecha"].min()
    fecha_maxima = ipc["fecha"].max()
    st.caption(
        f"Datos disponibles: {fecha_minima:%m/%Y} – {fecha_maxima:%m/%Y}"
    )

    fecha_inicio_default = None
    if vista == "Nivel del IPC":
        ultimos_meses = None
        key_periodo = "inflacion_nivel"
    elif vista == "Inflación últimos 12 meses":
        ultimos_meses = None
        fecha_inicio_default = "2002-01"
        key_periodo = "inflacion_interanual"
    else:
        ultimos_meses = 60
        key_periodo = "inflacion_mensual"

    fecha_inicio, fecha_fin = mostrar_controles_periodo(
        ipc["fecha"],
        key=key_periodo,
        ultimos_meses=ultimos_meses,
        fecha_inicio_default=fecha_inicio_default,
    )
    periodo_inicio = fecha_inicio.to_period("M")
    periodo_fin = fecha_fin.to_period("M")
    seleccion = ipc[
        ipc["fecha"].dt.to_period("M").between(periodo_inicio, periodo_fin)
    ]
    st.caption(
        f"Período seleccionado: {fecha_inicio:%m/%Y} – {fecha_fin:%m/%Y}"
    )

    if vista == "Nivel del IPC":

        st.subheader("Índice de Precios al Consumidor - Argentina")
        st.caption("Base: diciembre de 2016 = 100")

        escala = st.radio(
            "Escala del eje Y",
            ["Logarítmica", "Lineal"],
            horizontal=True,
            index=0,
            key="inflacion_escala_nivel",
        )
        _mostrar_grafico(
            seleccion,
            "Indice_IPC",
            "Índice",
            fecha_inicio,
            fecha_fin,
            escala_y="log" if escala == "Logarítmica" else "linear",
        )

        st.caption(
            "💡 Podés seleccionar una parte del gráfico "
            "para ampliar el período que quieras analizar."
        )

        st.markdown(
            """
            El Índice de Precios al Consumidor permite seguir la evolución
            general de los precios de bienes y servicios consumidos por los hogares.
            En esta serie se muestra el nivel del índice publicado por el INDEC
            para el total nacional.

            Observar el índice en niveles permite apreciar el efecto acumulado de
            la inflación a lo largo del tiempo.
            """
        )

    elif vista == "Variación mensual":

        st.subheader("Inflación mensual - Argentina")

        _mostrar_grafico(
            seleccion,
            "inflacion_mensual",
            "Variación mensual (%)",
            fecha_inicio,
            fecha_fin,
            tipo="bar",
        )

        st.caption(
            "💡 Podés seleccionar una parte del gráfico "
            "para ampliar el período que quieras analizar."
        )

        st.markdown(
            """
            La variación mensual muestra cuánto cambiaron los precios respecto
            del mes anterior. Esta vista permite identificar con mayor claridad
            períodos de aceleración o desaceleración inflacionaria.

            A diferencia del nivel del índice, que acumula los aumentos de precios
            a lo largo del tiempo, esta serie permite comparar directamente la
            intensidad de la inflación entre distintos meses.
            """
        )

    elif vista == "Inflación últimos 12 meses":

        st.subheader("Inflación últimos 12 meses - Argentina")

        _mostrar_grafico(
            seleccion,
            "inflacion_12m",
            "Variación interanual (%)",
            fecha_inicio,
            fecha_fin,
            tipo="bar",
        )

        st.caption(
            "💡 Fórmula: IPC actual / IPC de hace 12 meses − 1, expresada en %."
        )