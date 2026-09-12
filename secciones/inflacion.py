import streamlit as st

from Fuentes.indec_ipc import cargar_ipc


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

    ipc = cargar_ipc()

    if vista == "Nivel del IPC":

        st.subheader("Índice de Precios al Consumidor - Argentina")

        st.line_chart(
            ipc,
            x="fecha",
            y="Indice_IPC",
            x_label="Fecha",
            y_label="Índice",
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

        st.line_chart(
            ipc,
            x="fecha",
            y="inflacion_mensual",
            x_label="Fecha",
            y_label="Variación mensual (%)",
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