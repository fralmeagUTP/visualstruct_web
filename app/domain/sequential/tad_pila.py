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


def pila_mostrar(p: ptrPila) -> None:
    actual = p
    valores: list[str] = []
    while actual is not None:
        valores.append(str(actual.nro))
        actual = actual.sgte
    print(" -> ".join(valores) if valores else "(vacia)")


def pila_destruir(p: list[ptrPila]) -> None:
    p[0] = None

