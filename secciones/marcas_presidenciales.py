from datetime import date, datetime

import plotly.graph_objects as go


ADMINISTRACIONES = (
    (date(1942, 6, 30), "Castillo"),
    (date(1943, 6, 7), "Ramírez"),
    (date(1944, 2, 25), "Farrell"),
    (date(1946, 6, 4), "Perón"),
    (date(1955, 9, 23), "Lonardi"),
    (date(1955, 11, 13), "Aramburu"),
    (date(1958, 5, 1), "Frondizi"),
    (date(1962, 3, 29), "Guido"),
    (date(1963, 10, 12), "Illia"),
    (date(1966, 6, 29), "Onganía"),
    (date(1970, 6, 18), "Levingston"),
    (date(1971, 3, 26), "Lanusse"),
    (date(1973, 5, 25), "Cámpora"),
    (date(1973, 7, 13), "Lastiri"),
    (date(1973, 10, 12), "Perón"),
    (date(1974, 7, 1), "M. E. Martínez de Perón"),
    (date(1976, 3, 29), "Videla"),
    (date(1981, 3, 29), "Viola"),
    (date(1981, 12, 22), "Galtieri"),
    (date(1982, 7, 1), "Bignone"),
    (date(1983, 12, 10), "Alfonsín"),
    (date(1989, 7, 8), "Menem"),
    (date(1999, 12, 10), "De la Rúa"),
    (date(2002, 1, 2), "Duhalde"),
    (date(2003, 5, 25), "N. Kirchner"),
    (date(2007, 12, 10), "C. Fernández"),
    (date(2015, 12, 10), "Macri"),
    (date(2019, 12, 10), "A. Fernández"),
    (date(2023, 12, 10), "Milei"),
)

# En 1991 los comicios legislativos se escalonaron en cuatro jornadas;
# se usa el 27 de octubre como fecha nacional representativa única.
ELECCIONES = (
    date(1940, 3, 3),
    date(1942, 3, 1),
    date(1948, 3, 7),
    date(1951, 11, 11),  # Reelección de Juan Domingo Perón.
    date(1954, 4, 25),
    date(1960, 3, 27),
    date(1962, 3, 18),
    date(1965, 3, 14),
    date(1985, 11, 3),
    date(1987, 9, 6),
    date(1991, 10, 27),
    date(1993, 10, 3),
    date(1995, 5, 14),  # Reelección de Carlos Menem.
    date(1997, 10, 26),
    date(2001, 10, 14),
    date(2005, 10, 23),
    date(2009, 6, 28),
    date(2011, 10, 23),  # Reelección de Cristina Fernández de Kirchner.
    date(2013, 10, 27),
    date(2017, 10, 22),
    date(2021, 11, 14),
    date(2025, 10, 26),
)

# Compatibilidad con gráficos exploratorios que aún importan este nombre.
PRESIDENCIAS = ADMINISTRACIONES


def _as_datetime(value):
    if isinstance(value, datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(
            tzinfo=None
        )
    except (TypeError, ValueError):
        return None


def _visible_range(fig):
    x_range = fig.layout.xaxis.range
    if x_range and len(x_range) == 2:
        start, end = (_as_datetime(value) for value in x_range)
        if start is not None and end is not None:
            return min(start, end), max(start, end)

    fechas = []
    for trace in fig.data:
        if trace.x is not None:
            fechas.extend(
                fecha
                for value in trace.x
                if (fecha := _as_datetime(value)) is not None
            )
    if not fechas:
        return None
    return min(fechas), max(fechas)


def agregar_marcas_politicas(fig):
    """Agrega cambios de administración y elecciones visibles al gráfico."""
    rango = _visible_range(fig)
    if rango is None:
        return fig

    inicio, fin = rango
    duracion = (fin - inicio).total_seconds()
    if duracion <= 0:
        return fig

    administraciones_visibles = [
        (fecha, etiqueta)
        for fecha, etiqueta in ADMINISTRACIONES
        if inicio <= datetime.combine(fecha, datetime.min.time()) <= fin
    ]
    elecciones_visibles = [
        fecha
        for fecha in ELECCIONES
        if inicio <= datetime.combine(fecha, datetime.min.time()) <= fin
    ]

    for fecha in elecciones_visibles:
        fig.add_vline(
            x=fecha.isoformat(),
            line={"color": "rgba(90, 98, 105, 0.22)", "dash": "dash", "width": 0.8},
            layer="below",
        )

    if not administraciones_visibles:
        return fig

    ancho_figura = fig.layout.width or 1000
    margenes = fig.layout.margin
    ancho_grafico = max(
        320,
        ancho_figura - (margenes.l or 0) - (margenes.r or 0),
    )
    carriles = []
    marcas_con_carril = []

    for fecha, etiqueta in administraciones_visibles:
        posicion = (
            datetime.combine(fecha, datetime.min.time()) - inicio
        ).total_seconds() / duracion * ancho_grafico
        ancho_etiqueta = len(etiqueta) * 7 + 14
        izquierda = posicion - ancho_etiqueta / 2
        derecha = posicion + ancho_etiqueta / 2

        for indice, ultimo_borde in enumerate(carriles):
            if izquierda > ultimo_borde + 6:
                carriles[indice] = derecha
                break
        else:
            indice = len(carriles)
            carriles.append(derecha)

        marcas_con_carril.append((fecha, etiqueta, indice))

    margen_superior = 44 + len(carriles) * 22
    fig.update_layout(
        margin={
            "t": max(fig.layout.margin.t or 0, margen_superior),
        }
    )

    for fecha, etiqueta, carril in marcas_con_carril:
        fecha_iso = fecha.isoformat()
        fig.add_vline(
            x=fecha_iso,
            line={"color": "rgba(90, 98, 105, 0.45)", "dash": "dot", "width": 1},
            layer="below",
        )
        fig.add_annotation(
            x=fecha_iso,
            y=1.02 + carril * 0.08,
            xref="x",
            yref="paper",
            text=etiqueta,
            showarrow=False,
            xanchor="center",
            yanchor="bottom",
            font={"size": 10, "color": "#5a6269"},
            bgcolor="rgba(255, 255, 255, 0.78)",
            borderpad=2,
        )

    return fig


def agregar_marcas_presidenciales(fig):
    """Alias de compatibilidad: agrega todas las marcas políticas."""
    return agregar_marcas_politicas(fig)
