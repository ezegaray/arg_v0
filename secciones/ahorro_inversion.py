import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from Indicadores.analisis_horizontes import _tabla_horizonte
from Indicadores.analisis_horizontes_reales import _rendimientos_reales
from Indicadores.indice_real_base_100 import _construir_indice
from secciones.marcas_presidenciales import agregar_marcas_politicas


_PERIODO_INICIO_EJE = pd.Period("1996-01", freq="M")
_OPCIONES_HORIZONTE = {
    "Mensual anualizado": "Rendimiento real mensual anualizado (TNA equivalente)",
    "12 meses": "Rendimiento real móvil a 12 meses",
    "3 años": "CAGR real móvil a 3 años",
    "5 años": "CAGR real móvil a 5 años",
    "10 años": "CAGR real móvil a 10 años",
}
_HORIZONTES_INICIALES = {
    "Mensual anualizado": False,
    "12 meses": True,
    "3 años": True,
    "5 años": False,
    "10 años": True,
}
_INSTRUMENTOS = {
    "Plazo fijo": "rend_plazo_fijo",
    "Dólar": "rend_dolar",
    "Merval": "rend_merval",
    "S&P 500 en pesos": "rend_sp500_pesos",
}
_DESCRIPCIONES_INSTRUMENTOS = {
    "Plazo fijo": """
El índice de capital real muestra qué habría ocurrido con una inversión
inicial renovada mes a mes en plazo fijo, reinvirtiendo el capital y los
intereses y descontando posteriormente la inflación. Durante los primeros
años del período esta estrategia aumentó el poder adquisitivo del ahorro.
Hacia comienzos de los 2000 la tendencia comenzó a revertirse y, desde
entonces, el capital real atravesó un deterioro prolongado durante buena
parte de las dos décadas siguientes.

Los rendimientos móviles refuerzan esa lectura. Solamente el 32% de las
ventanas de doce meses terminó con rendimiento real positivo. Los resultados
fueron todavía menos favorables al extender el horizonte: alrededor del 23%
de las ventanas de tres y cinco años y apenas el 18% de las de diez años
fueron positivas. Las medianas anualizadas fueron de aproximadamente -5,2%
a tres años, -5,3% a cinco y -5,5% a diez años.

Esto no significa que el plazo fijo haya ofrecido siempre rendimientos reales
negativos. Hubo períodos puntuales con resultados de corto plazo elevados,
que quedan ocultos al observar solamente la evolución acumulada. Sin embargo,
identificarlos retrospectivamente no implica que hubieran sido previsibles.
La experiencia histórica muestra, sobre todo, una diferencia importante
entre esas oportunidades puntuales y el débil desempeño del plazo fijo como
estrategia pasiva de preservación del poder adquisitivo durante gran parte
del período analizado.
""",
    "Dólar": """
La serie busca representar la evolución del poder adquisitivo en Argentina
de una tenencia de dólares. Para aproximar la experiencia de un ahorrista se
utiliza una cotización de referencia que combina el dólar oficial y el blue
según las restricciones de acceso vigentes en cada período. Por eso no debe
interpretarse como una medida convencional del tipo de cambio real, sino
como el valor de una tenencia de dólares ajustado por la inflación argentina.

La serie muestra con claridad algunos de los grandes episodios cambiarios de
las últimas décadas. Durante la convertibilidad, la combinación de un tipo
de cambio nominal fijo y baja inflación produjo una evolución real
relativamente estable. La salida de ese régimen generó un fuerte incremento
del poder adquisitivo del dólar, seguido por una erosión progresiva a medida
que los precios internos reaccionaron. Episodios posteriores muestran
nuevamente saltos rápidos asociados a movimientos cambiarios, seguidos en
muchos casos por períodos en los que la inflación reduce parte de esa
ganancia real.

Los rendimientos por horizonte muestran una característica menos evidente:
tener dólares no garantizó preservar poder adquisitivo. A doce meses, el 65%
de las ventanas terminó con rendimiento real negativo y la mediana fue
cercana a -6%, pese a que la media fue positiva. Esa diferencia refleja una
distribución fuertemente asimétrica: algunos movimientos cambiarios
produjeron ganancias extraordinarias y elevaron el promedio, aunque fueron
más frecuentes los períodos de pérdida frente a la inflación. En horizontes
más largos los resultados se vuelven más equilibrados, pero tampoco aparece
una garantía de preservación: a diez años, el 56% de las ventanas analizadas
terminó con rendimiento real negativo.
""",
    "Merval": """
El Merval presenta una trayectoria real considerablemente más volátil que
las alternativas de ahorro tradicionales. Desde el máximo relativo de 1997
atravesó una fuerte caída hasta comienzos de los 2000, seguida por sucesivos
ciclos de recuperación y retroceso. Desde 2022 se observa uno de los
procesos de crecimiento más pronunciados de toda la serie, aunque acompañado
recientemente por oscilaciones también muy importantes.

La elevada variabilidad aparece con claridad en los horizontes cortos. Sin
embargo, al extender la duración de las ventanas aumenta el predominio de
resultados positivos, especialmente en el horizonte más largo.
Aproximadamente el 58% de las ventanas de cinco años y el 77% de las de diez
años terminaron con rendimientos reales positivos. A diez años, la mediana
del rendimiento real anualizado fue cercana al 2,8%.

Esto no implica que extender el horizonte elimine el riesgo ni que todos
los períodos largos hayan resultado favorables. El momento de entrada
continúa siendo relevante y las ventanas móviles de largo plazo se
superponen fuertemente entre sí. El gráfico permite observar, sin embargo,
una diferencia respecto de alternativas como el plazo fijo: la fuerte
variabilidad de corto plazo convivió históricamente con un predominio mucho
mayor de resultados positivos en las inversiones sostenidas durante diez
años.
""",
    "S&P 500 en pesos": """
El rendimiento del S&P 500 para un inversor argentino combina tres
movimientos: la evolución del índice estadounidense en dólares, el tipo de
cambio peso-dólar y la inflación local. Por ese motivo, la serie en pesos
reales puede comportarse de manera muy diferente del índice observado
directamente en Estados Unidos.

El episodio de 2002 permite verlo con claridad. Mientras el S&P 500 caía en
dólares, la fuerte depreciación del peso produjo inicialmente un aumento
considerable de su valor expresado en moneda local. La posterior aceleración
de la inflación erosionó parte de ese incremento. La inversión funciona así
simultáneamente como exposición al mercado accionario estadounidense y a la
evolución relativa entre el peso y el dólar.

En la muestra analizada predominan los rendimientos reales positivos en
todos los horizontes superiores al mensual: aproximadamente el 58% de las
ventanas de doce meses, el 62% de las de tres años, el 70% de las de cinco y
el 65% de las de diez años fueron positivas. Las medianas reales anualizadas
alcanzaron aproximadamente 5,3% a tres años, 10,6% a cinco y 4,6% a diez
años. El resultado siguió dependiendo fuertemente del momento de entrada,
pero históricamente los períodos positivos fueron más frecuentes que los
negativos en los horizontes considerados.
""",
}


def _construir_grafico_real(rendimientos, instrumento, horizontes_seleccionados):
    rendimientos = rendimientos.copy()
    rendimientos["periodo"] = pd.PeriodIndex(rendimientos["periodo"], freq="M")
    rendimiento = (
        rendimientos.set_index("periodo")[instrumento]
        .sort_index()
        .astype("float64")
    )

    rendimiento_visible = rendimiento.loc[
        rendimiento.index >= _PERIODO_INICIO_EJE
    ]
    periodo_base = rendimiento_visible.first_valid_index()
    if periodo_base is None:
        raise ValueError(
            f"No hay rendimientos reales de {instrumento} desde "
            f"{_PERIODO_INICIO_EJE}."
        )
    indice = _construir_indice(rendimiento, periodo_base).dropna()
    horizontes = {
        _OPCIONES_HORIZONTE["Mensual anualizado"]: rendimiento * 12,
        "Rendimiento real móvil a 12 meses": _tabla_horizonte(
            rendimientos, 12
        ).set_index("periodo")[instrumento],
        "CAGR real móvil a 3 años": _tabla_horizonte(
            rendimientos, 36, 3
        ).set_index("periodo")[f"cagr_{instrumento.removeprefix('rend_')}"],
        "CAGR real móvil a 5 años": _tabla_horizonte(
            rendimientos, 60, 5
        ).set_index("periodo")[f"cagr_{instrumento.removeprefix('rend_')}"],
        "CAGR real móvil a 10 años": _tabla_horizonte(
            rendimientos, 120, 10
        ).set_index("periodo")[f"cagr_{instrumento.removeprefix('rend_')}"],
    }
    horizontes = {
        nombre: serie.set_axis(pd.PeriodIndex(serie.index, freq="M")).dropna()
        for nombre, serie in horizontes.items()
    }

    indice = indice.loc[indice.index >= _PERIODO_INICIO_EJE]
    horizontes = {
        nombre: serie.loc[serie.index >= _PERIODO_INICIO_EJE]
        for nombre, serie in horizontes.items()
    }
    periodo_fin = max(
        [indice.index.max(), *(serie.index.max() for serie in horizontes.values())]
    )
    fecha_fin = periodo_fin.end_time

    figura = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.48, 0.52],
        subplot_titles=(
            f"Capital real — base: {periodo_base.to_timestamp():%m/%Y} = 100 "
            "(primer período visible)",
            "Rendimiento real según horizonte",
        ),
    )
    figura.add_trace(
        go.Scatter(
            x=indice.index.to_timestamp(),
            y=indice,
            name=f"Capital real — {_nombre_instrumento(instrumento)}",
            mode="lines",
            line={"color": "#a8e6ff", "width": 2},
            hovertemplate="%{x|%Y-%m}<br>Índice: %{y:.2f}<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figura.add_hline(
        y=100,
        line={"color": "rgba(230, 230, 230, 0.4)", "dash": "dash", "width": 1},
        row=1,
        col=1,
    )

    estilos = {
        _OPCIONES_HORIZONTE["Mensual anualizado"]: ("#ef5350", "solid", 1.2),
        _OPCIONES_HORIZONTE["12 meses"]: ("#b3ecff", "solid", 1.7),
        _OPCIONES_HORIZONTE["3 años"]: ("#48b4df", "solid", 1.7),
        _OPCIONES_HORIZONTE["5 años"]: ("#207dad", "solid", 1.7),
        _OPCIONES_HORIZONTE["10 años"]: ("#1a6b90", "dot", 2),
    }
    for nombre_opcion in _OPCIONES_HORIZONTE:
        nombre_serie = _OPCIONES_HORIZONTE[nombre_opcion]
        if nombre_opcion not in horizontes_seleccionados:
            continue
        serie = horizontes[nombre_serie]
        color, dash, ancho = estilos[nombre_serie]
        figura.add_trace(
            go.Scatter(
                x=serie.index.to_timestamp(),
                y=serie * 100,
                name=nombre_serie,
                mode="lines",
                line={"color": color, "dash": dash, "width": ancho},
                hovertemplate="%{x|%Y-%m}<br>Tasa: %{y:.2f}%<extra></extra>",
            ),
            row=2,
            col=1,
        )
    figura.add_hline(
        y=0,
        line={"color": "rgba(230, 230, 230, 0.75)", "width": 1},
        row=2,
        col=1,
    )
    figura.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        zerolinecolor="rgba(255, 255, 255, 0.25)",
        color="#f5f5f5",
    )
    figura.update_xaxes(
        range=[_PERIODO_INICIO_EJE.start_time, fecha_fin],
        title_text="Año",
        dtick="M24",
        tickformat="%Y",
        row=2,
        col=1,
    )
    figura.update_yaxes(
        title_text="Índice real",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        zerolinecolor="rgba(255, 255, 255, 0.25)",
        color="#f5f5f5",
        row=1,
        col=1,
    )
    figura.update_yaxes(
        title_text="Tasa anual (%)",
        showgrid=True,
        gridcolor="rgba(255, 255, 255, 0.12)",
        zerolinecolor="rgba(255, 255, 255, 0.25)",
        color="#f5f5f5",
        row=2,
        col=1,
    )
    figura.update_layout(
        height=780,
        template="plotly_dark",
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font={"color": "#f5f5f5"},
        hovermode="x unified",
        dragmode="zoom",
        legend={"orientation": "h", "yanchor": "top", "y": -0.14},
        margin={"t": 90, "b": 110, "l": 65, "r": 30},
    )
    agregar_marcas_politicas(figura)
    return figura


def _nombre_instrumento(instrumento):
    return next(
        nombre
        for nombre, columna in _INSTRUMENTOS.items()
        if columna == instrumento
    )


def mostrar():
    st.title("Ahorro e inversión")

    st.subheader("Rendimiento real por instrumento")
    instrumento = st.selectbox(
        "Instrumento",
        options=list(_INSTRUMENTOS),
        key="ahorro_inversion_instrumento",
    )
    columna_rendimiento = _INSTRUMENTOS[instrumento]
    st.markdown(_DESCRIPCIONES_INSTRUMENTOS[instrumento])
    st.caption("El índice de capital parte de 100 en el primer período visible.")
    columnas_controles = st.columns(len(_OPCIONES_HORIZONTE))
    horizontes_seleccionados = [
        opcion
        for columna, opcion in zip(columnas_controles, _OPCIONES_HORIZONTE)
        if columna.checkbox(
            opcion,
            value=_HORIZONTES_INICIALES[opcion],
            key=f"horizonte_{columna_rendimiento}_{opcion}",
        )
    ]
    rendimientos, _ = _rendimientos_reales()
    st.plotly_chart(
        _construir_grafico_real(
            rendimientos,
            columna_rendimiento,
            horizontes_seleccionados,
        ),
        use_container_width=True,
        config={
            "displaylogo": False,
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )