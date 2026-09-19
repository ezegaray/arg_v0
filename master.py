# master.py

from actualizar_datos import (
    actualizar_bcra,
    actualizar_ipc,
    actualizar_tas1,
    actualizar_ambito,
)


BCRA = False
IPC = False
TAS1 = False
AMBITO = False


if BCRA:
    actualizar_bcra()

if IPC:
    actualizar_ipc()

if TAS1:
    actualizar_tas1()

if AMBITO:
    actualizar_ambito()