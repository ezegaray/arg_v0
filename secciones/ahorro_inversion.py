import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from Indicadores.plazo_fijo_vs_dolar import cargar_comparacion


def _mostrar_grafico(datos):
    periodos = datos["periodo"].tolist()[::-1]
    figura = go.Figure()
    configuraciones = [
        ("valor_final_dolar", "Dólar - Caso A", "#4c78a8"),
        ("valor_final_pf", "Plazo fijo", "#f58518"),
    ]
    for columna, nombre, color in configuraciones:
        figura.add_trace(
            go.Bar(
                y=datos["periodo"],
                x=datos[columna],
                name=nombre,
                orientation="h",
                marker_color=color,
                customdata=datos[
                    [
                        "tna",
                        "tc_caso_a_inicial",
                        "tc_caso_a_final",
                        "fuente_caso_a_inicial",
                        "fuente_caso_a_final",
                        "rendimiento_pf",
                        "rendimiento_dolar",
                        "valor_final_pf",
                        "valor_final_dolar",
                    ]
                ],
                hovertemplate=(
                    "Período: %{y}<br>"
                    + (
                        "Tipo de cambio inicial: %{customdata[1]:.4f}<br>"
                        "Tipo de cambio final: %{customdata[2]:.4f}<br>"
                        "Fuente inicial: %{customdata[3]}<br>"
                        "Fuente final: %{customdata[4]}<br>"
                        "Rendimiento: %{customdata[6]:.2%}<br>"
                        "Valor final de $1: %{customdata[8]:.4f}"
                        if columna == "valor_final_dolar"
                        else "TNA: %{customdata[0]:.2f}%<br>"
                        "Tasa mensual utilizada: %{customdata[0]:.4f}%<br>"
                        "Rendimiento: %{customdata[5]:.2%}<br>"
                        "Valor final de $1: %{customdata[7]:.4f}"
                    )
                    + "<extra>"
                    + nombre
                    + "</extra>"
                ),
            )
        )

    figura.update_layout(
        barmode="group",
        xaxis_title="Valor final de $1",
        yaxis_title="Período mensual",
        yaxis={
            "categoryorder": "array",
            "categoryarray": periodos,
        },
        hovermode="closest",
        dragmode="zoom",
        height=max(520, len(datos) * 28 + 160),
        margin={"l": 20, "r": 20, "t": 20, "b": 20},
        shapes=[
            {
                "type": "line",
                "x0": 1,
                "x1": 1,
                "y0": 0,
                "y1": 1,
                "yref": "paper",
                "line": {"color": "gray", "dash": "dot", "width": 1},
            }
        ],
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
    st.title("Ahorro e inversión")

    st.subheader("Plazo fijo vs. dólar - Caso A")
    datos = cargar_comparacion()
    minimo = datos["mes_inicial"].min().to_timestamp().date()
    maximo = datos["mes_inicial"].max().to_timestamp().date()
    fecha_inicial = maximo - pd.DateOffset(months=35)

    rango = st.date_input(
        "Período",
        value=(max(minimo, fecha_inicial.date()), maximo),
        min_value=minimo,
        max_value=maximo,
    )
    if isinstance(rango, tuple) and len(rango) == 2:
        desde, hasta = rango
        seleccion = datos[
            (datos["mes_inicial"] >= pd.Period(desde, freq="M"))
            & (datos["mes_inicial"] <= pd.Period(hasta, freq="M"))
        ]
    else:
        seleccion = datos

    _mostrar_grafico(seleccion)

    st.caption(
        "💡 Usá la barra del gráfico para ampliar, desplazar, restablecer "
        "los ejes y mostrar u ocultar alternativas desde la leyenda."
    )

    st.markdown(
        """
        **Plazo fijo vs. dólar**

        El ejercicio compara, para cada mes, el valor al mes siguiente de $1
        colocado en un plazo fijo con el valor equivalente de $1 utilizado para
        comprar dólares según el Caso A. Para el plazo fijo se aproxima la tasa
        mensual como TNA/12. Para el dólar se utiliza la variación entre las
        cotizaciones de cierre mensual. Cada mes se analiza de manera
        independiente, sin reinvertir ni capitalizar los resultados de períodos
        anteriores.
        """
    )