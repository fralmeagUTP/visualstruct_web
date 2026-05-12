"""TAD Árbol AVL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterator, TypeVar

from .exceptions import ElementoDuplicadoError, ElementoNoEncontradoError

T = TypeVar("T")


@dataclass(slots=True)
class _NodoAVL(Generic[T]):
    dato: T
    altura: int = 1
    izquierdo: _NodoAVL[T] | None = None
    derecho: _NodoAVL[T] | None = None


class AVL(Generic[T]):
    """Árbol AVL genérico sin duplicados."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._raiz: _NodoAVL[T] | None = None
        self._tamano = 0

        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        self._raiz = self._insertar_rec(self._raiz, dato)

    def _insertar_rec(self, nodo: _NodoAVL[T] | None, dato: T) -> _NodoAVL[T]:
        if nodo is None:
            self._tamano += 1
            return _NodoAVL(dato=dato)

        if dato == nodo.dato:
            raise ElementoDuplicadoError(f"El dato {dato!r} ya existe.")

        if dato < nodo.dato:
            nodo.izquierdo = self._insertar_rec(nodo.izquierdo, dato)
        else:
            nodo.derecho = self._insertar_rec(nodo.derecho, dato)

        return self._balancear(nodo)

    def eliminar(self, dato: T) -> None:
        self._raiz = self._eliminar_rec(self._raiz, dato)

    def _eliminar_rec(self, nodo: _NodoAVL[T] | None, dato: T) -> _NodoAVL[T] | None:
        if nodo is None:
            raise ElementoNoEncontradoError(f"El dato {dato!r} no existe.")

        if dato < nodo.dato:
            nodo.izquierdo = self._eliminar_rec(nodo.izquierdo, dato)
        elif dato > nodo.dato:
            nodo.derecho = self._eliminar_rec(nodo.derecho, dato)
        else:
            self._tamano -= 1

            if nodo.izquierdo is None:
                return nodo.derecho

            if nodo.derecho is None:
                return nodo.izquierdo

            sucesor = self._minimo_nodo(nodo.derecho)
            nodo.dato = sucesor.dato
            self._tamano += 1
            nodo.derecho = self._eliminar_rec(nodo.derecho, sucesor.dato)

        return self._balancear(nodo) if nodo is not None else None

    def buscar(self, dato: T) -> bool:
        actual = self._raiz

        while actual is not None:
            if dato == actual.dato:
                return True
            actual = actual.izquierdo if dato < actual.dato else actual.derecho

        return False

    def _altura(self, nodo: _NodoAVL[T] | None) -> int:
        return 0 if nodo is None else nodo.altura

    def _actualizar_altura(self, nodo: _NodoAVL[T]) -> None:
        nodo.altura = 1 + max(self._altura(nodo.izquierdo), self._altura(nodo.derecho))

    def _factor_balance(self, nodo: _NodoAVL[T] | None) -> int:
        if nodo is None:
            return 0
        return self._altura(nodo.izquierdo) - self._altura(nodo.derecho)

    def _balancear(self, nodo: _NodoAVL[T]) -> _NodoAVL[T]:
        self._actualizar_altura(nodo)
        factor = self._factor_balance(nodo)

        if factor > 1:
            if self._factor_balance(nodo.izquierdo) < 0:
                nodo.izquierdo = self._rotar_izquierda(nodo.izquierdo)
            return self._rotar_derecha(nodo)

        if factor < -1:
            if self._factor_balance(nodo.derecho) > 0:
                nodo.derecho = self._rotar_derecha(nodo.derecho)
            return self._rotar_izquierda(nodo)

        return nodo

    def _rotar_derecha(self, y: _NodoAVL[T]) -> _NodoAVL[T]:
        x = y.izquierdo
        t2 = x.derecho

        x.derecho = y
        y.izquierdo = t2

        self._actualizar_altura(y)
        self._actualizar_altura(x)
        return x

    def _rotar_izquierda(self, x: _NodoAVL[T]) -> _NodoAVL[T]:
        y = x.derecho
        t2 = y.izquierdo

        y.izquierdo = x
        x.derecho = t2

        self._actualizar_altura(x)
        self._actualizar_altura(y)
        return y

    def _minimo_nodo(self, nodo: _NodoAVL[T]) -> _NodoAVL[T]:
        actual = nodo
        while actual.izquierdo is not None:
            actual = actual.izquierdo
        return actual

    def minimo(self) -> T:
        if self._raiz is None:
            raise ElementoNoEncontradoError("El árbol está vacío.")
        return self._minimo_nodo(self._raiz).dato

    def maximo(self) -> T:
        if self._raiz is None:
            raise ElementoNoEncontradoError("El árbol está vacío.")
        actual = self._raiz
        while actual.derecho is not None:
            actual = actual.derecho
        return actual.dato

    def altura(self) -> int:
        return self._altura(self._raiz)

    def inorden(self) -> list[T]:
        valores: list[T] = []
        self._inorden_rec(self._raiz, valores)
        return valores

    def _inorden_rec(self, nodo: _NodoAVL[T] | None, valores: list[T]) -> None:
        if nodo is None:
            return
        self._inorden_rec(nodo.izquierdo, valores)
        valores.append(nodo.dato)
        self._inorden_rec(nodo.derecho, valores)

    def validar(self) -> bool:
        valido, _, _ = self._validar_rec(self._raiz, None, None)
        return valido

    def _validar_rec(
        self,
        nodo: _NodoAVL[T] | None,
        minimo: T | None,
        maximo: T | None,
    ) -> tuple[bool, int, int]:
        if nodo is None:
            return True, 0, 0

        if minimo is not None and nodo.dato <= minimo:
            return False, 0, 0
        if maximo is not None and nodo.dato >= maximo:
            return False, 0, 0

        valido_izq, altura_izq, cant_izq = self._validar_rec(nodo.izquierdo, minimo, nodo.dato)
        valido_der, altura_der, cant_der = self._validar_rec(nodo.derecho, nodo.dato, maximo)
        altura_real = 1 + max(altura_izq, altura_der)
        factor = altura_izq - altura_der

        return (
            valido_izq and valido_der and nodo.altura == altura_real and -1 <= factor <= 1,
            altura_real,
            cant_izq + cant_der + 1,
        )

    def limpiar(self) -> None:
        self._raiz = None
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
        return f"AVL({self.inorden()!r})"
