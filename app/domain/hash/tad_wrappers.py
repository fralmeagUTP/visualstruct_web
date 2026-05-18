"""Wrappers de alto nivel sobre `tad_tabla_hash`."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from .tad_tabla_hash import THNodo, TablaHash as TablaHashTAD, th_buscar, th_capacidad, th_cantidad, th_contiene, th_destruir, th_eliminar, th_inicializar, th_insertar, th_vaciar

K = TypeVar("K")
V = TypeVar("V")


@dataclass(slots=True)
class _Entrada(Generic[K, V]):
    clave: K
    valor: V


class TablaHash(Generic[K, V]):
    """Tabla hash compatible con la app, respaldada por el TAD nuevo."""

    def __init__(self, capacidad: int = 17) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad debe ser positiva.")
        self._tabla = TablaHashTAD()
        th_inicializar(self._tabla, capacidad)
        self._key_to_id: dict[K, int] = {}
        self._id_to_key: dict[int, K] = {}
        self._values_by_key: dict[K, V] = {}
        self._buckets: list[list[_Entrada[K, V]]] = []
        self._sync_buckets_cache()

    def _indice(self, clave: K) -> int:
        return hash(clave) % self.capacidad()

    def _allocate_id_for_key(self, clave: K) -> int:
        if clave in self._key_to_id:
            return self._key_to_id[clave]
        base = self._indice(clave)
        step = self.capacidad()
        candidato = base
        while candidato in self._id_to_key and self._id_to_key[candidato] != clave:
            candidato += step
        return candidato

    def insertar(self, clave: K, valor: V) -> None:
        if clave in self._key_to_id:
            self._values_by_key[clave] = valor
            self._sync_buckets_cache()
            return

        ident = self._allocate_id_for_key(clave)
        th_insertar(self._tabla, ident, ident)
        self._key_to_id[clave] = ident
        self._id_to_key[ident] = clave
        self._values_by_key[clave] = valor

        if self.factor_carga() > 0.75:
            self._redimensionar(self.capacidad() * 2 + 1)
        else:
            self._sync_buckets_cache()

    def buscar(self, clave: K) -> V | None:
        if clave not in self._key_to_id:
            return None
        ident = self._key_to_id[clave]
        out: list[int] = []
        if not th_buscar(self._tabla, ident, out):
            return None
        return self._values_by_key.get(clave)

    def contiene(self, clave: K) -> bool:
        if clave not in self._key_to_id:
            return False
        return bool(th_contiene(self._tabla, self._key_to_id[clave]))

    def eliminar(self, clave: K) -> bool:
        if clave not in self._key_to_id:
            return False
        ident = self._key_to_id[clave]
        ok = th_eliminar(self._tabla, ident)
        if not ok:
            return False
        self._key_to_id.pop(clave, None)
        self._id_to_key.pop(ident, None)
        self._values_by_key.pop(clave, None)
        self._sync_buckets_cache()
        return True

    def claves(self) -> list[K]:
        return [entrada.clave for bucket in self._buckets for entrada in bucket]

    def valores(self) -> list[V]:
        return [entrada.valor for bucket in self._buckets for entrada in bucket]

    def items(self) -> list[tuple[K, V]]:
        return [(entrada.clave, entrada.valor) for bucket in self._buckets for entrada in bucket]

    def factor_carga(self) -> float:
        cap = self.capacidad()
        return (self.tamano() / cap) if cap > 0 else 0.0

    def tamano(self) -> int:
        return th_cantidad(self._tabla)

    def capacidad(self) -> int:
        return th_capacidad(self._tabla)

    def limpiar(self) -> None:
        th_vaciar(self._tabla)
        self._key_to_id.clear()
        self._id_to_key.clear()
        self._values_by_key.clear()
        self._sync_buckets_cache()

    def _redimensionar(self, nueva_capacidad: int) -> None:
        antiguos = list(self._values_by_key.items())
        th_destruir(self._tabla)
        th_inicializar(self._tabla, nueva_capacidad)
        self._key_to_id.clear()
        self._id_to_key.clear()
        self._values_by_key.clear()
        for clave, valor in antiguos:
            ident = self._allocate_id_for_key(clave)
            th_insertar(self._tabla, ident, ident)
            self._key_to_id[clave] = ident
            self._id_to_key[ident] = clave
            self._values_by_key[clave] = valor
        self._sync_buckets_cache()

    def _sync_buckets_cache(self) -> None:
        buckets: list[list[_Entrada[K, V]]] = [[] for _ in range(self.capacidad())]
        for idx, head in enumerate(self._tabla.buckets):
            actual: THNodo | None = head
            while actual is not None:
                ident = actual.clave
                clave = self._id_to_key.get(ident)
                if clave in self._values_by_key:
                    buckets[idx].append(_Entrada(clave=clave, valor=self._values_by_key[clave]))
                actual = actual.siguiente
        self._buckets = buckets

    def __len__(self) -> int:
        return self.tamano()

    def __repr__(self) -> str:
        return f"TablaHash({self.items()!r})"
