"""TAD Lista Circular Simple."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from .exceptions import EstructuraVaciaError

T = TypeVar("T")


@dataclass(slots=True)
class _NodoCircular(Generic[T]):
    dato: T
    siguiente: _NodoCircular[T] | None = None


class ListaCircular(Generic[T]):
    """Lista circular con punteros a cabeza y cola."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._cabeza: _NodoCircular[T] | None = None
        self._cola: _NodoCircular[T] | None = None
        self._tamano = 0

        if valores is not None:
            for valor in valores:
                self.insertar_final(valor)

    def insertar_inicio(self, dato: T) -> None:
        nuevo = _NodoCircular(dato=dato)

        if self._cabeza is None:
            nuevo.siguiente = nuevo
            self._cabeza = nuevo
            self._cola = nuevo
        else:
            nuevo.siguiente = self._cabeza
            self._cola.siguiente = nuevo
            self._cabeza = nuevo

        self._tamano += 1

    def insertar_final(self, dato: T) -> None:
        nuevo = _NodoCircular(dato=dato)

        if self._cabeza is None:
            nuevo.siguiente = nuevo
            self._cabeza = nuevo
            self._cola = nuevo
        else:
            nuevo.siguiente = self._cabeza
            self._cola.siguiente = nuevo
            self._cola = nuevo

        self._tamano += 1

    def eliminar_inicio(self) -> T:
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista circular está vacía.")

        dato = self._cabeza.dato

        if self._tamano == 1:
            self._cabeza = None
            self._cola = None
        else:
            self._cabeza = self._cabeza.siguiente
            self._cola.siguiente = self._cabeza

        self._tamano -= 1
        return dato

    def buscar_posiciones(self, dato: T) -> list[int]:
        posiciones: list[int] = []

        for posicion, valor in enumerate(self):
            if valor == dato:
                posiciones.append(posicion)

        return posiciones

    def limpiar(self) -> None:
        self._cabeza = None
        self._cola = None
        self._tamano = 0

    def vacia(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def a_lista(self) -> list[T]:
        return list(iter(self))

    def __len__(self) -> int:
        return self._tamano

    def __iter__(self) -> Iterator[T]:
        actual = self._cabeza
        for _ in range(self._tamano):
            yield actual.dato
            actual = actual.siguiente

    def __repr__(self) -> str:
        return f"ListaCircular({self.a_lista()!r})"
