"""Transcripcion Python de `tad_pila.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NodoPila:
    nro: int
    sgte: NodoPila | None = None


ptrPila = NodoPila | None


def pila_apilar(p: list[ptrPila], valor: int) -> None:
    p[0] = NodoPila(nro=valor, sgte=p[0])


def pila_desapilar(p: list[ptrPila]) -> int:
    if not p or p[0] is None:
        return -1
    valor = p[0].nro
    p[0] = p[0].sgte
    return valor


def pila_cima(p: ptrPila) -> int:
    """Return the borrowed top value, or the C sentinel -1 for NULL."""
    return -1 if p is None else p.nro


def pila_mostrar(p: ptrPila) -> None:
    actual = p
    if actual is None:
        print("Pila vacia.")
        return
    while actual is not None:
        print(f"\t{actual.nro}")
        actual = actual.sgte

def pila_destruir(p: list[ptrPila]) -> None:
    p[0] = None

