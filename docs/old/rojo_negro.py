"""TAD Árbol Rojo-Negro."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, Iterator, TypeVar

from .exceptions import ElementoDuplicadoError, ElementoNoEncontradoError

T = TypeVar("T")


class ColorRN(Enum):
    ROJO = 0
    NEGRO = 1


@dataclass(slots=True)
class _NodoRN(Generic[T]):
    dato: T | None
    color: ColorRN
    padre: _NodoRN[T] | None = None
    izquierdo: _NodoRN[T] | None = None
    derecho: _NodoRN[T] | None = None


class RojoNegro(Generic[T]):
    """Árbol rojo-negro genérico sin duplicados."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._nil = _NodoRN(dato=None, color=ColorRN.NEGRO)
        self._nil.padre = self._nil
        self._nil.izquierdo = self._nil
        self._nil.derecho = self._nil
        self._raiz: _NodoRN[T] = self._nil
        self._tamano = 0

        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        padre = self._nil
        actual = self._raiz

        while actual is not self._nil:
            padre = actual
            if dato == actual.dato:
                raise ElementoDuplicadoError(f"El dato {dato!r} ya existe.")
            actual = actual.izquierdo if dato < actual.dato else actual.derecho

        nuevo = _NodoRN(
            dato=dato,
            color=ColorRN.ROJO,
            padre=padre,
            izquierdo=self._nil,
            derecho=self._nil,
        )

        if padre is self._nil:
            self._raiz = nuevo
        elif dato < padre.dato:
            padre.izquierdo = nuevo
        else:
            padre.derecho = nuevo

        self._tamano += 1
        self._arreglar_insercion(nuevo)

    def _arreglar_insercion(self, z: _NodoRN[T]) -> None:
        while z.padre.color == ColorRN.ROJO:
            if z.padre is z.padre.padre.izquierdo:
                y = z.padre.padre.derecho

                if y.color == ColorRN.ROJO:
                    z.padre.color = ColorRN.NEGRO
                    y.color = ColorRN.NEGRO
                    z.padre.padre.color = ColorRN.ROJO
                    z = z.padre.padre
                else:
                    if z is z.padre.derecho:
                        z = z.padre
                        self._rotar_izquierda(z)

                    z.padre.color = ColorRN.NEGRO
                    z.padre.padre.color = ColorRN.ROJO
                    self._rotar_derecha(z.padre.padre)
            else:
                y = z.padre.padre.izquierdo

                if y.color == ColorRN.ROJO:
                    z.padre.color = ColorRN.NEGRO
                    y.color = ColorRN.NEGRO
                    z.padre.padre.color = ColorRN.ROJO
                    z = z.padre.padre
                else:
                    if z is z.padre.izquierdo:
                        z = z.padre
                        self._rotar_derecha(z)

                    z.padre.color = ColorRN.NEGRO
                    z.padre.padre.color = ColorRN.ROJO
                    self._rotar_izquierda(z.padre.padre)

        self._raiz.color = ColorRN.NEGRO

    def eliminar(self, dato: T) -> None:
        z = self._buscar_nodo(dato)
        if z is self._nil:
            raise ElementoNoEncontradoError(f"El dato {dato!r} no existe.")

        y = z
        color_original = y.color

        if z.izquierdo is self._nil:
            x = z.derecho
            self._trasplantar(z, z.derecho)
        elif z.derecho is self._nil:
            x = z.izquierdo
            self._trasplantar(z, z.izquierdo)
        else:
            y = self._minimo_nodo(z.derecho)
            color_original = y.color
            x = y.derecho

            if y.padre is z:
                x.padre = y
            else:
                self._trasplantar(y, y.derecho)
                y.derecho = z.derecho
                y.derecho.padre = y

            self._trasplantar(z, y)
            y.izquierdo = z.izquierdo
            y.izquierdo.padre = y
            y.color = z.color

        self._tamano -= 1

        if color_original == ColorRN.NEGRO:
            self._arreglar_eliminacion(x)

    def _arreglar_eliminacion(self, x: _NodoRN[T]) -> None:
        while x is not self._raiz and x.color == ColorRN.NEGRO:
            if x is x.padre.izquierdo:
                w = x.padre.derecho

                if w.color == ColorRN.ROJO:
                    w.color = ColorRN.NEGRO
                    x.padre.color = ColorRN.ROJO
                    self._rotar_izquierda(x.padre)
                    w = x.padre.derecho

                if w.izquierdo.color == ColorRN.NEGRO and w.derecho.color == ColorRN.NEGRO:
                    w.color = ColorRN.ROJO
                    x = x.padre
                else:
                    if w.derecho.color == ColorRN.NEGRO:
                        w.izquierdo.color = ColorRN.NEGRO
                        w.color = ColorRN.ROJO
                        self._rotar_derecha(w)
                        w = x.padre.derecho

                    w.color = x.padre.color
                    x.padre.color = ColorRN.NEGRO
                    w.derecho.color = ColorRN.NEGRO
                    self._rotar_izquierda(x.padre)
                    x = self._raiz
            else:
                w = x.padre.izquierdo

                if w.color == ColorRN.ROJO:
                    w.color = ColorRN.NEGRO
                    x.padre.color = ColorRN.ROJO
                    self._rotar_derecha(x.padre)
                    w = x.padre.izquierdo

                if w.derecho.color == ColorRN.NEGRO and w.izquierdo.color == ColorRN.NEGRO:
                    w.color = ColorRN.ROJO
                    x = x.padre
                else:
                    if w.izquierdo.color == ColorRN.NEGRO:
                        w.derecho.color = ColorRN.NEGRO
                        w.color = ColorRN.ROJO
                        self._rotar_izquierda(w)
                        w = x.padre.izquierdo

                    w.color = x.padre.color
                    x.padre.color = ColorRN.NEGRO
                    w.izquierdo.color = ColorRN.NEGRO
                    self._rotar_derecha(x.padre)
                    x = self._raiz

        x.color = ColorRN.NEGRO

    def buscar(self, dato: T) -> bool:
        return self._buscar_nodo(dato) is not self._nil

    def _buscar_nodo(self, dato: T) -> _NodoRN[T]:
        actual = self._raiz

        while actual is not self._nil:
            if dato == actual.dato:
                return actual
            actual = actual.izquierdo if dato < actual.dato else actual.derecho

        return self._nil

    def _minimo_nodo(self, nodo: _NodoRN[T]) -> _NodoRN[T]:
        actual = nodo
        while actual.izquierdo is not self._nil:
            actual = actual.izquierdo
        return actual

    def _trasplantar(self, u: _NodoRN[T], v: _NodoRN[T]) -> None:
        if u.padre is self._nil:
            self._raiz = v
        elif u is u.padre.izquierdo:
            u.padre.izquierdo = v
        else:
            u.padre.derecho = v
        v.padre = u.padre

    def _rotar_izquierda(self, x: _NodoRN[T]) -> None:
        y = x.derecho
        x.derecho = y.izquierdo

        if y.izquierdo is not self._nil:
            y.izquierdo.padre = x

        y.padre = x.padre

        if x.padre is self._nil:
            self._raiz = y
        elif x is x.padre.izquierdo:
            x.padre.izquierdo = y
        else:
            x.padre.derecho = y

        y.izquierdo = x
        x.padre = y

    def _rotar_derecha(self, y: _NodoRN[T]) -> None:
        x = y.izquierdo
        y.izquierdo = x.derecho

        if x.derecho is not self._nil:
            x.derecho.padre = y

        x.padre = y.padre

        if y.padre is self._nil:
            self._raiz = x
        elif y is y.padre.derecho:
            y.padre.derecho = x
        else:
            y.padre.izquierdo = x

        x.derecho = y
        y.padre = x

    def inorden(self) -> list[T]:
        valores: list[T] = []
        self._inorden_rec(self._raiz, valores)
        return valores

    def _inorden_rec(self, nodo: _NodoRN[T], valores: list[T]) -> None:
        if nodo is self._nil:
            return
        self._inorden_rec(nodo.izquierdo, valores)
        valores.append(nodo.dato)
        self._inorden_rec(nodo.derecho, valores)

    def altura(self) -> int:
        return self._altura_rec(self._raiz)

    def _altura_rec(self, nodo: _NodoRN[T]) -> int:
        if nodo is self._nil:
            return 0
        return 1 + max(self._altura_rec(nodo.izquierdo), self._altura_rec(nodo.derecho))

    def validar(self) -> bool:
        if self._raiz is self._nil:
            return True
        if self._raiz.color != ColorRN.NEGRO:
            return False
        valido, _ = self._validar_rec(self._raiz, None, None)
        return valido

    def _validar_rec(
        self,
        nodo: _NodoRN[T],
        minimo: T | None,
        maximo: T | None,
    ) -> tuple[bool, int]:
        if nodo is self._nil:
            return True, 1

        if minimo is not None and nodo.dato <= minimo:
            return False, 0
        if maximo is not None and nodo.dato >= maximo:
            return False, 0

        if nodo.color == ColorRN.ROJO:
            if nodo.izquierdo.color != ColorRN.NEGRO or nodo.derecho.color != ColorRN.NEGRO:
                return False, 0

        valido_izq, negros_izq = self._validar_rec(nodo.izquierdo, minimo, nodo.dato)
        valido_der, negros_der = self._validar_rec(nodo.derecho, nodo.dato, maximo)

        if not valido_izq or not valido_der or negros_izq != negros_der:
            return False, 0

        return True, negros_izq + (1 if nodo.color == ColorRN.NEGRO else 0)

    def limpiar(self) -> None:
        self._raiz = self._nil
        self._nil.padre = self._nil
        self._tamano = 0

    def vacio(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def __len__(self) -> int:
        return self._tamano

    def __contains__(self, dato: object) -> bool:
        return self.buscar(dato)

    def __iter__(self) -> Iterator[T]:
        return iter(self.inorden())

    def __repr__(self) -> str:
        return f"RojoNegro({self.inorden()!r})"
