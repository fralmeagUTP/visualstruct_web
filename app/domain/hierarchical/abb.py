"""TAD Árbol Binario de Búsqueda."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, TypeVar, Generic

from .exceptions import ElementoDuplicadoError, ElementoNoEncontradoError

T = TypeVar("T")


@dataclass(slots=True)
class _NodoABB(Generic[T]):
    dato: T
    izquierdo: _NodoABB[T] | None = None
    derecho: _NodoABB[T] | None = None


class ABB(Generic[T]):
    """Árbol binario de búsqueda genérico sin duplicados."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._raiz: _NodoABB[T] | None = None
        self._tamano = 0

        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        """Inserta un dato. Lanza ElementoDuplicadoError si ya existe."""
        self._raiz = self._insertar_rec(self._raiz, dato)

    def _insertar_rec(self, nodo: _NodoABB[T] | None, dato: T) -> _NodoABB[T]:
        if nodo is None:
            self._tamano += 1
            return _NodoABB(dato)

        if dato == nodo.dato:
            raise ElementoDuplicadoError(f"El dato {dato!r} ya existe.")

        if dato < nodo.dato:
            nodo.izquierdo = self._insertar_rec(nodo.izquierdo, dato)
        else:
            nodo.derecho = self._insertar_rec(nodo.derecho, dato)

        return nodo

    def eliminar(self, dato: T) -> None:
        """Elimina un dato. Lanza ElementoNoEncontradoError si no existe."""
        self._raiz = self._eliminar_rec(self._raiz, dato)

    def _eliminar_rec(self, nodo: _NodoABB[T] | None, dato: T) -> _NodoABB[T] | None:
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

        return nodo

    def buscar(self, dato: T) -> bool:
        """Indica si un dato existe."""
        actual = self._raiz

        while actual is not None:
            if dato == actual.dato:
                return True
            actual = actual.izquierdo if dato < actual.dato else actual.derecho

        return False

    def minimo(self) -> T:
        """Retorna el menor dato."""
        if self._raiz is None:
            raise ElementoNoEncontradoError("El árbol está vacío.")
        return self._minimo_nodo(self._raiz).dato

    def maximo(self) -> T:
        """Retorna el mayor dato."""
        if self._raiz is None:
            raise ElementoNoEncontradoError("El árbol está vacío.")
        actual = self._raiz
        while actual.derecho is not None:
            actual = actual.derecho
        return actual.dato

    def _minimo_nodo(self, nodo: _NodoABB[T]) -> _NodoABB[T]:
        actual = nodo
        while actual.izquierdo is not None:
            actual = actual.izquierdo
        return actual

    def altura(self) -> int:
        return self._altura_rec(self._raiz)

    def _altura_rec(self, nodo: _NodoABB[T] | None) -> int:
        if nodo is None:
            return 0
        return 1 + max(self._altura_rec(nodo.izquierdo), self._altura_rec(nodo.derecho))

    def contar_hojas(self) -> int:
        return self._contar_hojas_rec(self._raiz)

    def _contar_hojas_rec(self, nodo: _NodoABB[T] | None) -> int:
        if nodo is None:
            return 0
        if nodo.izquierdo is None and nodo.derecho is None:
            return 1
        return self._contar_hojas_rec(nodo.izquierdo) + self._contar_hojas_rec(nodo.derecho)

    def inorden(self) -> list[T]:
        valores: list[T] = []
        self._inorden_rec(self._raiz, valores)
        return valores

    def _inorden_rec(self, nodo: _NodoABB[T] | None, valores: list[T]) -> None:
        if nodo is None:
            return
        self._inorden_rec(nodo.izquierdo, valores)
        valores.append(nodo.dato)
        self._inorden_rec(nodo.derecho, valores)

    def preorden(self) -> list[T]:
        valores: list[T] = []
        self._preorden_rec(self._raiz, valores)
        return valores

    def _preorden_rec(self, nodo: _NodoABB[T] | None, valores: list[T]) -> None:
        if nodo is None:
            return
        valores.append(nodo.dato)
        self._preorden_rec(nodo.izquierdo, valores)
        self._preorden_rec(nodo.derecho, valores)

    def postorden(self) -> list[T]:
        valores: list[T] = []
        self._postorden_rec(self._raiz, valores)
        return valores

    def _postorden_rec(self, nodo: _NodoABB[T] | None, valores: list[T]) -> None:
        if nodo is None:
            return
        self._postorden_rec(nodo.izquierdo, valores)
        self._postorden_rec(nodo.derecho, valores)
        valores.append(nodo.dato)

    def validar(self) -> bool:
        return self._validar_rec(self._raiz, None, None)

    def _validar_rec(self, nodo: _NodoABB[T] | None, minimo: T | None, maximo: T | None) -> bool:
        if nodo is None:
            return True
        if minimo is not None and nodo.dato <= minimo:
            return False
        if maximo is not None and nodo.dato >= maximo:
            return False
        return (
            self._validar_rec(nodo.izquierdo, minimo, nodo.dato)
            and self._validar_rec(nodo.derecho, nodo.dato, maximo)
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
        return f"ABB({self.inorden()!r})"
