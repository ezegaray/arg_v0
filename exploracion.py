# %%
from Fuentes.indec_ipc import cargar_ipc

ipc = cargar_ipc()

# %%
ipc.head()

# %%
ipc.tail()

# %%
ipc.dtypes
# %%



# %%
from Fuentes.inflacion_historica import cargar_inflacion_historica

inflacion_historica = cargar_inflacion_historica()

inflacion_historica.head()

inflacion_historica.tail()


# %%
from Fuentes.inflacion import cargar_inflacion

inflacion = cargar_inflacion()


# %%
inflacion[
    (inflacion["fecha"] >= "2016-09-01") &
    (inflacion["fecha"] <= "2017-03-01")
]


# %%


# %%
1 + 1



# %%
from Fuentes.bcra import cargar_bcra

bcra = cargar_bcra()

bcra.head()




# %%
from Indicadores.poder_compra_usd import cargar_poder_compra_usd

poder_compra_usd = cargar_poder_compra_usd()

poder_compra_usd.head()


# %%
poder_compra_usd[
    (poder_compra_usd["fecha"] >= "2016-10-01")
    & (poder_compra_usd["fecha"] <= "2017-02-01")
]
# %%


# %%
<from pathlib import Path

import pandas as pd


archivo_tas1 = Path("data/raw/tas1_ser.txt")
columnas_tas1 = ["codigo", "fecha", "valor"]


def limpiar_tas1(bloque):
    bloque = bloque.copy()

    bloque = bloque[
        bloque["codigo"].notna()
        & bloque["fecha"].notna()
        & bloque["valor"].notna()
        & (bloque["codigo"] != "\x1a")
    ]

    bloque["fecha"] = pd.to_datetime(
        bloque["fecha"],
        format="%d/%m/%Y",
        errors="coerce",
    )
    bloque["valor"] = pd.to_numeric(
        bloque["valor"],
        errors="coerce",
    )

    return bloque.dropna(subset=["fecha", "valor"])


def cargar_tas1(codigo=None, chunksize=200_000):
    """Carga todo o un código específico sin leer innecesariamente el archivo completo."""
    bloques = []

    lector = pd.read_csv(
        archivo_tas1,
        sep=";",
        header=None,
        names=columnas_tas1,
        dtype={"codigo": "string", "fecha": "string"},
        chunksize=chunksize,
    )

    for bloque in lector:
        if codigo is not None:
            bloque = bloque[bloque["codigo"] == str(codigo)]

        bloque = limpiar_tas1(bloque)
        if not bloque.empty:
            bloques.append(bloque)

    if not bloques:
        return pd.DataFrame(columns=columnas_tas1).astype(
            {"codigo": "string", "fecha": "datetime64[ns]", "valor": "float64"}
        )

    return pd.concat(bloques, ignore_index=True)


# Ejemplos básicos de inspección.
tas1 = cargar_tas1(codigo="1211")
tas1.head()
tas1.tail()
tas1.columns
tas1.dtypes
tas1.shape


# Códigos únicos sin concatenar todas las filas del archivo en memoria.
codigos_tas1 = set()
for bloque in pd.read_csv(
    archivo_tas1,
    sep=";",
    header=None,
    names=columnas_tas1,
    dtype={"codigo": "string"},
    usecols=["codigo"],
    chunksize=200_000,
):
    codigos_tas1.update(
        bloque.loc[
            bloque["codigo"].notna() & (bloque["codigo"] != "\x1a"),
            "codigo",
        ].unique()
    )

sorted(codigos_tas1)


# Cambiá el código para inspeccionar otra serie del TXT.
codigo_a_explorar = "1211"
tas1_codigo = cargar_tas1(codigo=codigo_a_explorar)
tas1_codigo.head()
# %%
