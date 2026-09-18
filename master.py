# master.py

from actualizar_datos import (
    actualizar_bcra,
    actualizar_ipc,
    actualizar_tas1,
)


BCRA = False
IPC = False
TAS1 = False


if BCRA:
    actualizar_bcra()

if IPC:
    actualizar_ipc()

if TAS1:
    actualizar_tas1()