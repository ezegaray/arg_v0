import matplotlib.pyplot as plt
import streamlit as st

from Indicadores.graficos_exploratorios_reales_finales import (
    _leer_horizontes,
    construir_estadisticas_muestras_comunes,
    construir_boxplot_por_horizonte,
    construir_boxplot_por_instrumento,
    filtrar_muestras_comunes,
)


def mostrar():
    st.title("Distribución de rendimientos")
    st.write(
        "Distribución histórica de los rendimientos reales de Plazo fijo, "
        "Dólar, Merval y S&P 500 en pesos para distintos horizontes."
    )
    st.caption(
        "Las ventanas son móviles y se solapan, por lo que las observaciones "
        "no son independientes. Para cada horizonte, todas las alternativas "
        "usan las mismas fechas finales válidas. La categoría mensual muestra "
        "el rendimiento real mensual, no anualizado."
    )

    tablas = filtrar_muestras_comunes(_leer_horizontes())
    st.subheader("Instrumentos por horizonte")
    figura = construir_boxplot_por_horizonte(tablas)
    st.pyplot(figura, width="stretch")
    plt.close(figura)

    st.subheader("Estadísticas descriptivas")
    st.caption(
        "Los rendimientos se expresan en porcentaje; N, período y métricas "
        "corresponden a las mismas muestras que los boxplots."
    )
    estadisticas = construir_estadisticas_muestras_comunes(tablas)
    st.dataframe(estadisticas, hide_index=True, width="stretch")

    st.subheader("Horizontes por instrumento")
    figura = construir_boxplot_por_instrumento(tablas)
    st.pyplot(figura, width="stretch")
    plt.close(figura)
