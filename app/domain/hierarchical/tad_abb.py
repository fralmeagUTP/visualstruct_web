"""Transcripcion Python de `tad_abb.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ABBNodo:
    valor: int
    izquierdo: ABBNodo | None = None
    derecho: ABBNodo | None = None


def abb_insertar(nodo: ABBNodo | None, valor: int) -> ABBNodo:
    if nodo is None:
        return ABBNodo(valor=valor)
    if valor < nodo.valor:
        nodo.izquierdo = abb_insertar(nodo.izquierdo, valor)
    elif valor > nodo.valor:
        nodo.derecho = abb_insertar(nodo.derecho, valor)
    return nodo


def abb_buscar(nodo: ABBNodo | None, valor: int) -> ABBNodo | None:
    actual = nodo
    while actual is not None:
        if valor == actual.valor:
            return actual
        actual = actual.izquierdo if valor < actual.valor else actual.derecho
    return None


def abb_encontrarMinimo(nodo: ABBNodo | None) -> ABBNodo | None:
    actual = nodo
    while actual is not None and actual.izquierdo is not None:
        actual = actual.izquierdo
    return actual


def abb_encontrarMaximo(nodo: ABBNodo | None) -> ABBNodo | None:
    actual = nodo
    while actual is not None and actual.derecho is not None:
        actual = actual.derecho
    return actual


def abb_eliminar(nodo: ABBNodo | None, valor: int) -> ABBNodo | None:
    if nodo is None:
        return None
    if valor < nodo.valor:
        nodo.izquierdo = abb_eliminar(nodo.izquierdo, valor)
        return nodo
    if valor > nodo.valor:
        nodo.derecho = abb_eliminar(nodo.derecho, valor)
        return nodo
    if nodo.izquierdo is None:
        return nodo.derecho
    if nodo.derecho is None:
        return nodo.izquierdo
    sucesor = abb_encontrarMinimo(nodo.derecho)
    nodo.valor = sucesor.valor
    nodo.derecho = abb_eliminar(nodo.derecho, sucesor.valor)
    return nodo


def abb_preorden(nodo: ABBNodo | None) -> None:
    print(" ".join(str(v) for v in _preorden_vals(nodo)))


def abb_inorden(nodo: ABBNodo | None) -> None:
    print(" ".join(str(v) for v in _inorden_vals(nodo)))


def abb_postorden(nodo: ABBNodo | None) -> None:
    print(" ".join(str(v) for v in _postorden_vals(nodo)))


def abb_liberarArbol(nodo: ABBNodo | None) -> None:
    # Python libera por GC; se deja para compatibilidad de firma.
    _ = nodo


def abb_mostrarArbol(nodo: ABBNodo | None, espacio: int) -> None:
    if nodo is None:
        return
    abb_mostrarArbol(nodo.derecho, espacio + 4)
    print(" " * espacio + str(nodo.valor))
    abb_mostrarArbol(nodo.izquierdo, espacio + 4)


def abb_altura(nodo: ABBNodo | None) -> int:
    if nodo is None:
        return 0
    return 1 + max(abb_altura(nodo.izquierdo), abb_altura(nodo.derecho))


def abb_contarNiveles(nodo: ABBNodo | None) -> int:
    return abb_altura(nodo)


def _preorden_vals(nodo: ABBNodo | None) -> list[int]:
    if nodo is None:
        return []
    return [nodo.valor] + _preorden_vals(nodo.izquierdo) + _preorden_vals(nodo.derecho)


def _inorden_vals(nodo: ABBNodo | None) -> list[int]:
    if nodo is None:
        return []
    return _inorden_vals(nodo.izquierdo) + [nodo.valor] + _inorden_vals(nodo.derecho)


def _postorden_vals(nodo: ABBNodo | None) -> list[int]:
    if nodo is None:
        return []
    return _postorden_vals(nodo.izquierdo) + _postorden_vals(nodo.derecho) + [nodo.valor]

