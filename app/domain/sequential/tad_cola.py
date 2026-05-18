"""Transcripcion Python de `tad_cola.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class NodoCola:
    nro: int
    sgte: NodoCola | None = None


@dataclass
class Cola:
    delante: NodoCola | None = None
    atras: NodoCola | None = None


def cola_encolar(q: Cola, valor: int) -> None:
    nuevo = NodoCola(nro=valor)
    if q.atras is None:
        q.delante = nuevo
        q.atras = nuevo
        return
    q.atras.sgte = nuevo
    q.atras = nuevo


def cola_desencolar(q: Cola) -> int:
    if q.delante is None:
        return -1
    valor = q.delante.nro
    q.delante = q.delante.sgte
    if q.delante is None:
        q.atras = None
    return valor


def cola_mostrar(q: Cola) -> None:
    actual = q.delante
    valores: list[str] = []
    while actual is not None:
        valores.append(str(actual.nro))
        actual = actual.sgte
    print(" <- ".join(valores) if valores else "(vacia)")


def cola_vaciar(q: Cola) -> None:
    q.delante = None
    q.atras = None


def cola_frente(q: Cola) -> int:
    return -1 if q.delante is None else q.delante.nro

