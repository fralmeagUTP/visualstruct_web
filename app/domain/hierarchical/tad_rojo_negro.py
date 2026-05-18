"""Transcripcion Python de `tad_rojo_negro.h`."""

from __future__ import annotations

from dataclasses import dataclass

ROJO = "r"
NEGRO = "n"


@dataclass
class nodoRBT:
    nro: int
    rbt_color: str = ROJO
    padre: nodoRBT | None = None
    izq: nodoRBT | None = None
    der: nodoRBT | None = None


RBT = nodoRBT | None


def rbt_abuelo(n: RBT) -> RBT:
    if n is None or n.padre is None:
        return None
    return n.padre.padre


def rbt_tio(n: RBT) -> RBT:
    abuelo = rbt_abuelo(n)
    if abuelo is None or n is None or n.padre is None:
        return None
    return abuelo.der if n.padre is abuelo.izq else abuelo.izq


def rbt_rotar_dcha(r: list[RBT], nodo: RBT) -> None:
    if nodo is None or nodo.izq is None:
        return
    pivote = nodo.izq
    nodo.izq = pivote.der
    if pivote.der is not None:
        pivote.der.padre = nodo
    pivote.padre = nodo.padre
    if nodo.padre is None:
        r[0] = pivote
    elif nodo is nodo.padre.der:
        nodo.padre.der = pivote
    else:
        nodo.padre.izq = pivote
    pivote.der = nodo
    nodo.padre = pivote


def rbt_rotar_izda(r: list[RBT], nodo: RBT) -> None:
    if nodo is None or nodo.der is None:
        return
    pivote = nodo.der
    nodo.der = pivote.izq
    if pivote.izq is not None:
        pivote.izq.padre = nodo
    pivote.padre = nodo.padre
    if nodo.padre is None:
        r[0] = pivote
    elif nodo is nodo.padre.izq:
        nodo.padre.izq = pivote
    else:
        nodo.padre.der = pivote
    pivote.izq = nodo
    nodo.padre = pivote


def rbt_insercion_caso1(n: RBT, arbol: list[RBT]) -> None:
    if n is None:
        return
    if n.padre is None:
        n.rbt_color = NEGRO
        arbol[0] = n
    else:
        rbt_insercion_caso2(n, arbol)


def rbt_insercion_caso2(n: RBT, arbol: list[RBT]) -> None:
    if n is None or n.padre is None:
        return
    if n.padre.rbt_color == NEGRO:
        return
    rbt_insercion_caso3(n, arbol)


def rbt_insercion_caso3(n: RBT, arbol: list[RBT]) -> None:
    tio = rbt_tio(n)
    if n is None or n.padre is None:
        return
    if tio is not None and tio.rbt_color == ROJO:
        n.padre.rbt_color = NEGRO
        tio.rbt_color = NEGRO
        abuelo = rbt_abuelo(n)
        if abuelo is not None:
            abuelo.rbt_color = ROJO
            rbt_insercion_caso1(abuelo, arbol)
    else:
        rbt_insercion_caso4(n, arbol)


def rbt_insercion_caso4(n: RBT, arbol: list[RBT]) -> None:
    if n is None or n.padre is None:
        return
    abuelo = rbt_abuelo(n)
    if abuelo is None:
        return
    if n is n.padre.der and n.padre is abuelo.izq:
        rbt_rotar_izda(arbol, n.padre)
        n = n.izq
    elif n is n.padre.izq and n.padre is abuelo.der:
        rbt_rotar_dcha(arbol, n.padre)
        n = n.der
    rbt_insercion_caso5(n, arbol)


def rbt_insercion_caso5(n: RBT, arbol: list[RBT]) -> None:
    if n is None or n.padre is None:
        return
    abuelo = rbt_abuelo(n)
    if abuelo is None:
        return
    n.padre.rbt_color = NEGRO
    abuelo.rbt_color = ROJO
    if n is n.padre.izq and n.padre is abuelo.izq:
        rbt_rotar_dcha(arbol, abuelo)
    else:
        rbt_rotar_izda(arbol, abuelo)


def rbt_color(c: int) -> None:
    _ = c


def rbt_buscar(nodo: RBT, dato: int) -> RBT:
    actual = nodo
    while actual is not None:
        if dato == actual.nro:
            return actual
        actual = actual.izq if dato < actual.nro else actual.der
    return None


def rbt_verArbol(arbol: RBT, n: int) -> None:
    if arbol is None:
        return
    rbt_verArbol(arbol.der, n + 4)
    print(" " * n + f"{arbol.nro}({arbol.rbt_color})")
    rbt_verArbol(arbol.izq, n + 4)


def rbt_insertar(arbol: list[RBT], dato: int) -> None:
    padre: RBT = None
    actual = arbol[0]
    while actual is not None:
        padre = actual
        if dato < actual.nro:
            actual = actual.izq
        elif dato > actual.nro:
            actual = actual.der
        else:
            return
    nuevo = nodoRBT(nro=dato, rbt_color=ROJO, padre=padre)
    if padre is None:
        arbol[0] = nuevo
    elif dato < padre.nro:
        padre.izq = nuevo
    else:
        padre.der = nuevo
    rbt_insercion_caso1(nuevo, arbol)
    if arbol[0] is not None:
        arbol[0].rbt_color = NEGRO


def rbt_eliminar(arbol: list[RBT], key: int) -> None:
    nodo = rbt_buscar(arbol[0], key)
    if nodo is None:
        return
    if nodo.izq is not None and nodo.der is not None:
        sucesor = _minimo(nodo.der)
        nodo.nro = sucesor.nro
        nodo = sucesor
    hijo = nodo.izq if nodo.izq is not None else nodo.der
    _trasplantar(arbol, nodo, hijo)
    if arbol[0] is not None:
        arbol[0].rbt_color = NEGRO


def rbt_liberar(arbol: RBT) -> None:
    _ = arbol


def _minimo(nodo: RBT) -> RBT:
    actual = nodo
    while actual is not None and actual.izq is not None:
        actual = actual.izq
    return actual


def _trasplantar(arbol: list[RBT], u: RBT, v: RBT) -> None:
    if u is None:
        return
    if u.padre is None:
        arbol[0] = v
    elif u is u.padre.izq:
        u.padre.izq = v
    else:
        u.padre.der = v
    if v is not None:
        v.padre = u.padre

