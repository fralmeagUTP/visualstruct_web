"""Transcripcion Python de `tad_avl.h`."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class nodoAVL:
    nro: int
    FE: int = 0
    der: nodoAVL | None = None
    izq: nodoAVL | None = None
    padre: nodoAVL | None = None


AVL = nodoAVL | None


def avl_verArbol(arbol: AVL, n: int) -> None:
    if arbol is None:
        return
    avl_verArbol(arbol.der, n + 4)
    print(" " * n + f"{arbol.nro}(FE={arbol.FE})")
    avl_verArbol(arbol.izq, n + 4)


def avl_esHoja(nodo: AVL) -> int:
    return 1 if nodo is not None and nodo.izq is None and nodo.der is None else 0


def avl_altura(arbol: AVL) -> int:
    if arbol is None:
        return 0
    return 1 + max(avl_altura(arbol.izq), avl_altura(arbol.der))


def avl_RSD(r: list[AVL], nodo: AVL) -> None:
    if nodo is None or nodo.izq is None:
        return
    nuevo = _rotar_derecha(nodo)
    _reemplazar_en_padre(r, nodo, nuevo)


def avl_RSI(r: list[AVL], nodo: AVL) -> None:
    if nodo is None or nodo.der is None:
        return
    nuevo = _rotar_izquierda(nodo)
    _reemplazar_en_padre(r, nodo, nuevo)


def avl_RDD(r: list[AVL], nodo: AVL) -> None:
    if nodo is None or nodo.izq is None:
        return
    nodo.izq = _rotar_izquierda(nodo.izq)
    if nodo.izq is not None:
        nodo.izq.padre = nodo
    nuevo = _rotar_derecha(nodo)
    _reemplazar_en_padre(r, nodo, nuevo)


def avl_RDI(r: list[AVL], nodo: AVL) -> None:
    if nodo is None or nodo.der is None:
        return
    nodo.der = _rotar_derecha(nodo.der)
    if nodo.der is not None:
        nodo.der.padre = nodo
    nuevo = _rotar_izquierda(nodo)
    _reemplazar_en_padre(r, nodo, nuevo)


def avl_insertar(raiz: list[AVL], x: int) -> None:
    raiz[0] = _insertar_rec(raiz[0], x, None)


def avl_eliminar(raiz: list[AVL], x: int) -> None:
    raiz[0] = _eliminar_rec(raiz[0], x)
    if raiz[0] is not None:
        raiz[0].padre = None


def avl_buscar(raiz: AVL, x: int) -> AVL:
    actual = raiz
    while actual is not None:
        if x == actual.nro:
            return actual
        actual = actual.izq if x < actual.nro else actual.der
    return None


def avl_minimo(nodo: AVL) -> AVL:
    actual = nodo
    while actual is not None and actual.izq is not None:
        actual = actual.izq
    return actual


def avl_liberarAVL(raiz: AVL) -> None:
    _ = raiz


def _insertar_rec(nodo: AVL, valor: int, padre: AVL) -> AVL:
    if nodo is None:
        return nodoAVL(nro=valor, padre=padre)
    if valor < nodo.nro:
        nodo.izq = _insertar_rec(nodo.izq, valor, nodo)
    elif valor > nodo.nro:
        nodo.der = _insertar_rec(nodo.der, valor, nodo)
    else:
        return nodo
    return _balancear(nodo)


def _eliminar_rec(nodo: AVL, valor: int) -> AVL:
    if nodo is None:
        return None
    if valor < nodo.nro:
        nodo.izq = _eliminar_rec(nodo.izq, valor)
        if nodo.izq is not None:
            nodo.izq.padre = nodo
    elif valor > nodo.nro:
        nodo.der = _eliminar_rec(nodo.der, valor)
        if nodo.der is not None:
            nodo.der.padre = nodo
    else:
        if nodo.izq is None:
            hijo = nodo.der
            if hijo is not None:
                hijo.padre = nodo.padre
            return hijo
        if nodo.der is None:
            hijo = nodo.izq
            if hijo is not None:
                hijo.padre = nodo.padre
            return hijo
        sucesor = avl_minimo(nodo.der)
        nodo.nro = sucesor.nro
        nodo.der = _eliminar_rec(nodo.der, sucesor.nro)
        if nodo.der is not None:
            nodo.der.padre = nodo
    return _balancear(nodo)


def _factor(nodo: AVL) -> int:
    if nodo is None:
        return 0
    return avl_altura(nodo.der) - avl_altura(nodo.izq)


def _actualizar_fe(nodo: AVL) -> None:
    if nodo is not None:
        nodo.FE = _factor(nodo)


def _balancear(nodo: AVL) -> AVL:
    _actualizar_fe(nodo)
    if nodo is None:
        return None
    if nodo.FE < -1:
        if _factor(nodo.izq) > 0:
            nodo.izq = _rotar_izquierda(nodo.izq)
            if nodo.izq is not None:
                nodo.izq.padre = nodo
        nuevo = _rotar_derecha(nodo)
        _actualizar_fe(nuevo.izq)
        _actualizar_fe(nuevo.der)
        _actualizar_fe(nuevo)
        return nuevo
    if nodo.FE > 1:
        if _factor(nodo.der) < 0:
            nodo.der = _rotar_derecha(nodo.der)
            if nodo.der is not None:
                nodo.der.padre = nodo
        nuevo = _rotar_izquierda(nodo)
        _actualizar_fe(nuevo.izq)
        _actualizar_fe(nuevo.der)
        _actualizar_fe(nuevo)
        return nuevo
    return nodo


def _rotar_izquierda(x: AVL) -> AVL:
    if x is None or x.der is None:
        return x
    y = x.der
    x.der = y.izq
    if y.izq is not None:
        y.izq.padre = x
    y.izq = x
    y.padre = x.padre
    x.padre = y
    _actualizar_fe(x)
    _actualizar_fe(y)
    return y


def _rotar_derecha(y: AVL) -> AVL:
    if y is None or y.izq is None:
        return y
    x = y.izq
    y.izq = x.der
    if x.der is not None:
        x.der.padre = y
    x.der = y
    x.padre = y.padre
    y.padre = x
    _actualizar_fe(y)
    _actualizar_fe(x)
    return x


def _reemplazar_en_padre(raiz_ref: list[AVL], viejo: AVL, nuevo: AVL) -> None:
    if viejo is None:
        return
    padre = viejo.padre
    if padre is None:
        raiz_ref[0] = nuevo
        if nuevo is not None:
            nuevo.padre = None
        return
    if padre.izq is viejo:
        padre.izq = nuevo
    else:
        padre.der = nuevo
    if nuevo is not None:
        nuevo.padre = padre

