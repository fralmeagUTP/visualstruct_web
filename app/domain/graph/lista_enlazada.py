"""TAD Lista Enlazada Simple.

La lista enlazada es una estructura base reutilizada por otros TAD:
- Pila
- Cola
- TablaHash, como buckets de encadenamiento separado

La implementación mantiene punteros a cabeza y cola para permitir inserciones
eficientes al inicio y al final.
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from .exceptions import EstructuraVaciaError, PosicionInvalidaError

T = TypeVar("T")


@dataclass(slots=True)
class _Nodo(Generic[T]):
    """Nodo interno de una lista enlazada simple."""

    dato: T
    siguiente: _Nodo[T] | None = None


class ListaEnlazada(Generic[T]):
    """Lista simplemente enlazada genérica."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._cabeza: _Nodo[T] | None = None
        self._cola: _Nodo[T] | None = None
        self._tamano = 0

        if valores is not None:
            for valor in valores:
                self.insertar_final(valor)

    def insertar_inicio(self, dato: T) -> None:
        """Inserta un dato al inicio. Complejidad: O(1)."""
        nuevo = _Nodo(dato=dato, siguiente=self._cabeza)
        self._cabeza = nuevo

        if self._cola is None:
            self._cola = nuevo

        self._tamano += 1

    def insertar_final(self, dato: T) -> None:
        """Inserta un dato al final. Complejidad: O(1)."""
        nuevo = _Nodo(dato=dato)

        if self._cola is None:
            self._cabeza = nuevo
            self._cola = nuevo
        else:
            self._cola.siguiente = nuevo
            self._cola = nuevo

        self._tamano += 1

    def insertar_posicion(self, posicion: int, dato: T) -> None:
        """Inserta en una posición 0-based. Complejidad: O(n)."""
        if posicion < 0 or posicion > self._tamano:
            raise PosicionInvalidaError("La posición está fuera de rango.")

        if posicion == 0:
            self.insertar_inicio(dato)
            return

        if posicion == self._tamano:
            self.insertar_final(dato)
            return

        anterior = self._nodo_en(posicion - 1)
        nuevo = _Nodo(dato=dato, siguiente=anterior.siguiente)
        anterior.siguiente = nuevo
        self._tamano += 1

    def eliminar_inicio(self) -> T:
        """Elimina y retorna el primer dato. Complejidad: O(1)."""
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista está vacía.")

        dato = self._cabeza.dato
        self._cabeza = self._cabeza.siguiente
        self._tamano -= 1

        if self._tamano == 0:
            self._cola = None

        return dato

    def eliminar_final(self) -> T:
        """Elimina y retorna el último dato. Complejidad: O(n)."""
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista está vacía.")

        if self._cabeza is self._cola:
            return self.eliminar_inicio()

        actual = self._cabeza
        while actual.siguiente is not self._cola:
            actual = actual.siguiente

        dato = self._cola.dato
        actual.siguiente = None
        self._cola = actual
        self._tamano -= 1
        return dato

    def eliminar_posicion(self, posicion: int) -> T:
        """Elimina y retorna el dato en una posición 0-based. Complejidad: O(n)."""
        if posicion < 0 or posicion >= self._tamano:
            raise PosicionInvalidaError("La posición está fuera de rango.")

        if posicion == 0:
            return self.eliminar_inicio()

        anterior = self._nodo_en(posicion - 1)
        objetivo = anterior.siguiente
        anterior.siguiente = objetivo.siguiente

        if objetivo is self._cola:
            self._cola = anterior

        self._tamano -= 1
        return objetivo.dato

    def eliminar_primero(self, dato: T) -> bool:
        """Elimina la primera ocurrencia de un dato. Retorna True si elimina."""
        anterior: _Nodo[T] | None = None
        actual = self._cabeza

        while actual is not None:
            if actual.dato == dato:
                if anterior is None:
                    self.eliminar_inicio()
                else:
                    anterior.siguiente = actual.siguiente
                    if actual is self._cola:
                        self._cola = anterior
                    self._tamano -= 1
                return True

            anterior = actual
            actual = actual.siguiente

        return False

    def buscar_posiciones(self, dato: T) -> list[int]:
        """Retorna posiciones 0-based donde aparece el dato. Complejidad: O(n)."""
        posiciones: list[int] = []
        actual = self._cabeza
        posicion = 0

        while actual is not None:
            if actual.dato == dato:
                posiciones.append(posicion)
            actual = actual.siguiente
            posicion += 1

        return posiciones

    def invertir(self) -> None:
        """Invierte la lista in-place. Complejidad: O(n)."""
        anterior = None
        actual = self._cabeza
        self._cola = self._cabeza

        while actual is not None:
            siguiente = actual.siguiente
            actual.siguiente = anterior
            anterior = actual
            actual = siguiente

        self._cabeza = anterior

    def primero(self) -> T:
        """Retorna el primer dato sin eliminarlo."""
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista está vacía.")
        return self._cabeza.dato

    def ultimo(self) -> T:
        """Retorna el último dato sin eliminarlo."""
        if self._cola is None:
            raise EstructuraVaciaError("La lista está vacía.")
        return self._cola.dato

    def limpiar(self) -> None:
        """Elimina todos los nodos. Complejidad: O(1) en Python."""
        self._cabeza = None
        self._cola = None
        self._tamano = 0

    def vacia(self) -> bool:
        """Indica si la lista está vacía."""
        return self._tamano == 0

    def tamano(self) -> int:
        """Retorna el número de elementos."""
        return self._tamano

    def a_lista(self) -> list[T]:
        """Retorna los datos en una lista de Python."""
        return list(iter(self))

    def _nodo_en(self, posicion: int) -> _Nodo[T]:
        if posicion < 0 or posicion >= self._tamano:
            raise PosicionInvalidaError("La posición está fuera de rango.")

        actual = self._cabeza
        for _ in range(posicion):
            actual = actual.siguiente

        return actual

    def __len__(self) -> int:
        return self._tamano

    def __iter__(self) -> Iterator[T]:
        actual = self._cabeza

        while actual is not None:
            yield actual.dato
            actual = actual.siguiente

    def __contains__(self, dato: object) -> bool:
        return any(elemento == dato for elemento in self)

    def __repr__(self) -> str:
        return f"ListaEnlazada({self.a_lista()!r})"
