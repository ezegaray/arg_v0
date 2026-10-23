import matplotlib.pyplot as plt
import streamlit as st

from Indicadores.graficos_exploratorios_reales_finales import (
    _leer_horizontes,
    construir_boxplot_por_horizonte,
    construir_boxplot_por_instrumento,
    filtrar_muestras_comunes,
)


def mostrar():
    st.title("Distribución de rendimientos")
    st.write(
        """
Los gráficos temporales de la sección
[Ahorro e inversión](?seccion=Ahorro%20e%20inversi%C3%B3n) permiten identificar cuándo
ocurrieron los períodos
positivos y negativos, pero dificultan resumir cómo se distribuyeron los
resultados históricos. Los boxplots complementan esa mirada mostrando, para
cada horizonte, la mediana, la dispersión y los valores extremos de los
rendimientos reales obtenidos por cada alternativa. Para hacer comparables
las distribuciones, cada horizonte utiliza exactamente las mismas fechas
para los cuatro instrumentos.

La comparación muestra perfiles muy diferentes. En el plazo fijo predominan
ampliamente los resultados negativos y esa característica no desaparece al
aumentar el horizonte. El dólar presenta numerosos períodos de pérdida real
y episodios positivos de gran magnitud, particularmente visibles en
horizontes cortos. En los índices accionarios, en cambio, los resultados
positivos se vuelven mayoritarios en los horizontes largos de la muestra: a
diez años fueron positivos aproximadamente el 77% de los períodos del
Merval y el 65% de los del S&P 500 en pesos.

Estos resultados muestran una fuerte sensibilidad al momento de ingreso y a la inclusión, dentro de cada horizonte, de episodios positivos o negativos de gran magnitud ocurridos en momentos puntuales.

"""
    )
    st.caption(
        "Las ventanas son móviles y se solapan, por lo que las observaciones "
        "no son independientes. Para cada horizonte, todas las alternativas "
        "usan las mismas fechas finales válidas. La categoría mensual muestra "
        "el rendimiento real mensual, no anualizado."
    )

    tablas = filtrar_muestras_comunes(_leer_horizontes())

    st.subheader("Horizontes por instrumento")
    figura = construir_boxplot_por_instrumento(tablas)
    _, grafico, _ = st.columns([1, 6, 1])
    with grafico:
        st.pyplot(figura, width="stretch")
    plt.close(figura)

    st.write(
        """
Los boxplots también ayudan a evitar una interpretación engañosa de los
gráficos temporales. Las curvas de rendimientos de largo plazo parecen más
suaves en parte porque las ventanas consecutivas comparten gran cantidad de
meses entre sí. Por eso, una curva temporal menos oscilante no equivale por
sí sola a menor riesgo. La distribución de resultados ofrece una perspectiva
complementaria para observar tanto la variabilidad como la frecuencia
histórica de ganancias y pérdidas.

"""
    )

    st.subheader("Instrumentos por horizonte")
    figura = construir_boxplot_por_horizonte(tablas)
    _, grafico, _ = st.columns([1, 6, 1])
    with grafico:
        st.pyplot(figura, width="stretch")
    plt.close(figura)
