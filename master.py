# master.py

from actualizar_datos import actualizar_bcra, actualizar_ipc


BCRA = False
IPC = True


if BCRA:
    actualizar_bcra()

if IPC:
    actualizar_ipc()