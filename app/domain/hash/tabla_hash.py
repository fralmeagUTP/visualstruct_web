"""Hash table TAD with separate chaining buckets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .lista_enlazada import ListaEnlazada

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True)
class _Entrada(Generic[K, V]):
    """Internal key-value entry."""

    clave: K
    valor: V


class TablaHash(Generic[K, V]):
    """Generic hash table with linked-list buckets."""

    def __init__(self, capacidad: int = 17) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")

        self._capacidad = capacidad
        self._cantidad = 0
        self._buckets: list[ListaEnlazada[_Entrada[K, V]]] = [
            ListaEnlazada() for _ in range(capacidad)
        ]

    def _indice(self, clave: K) -> int:
        return hash(clave) % self._capacidad

    def insertar(self, clave: K, valor: V) -> None:
        """Insert or update one key-value entry."""
        bucket = self._buckets[self._indice(clave)]

        for entrada in bucket:
            if entrada.clave == clave:
                entrada.valor = valor
                return

        bucket.insertar_final(_Entrada(clave, valor))
        self._cantidad += 1

        if self.factor_carga() > 0.75:
            self._redimensionar(self._capacidad * 2 + 1)

    def buscar(self, clave: K) -> V | None:
        """Return value for key, or None when missing."""
        bucket = self._buckets[self._indice(clave)]

        for entrada in bucket:
            if entrada.clave == clave:
                return entrada.valor

        return None

    def contiene(self, clave: K) -> bool:
        """Return True when key exists."""
        bucket = self._buckets[self._indice(clave)]
        return any(entrada.clave == clave for entrada in bucket)

    def eliminar(self, clave: K) -> bool:
        """Delete key and return True when removed."""
        bucket = self._buckets[self._indice(clave)]

        for posicion, entrada in enumerate(bucket):
            if entrada.clave == clave:
                bucket.eliminar_posicion(posicion)
                self._cantidad -= 1
                return True

        return False

    def claves(self) -> list[K]:
        """Return all keys."""
        return [entrada.clave for bucket in self._buckets for entrada in bucket]

    def valores(self) -> list[V]:
        """Return all values."""
        return [entrada.valor for bucket in self._buckets for entrada in bucket]

    def items(self) -> list[tuple[K, V]]:
        """Return all key-value pairs."""
        return [
            (entrada.clave, entrada.valor)
            for bucket in self._buckets
            for entrada in bucket
        ]

    def factor_carga(self) -> float:
        """Return load factor."""
        return self._cantidad / self._capacidad

    def tamano(self) -> int:
        """Return number of entries."""
        return self._cantidad

    def capacidad(self) -> int:
        """Return current bucket capacity."""
        return self._capacidad

    def limpiar(self) -> None:
        """Clear every bucket."""
        self._buckets = [ListaEnlazada() for _ in range(self._capacidad)]
        self._cantidad = 0

    def _redimensionar(self, nueva_capacidad: int) -> None:
        antiguos = self.items()
        self._capacidad = nueva_capacidad
        self._buckets = [ListaEnlazada() for _ in range(nueva_capacidad)]
        self._cantidad = 0

        for clave, valor in antiguos:
            self.insertar(clave, valor)

    def __len__(self) -> int:
        return self._cantidad

    def __repr__(self) -> str:
        return f"TablaHash({self.items()!r})"
