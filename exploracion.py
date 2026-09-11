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
