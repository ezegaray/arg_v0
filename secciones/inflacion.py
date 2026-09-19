import streamlit as st
import plotly.graph_objects as go

from Fuentes.inflacion import cargar_inflacion


def _mostrar_grafico(datos, columna, titulo_eje, tipo="line"):
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

    st.title("Inflación")

    vista = st.radio(
        "Vista",
        [
            "Nivel del IPC",
            "Variación mensual",
        ],
        horizontal=True,
    )

    ipc = cargar_inflacion()

    if vista == "Nivel del IPC":

        st.subheader("Índice de Precios al Consumidor - Argentina")

        _mostrar_grafico(ipc, "Indice_IPC", "Índice")

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
            ipc,
            "inflacion_mensual",
            "Variación mensual (%)",
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