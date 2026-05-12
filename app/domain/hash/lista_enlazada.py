"""Singly linked list used as hash-table bucket container."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from .exceptions import EstructuraVaciaError, PosicionInvalidaError

T = TypeVar("T")


@dataclass(slots=True)
class _Nodo(Generic[T]):
    """Internal node for singly linked list."""

    dato: T
    siguiente: _Nodo[T] | None = None


class ListaEnlazada(Generic[T]):
    """Generic singly linked list."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._cabeza: _Nodo[T] | None = None
        self._cola: _Nodo[T] | None = None
        self._tamano = 0

        if valores is not None:
            for valor in valores:
                self.insertar_final(valor)

    def insertar_final(self, dato: T) -> None:
        """Insert value at tail in O(1)."""
        nuevo = _Nodo(dato=dato)
        if self._cola is None:
            self._cabeza = nuevo
            self._cola = nuevo
        else:
            self._cola.siguiente = nuevo
            self._cola = nuevo
        self._tamano += 1

    def eliminar_inicio(self) -> T:
        """Remove and return first value."""
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista esta vacia.")

        dato = self._cabeza.dato
        self._cabeza = self._cabeza.siguiente
        self._tamano -= 1

        if self._tamano == 0:
            self._cola = None

        return dato

    def eliminar_posicion(self, posicion: int) -> T:
        """Remove and return value at 0-based index."""
        if posicion < 0 or posicion >= self._tamano:
            raise PosicionInvalidaError("La posicion esta fuera de rango.")

        if posicion == 0:
            return self.eliminar_inicio()

        anterior = self._nodo_en(posicion - 1)
        objetivo = anterior.siguiente
        anterior.siguiente = objetivo.siguiente

        if objetivo is self._cola:
            self._cola = anterior

        self._tamano -= 1
        return objetivo.dato

    def limpiar(self) -> None:
        """Remove all nodes."""
        self._cabeza = None
        self._cola = None
        self._tamano = 0

    def tamano(self) -> int:
        """Return number of elements."""
        return self._tamano

    def _nodo_en(self, posicion: int) -> _Nodo[T]:
        if posicion < 0 or posicion >= self._tamano:
            raise PosicionInvalidaError("La posicion esta fuera de rango.")

        actual = self._cabeza
        for _ in range(posicion):
            actual = actual.siguiente
        return actual

    def __iter__(self) -> Iterator[T]:
        actual = self._cabeza
        while actual is not None:
            yield actual.dato
            actual = actual.siguiente
