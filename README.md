# Actualización de datos

Las fuentes disponibles se actualizan desde `master.py`. Ejecutado sin
argumentos, descarga y procesa todas las fuentes:

```bash
uv run python master.py
```

Para actualizar solo algunas, indicar una o más fuentes con `--fuentes`:

```bash
uv run python master.py --fuentes bcra ipc
uv run python master.py --fuentes dolar_blue dolar_ccl bolsas
```

Fuentes admitidas:

- `bcra`: tipo de cambio oficial.
- `ipc`: serie del IPC del INDEC.
- `tasas`: tasas de plazo fijo del BCRA.
- `dolar_blue`: dólar blue de Ámbito.
- `dolar_ccl`: dólar CCL de Ámbito.
- `bolsas`: S&P 500 y Merval de Yahoo Finance.

Si una fuente falla, se informa el error y se intenta actualizar el resto. El
proceso termina con código distinto de cero para indicar que hubo fallas.
También se puede ejecutar `actualizar_datos.py` con las mismas opciones.

La serie histórica de inflación de `data/raw/Argentina_inflation.csv` no cuenta
con un proceso de descarga en el proyecto y no se actualiza mediante estos
comandos.

## Aplicación

Instalá las dependencias con `uv sync` y ejecutá la aplicación:

```bash
uv run streamlit run streamlit_app.py
```
