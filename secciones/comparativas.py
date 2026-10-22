import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from Indicadores.analisis_horizontes_reales import _rendimientos_reales
from Indicadores.indice_real_base_100 import _construir_indice


_INSTRUMENTOS = {
    "Dólar": ("rend_dolar", "#2ecc71"),
    "Plazo fijo": ("rend_plazo_fijo", "#f39c12"),
    "Merval": ("rend_merval", "#3498db"),
    "S&P 500 en pesos": ("rend_sp500_pesos", "#e74c3c"),
}
_BASE_INICIAL = pd.Period("2016-12", freq="M")


def _periodo_comun_continuo(rendimientos):
    columnas = [columna for columna, _ in _INSTRUMENTOS.values()]
    datos = rendimientos.copy()
    datos["periodo"] = pd.PeriodIndex(datos["periodo"], freq="M")
    datos = datos.set_index("periodo").sort_index()

    if datos.index.has_duplicates:
        raise ValueError("Los rendimientos contienen períodos mensuales duplicados.")

    valores = datos[columnas].to_numpy(dtype="float64")
    validos = pd.Series(np.isfinite(valores).all(axis=1), index=datos.index)
    periodos_validos = list(datos.index[validos])
    if not periodos_validos:
        raise ValueError("No hay un período válido común para los cuatro instrumentos.")

    tramos = []
    inicio = anterior = periodos_validos[0]
    for periodo in periodos_validos[1:]:
        if periodo != anterior + 1:
            tramos.append((inicio, anterior))
            inicio = periodo
        anterior = periodo
    tramos.append((inicio, anterior))
    inicio, fin = max(tramos, key=lambda tramo: tramo[1].ordinal - tramo[0].ordinal)
    return datos.loc[inicio:fin, columnas]


def _construir_series_reales(rendimientos, periodo_base):
    comunes = _periodo_comun_continuo(rendimientos)
    periodo_base = pd.Period(periodo_base, freq="M")
    if periodo_base not in comunes.index:
        raise ValueError("La fecha base debe pertenecer al período común disponible.")

    factores = 1 + comunes
    if not np.isfinite(factores.to_numpy()).all() or (factores <= 0).any().any():
        raise ValueError("Hay rendimientos que no permiten construir índices positivos.")

    indices = {}
    for nombre, (columna, _) in _INSTRUMENTOS.items():
        nivel_inicial = _construir_indice(comunes[columna], comunes.index[0])
        base = nivel_inicial.loc[periodo_base]
        if not np.isfinite(base) or base <= 0:
            raise ValueError(f"No se puede rebasing {nombre} en {periodo_base}.")
        indice = nivel_inicial / base * 100
        indice.loc[periodo_base] = 100.0
        indices[nombre] = indice

    return pd.DataFrame(indices)


def _construir_grafico_comparativo(series, periodo_base):
    figura = go.Figure()
    for nombre, (_, color) in _INSTRUMENTOS.items():
        serie = series[nombre]
        figura.add_trace(
            go.Scatter(
                x=serie.index.to_timestamp(),
                y=serie,
                name=nombre,
                mode="lines",
                line={"color": color, "width": 2},
                hovertemplate="%{x|%Y-%m}<br>Índice: %{y:.2f}<extra></extra>",
            )
        )

    fecha_base = periodo_base.to_timestamp()
    figura.add_hline(
        y=100,
        line={"color": "rgba(230, 230, 230, 0.4)", "dash": "dash", "width": 1},
    )
    figura.add_vline(
        x=fecha_base,
        line={"color": "rgba(230, 230, 230, 0.65)", "dash": "dot", "width": 1},
        annotation_text="Fecha base",
        annotation_position="top",
    )
    figura.update_layout(
        title="Evolución real comparada con base móvil",
        xaxis_title="Año",
        yaxis_title="Índice real (fecha base = 100)",
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font={"color": "#f5f5f5"},
        hovermode="x unified",
        dragmode="zoom",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02},
        margin={"t": 95, "b": 55, "l": 65, "r": 30},
    )
    figura.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        color="#f5f5f5",
    )
    figura.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        color="#f5f5f5",
    )
    return figura


def mostrar():
    st.title("Comparativas")
    st.write(
        """
Comparar las cuatro alternativas desde una misma base permite observar algo
que los gráficos individuales ocultan: pequeñas diferencias sostenidas
durante muchos años pueden producir trayectorias de capital profundamente
distintas. Al mismo tiempo, elegir una única fecha inicial puede condicionar
fuertemente esa comparación, porque cada instrumento atravesó ciclos muy
diferentes.

Por eso, el gráfico permite modificar la fecha en la que todas las
alternativas toman valor 100. Mover la base no altera los rendimientos de
cada instrumento, pero sí permite formular distintas preguntas: qué habría
ocurrido si la comparación hubiera comenzado antes de una crisis, después de
ella o durante un período de relativa estabilidad. La herramienta hace
visible hasta qué punto las conclusiones sobre desempeño acumulado dependen
del momento desde el cual se comienza a medir.

Más que buscar un “ganador” único para todo el período, la comparación
permite observar que las alternativas presentan perfiles históricos
diferentes. Algunas mostraron menores oscilaciones pero pérdidas persistentes
frente a la inflación; otras combinaron una volatilidad mucho mayor con
períodos prolongados de crecimiento real. El resultado final de una
inversión dependió tanto del instrumento elegido como del horizonte y del
momento de entrada.
"""
    )

    rendimientos, _ = _rendimientos_reales()
    comunes = _periodo_comun_continuo(rendimientos)
    periodos = list(comunes.index)
    periodo_inicial = (
        _BASE_INICIAL
        if _BASE_INICIAL in comunes.index
        else periodos[len(periodos) // 2]
    )
    fechas = [periodo.to_timestamp() for periodo in periodos]
    fecha_base = st.select_slider(
        "Fecha base",
        options=fechas,
        value=periodo_inicial.to_timestamp(),
        format_func=lambda fecha: fecha.strftime("%m/%Y"),
        key="comparativas_fecha_base",
        help="Elegí un mes disponible en el período común de los cuatro instrumentos.",
    )
    periodo_base = fecha_base.to_period("M")

    st.caption(
        "Período común disponible: "
        f"{periodos[0].to_timestamp():%m/%Y}–"
        f"{periodos[-1].to_timestamp():%m/%Y}. "
        f"En {periodo_base.to_timestamp():%m/%Y}, todas las series se fijan "
        "en 100; los valores anteriores muestran la evolución relativa "
        "previa a esa fecha."
    )
    series = _construir_series_reales(rendimientos, periodo_base)
    st.plotly_chart(
        _construir_grafico_comparativo(series, periodo_base),
        width="stretch",
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )
