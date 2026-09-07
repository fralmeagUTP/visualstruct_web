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
    z = rbt_buscar(arbol[0], key)
    if z is None:
        return

    y = z
    y_color_original = y.rbt_color
    x: RBT = None
    x_parent: RBT = None

    if z.izq is None:
        x = z.der
        x_parent = z.padre
        _trasplantar(arbol, z, z.der)
    elif z.der is None:
        x = z.izq
        x_parent = z.padre
        _trasplantar(arbol, z, z.izq)
    else:
        y = _minimo(z.der)
        assert y is not None
        y_color_original = y.rbt_color
        x = y.der
        if y.padre is z:
            x_parent = y
        else:
            _trasplantar(arbol, y, y.der)
            x_parent = y.padre
            y.der = z.der
            y.der.padre = y
        _trasplantar(arbol, z, y)
        y.izq = z.izq
        y.izq.padre = y
        y.rbt_color = z.rbt_color

    if y_color_original == NEGRO:
        _arreglar_eliminacion(arbol, x, x_parent)
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


def _color_de(nodo: RBT) -> str:
    return NEGRO if nodo is None else nodo.rbt_color


def _arreglar_eliminacion(arbol: list[RBT], x: RBT, x_parent: RBT) -> None:
    """Restaura los invariantes rojo-negro tratando ``None`` como NIL negro."""

    while x is not arbol[0] and _color_de(x) == NEGRO:
        if x_parent is None:
            break

        es_izq = x is x_parent.izq
        w = x_parent.der if es_izq else x_parent.izq

        if es_izq:
            if _color_de(w) == ROJO:
                assert w is not None
                w.rbt_color = NEGRO
                x_parent.rbt_color = ROJO
                rbt_rotar_izda(arbol, x_parent)
                w = x_parent.der

            w_izq = w.izq if w is not None else None
            w_der = w.der if w is not None else None
            if _color_de(w_izq) == NEGRO and _color_de(w_der) == NEGRO:
                if w is not None:
                    w.rbt_color = ROJO
                x = x_parent
                x_parent = x.padre
            else:
                if _color_de(w_der) == NEGRO:
                    if w_izq is not None:
                        w_izq.rbt_color = NEGRO
                    if w is not None:
                        w.rbt_color = ROJO
                        rbt_rotar_dcha(arbol, w)
                    w = x_parent.der
                    w_der = w.der if w is not None else None
                if w is not None:
                    w.rbt_color = _color_de(x_parent)
                x_parent.rbt_color = NEGRO
                if w_der is not None:
                    w_der.rbt_color = NEGRO
                rbt_rotar_izda(arbol, x_parent)
                x = arbol[0]
        else:
            if _color_de(w) == ROJO:
                assert w is not None
                w.rbt_color = NEGRO
                x_parent.rbt_color = ROJO
                rbt_rotar_dcha(arbol, x_parent)
                w = x_parent.izq

            w_izq = w.izq if w is not None else None
            w_der = w.der if w is not None else None
            if _color_de(w_der) == NEGRO and _color_de(w_izq) == NEGRO:
                if w is not None:
                    w.rbt_color = ROJO
                x = x_parent
                x_parent = x.padre
            else:
                if _color_de(w_izq) == NEGRO:
                    if w_der is not None:
                        w_der.rbt_color = NEGRO
                    if w is not None:
                        w.rbt_color = ROJO
                        rbt_rotar_izda(arbol, w)
                    w = x_parent.izq
                    w_izq = w.izq if w is not None else None
                if w is not None:
                    w.rbt_color = _color_de(x_parent)
                x_parent.rbt_color = NEGRO
                if w_izq is not None:
                    w_izq.rbt_color = NEGRO
                rbt_rotar_dcha(arbol, x_parent)
                x = arbol[0]

    if x is not None:
        x.rbt_color = NEGRO
