"""Wrappers de alto nivel construidos sobre los nuevos `tad_*`.

Este modulo reemplaza a los wrappers legacy por archivo separado
(`pila.py`, `cola.py`, etc.) para que la app use solo los nuevos TAD.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from .exceptions import ElementoNoEncontradoError, EstructuraVaciaError, PosicionInvalidaError
from .tad_cola import Cola as ColaTAD
from .tad_cola import cola_desencolar, cola_encolar, cola_vaciar
from .tad_cola_prioridad import (
    ColaPrioridad as ColaPrioridadTAD,
    cp_contar,
    cp_copiar_items,
    cp_desencolar,
    cp_encolar,
    cp_inicializar,
    cp_vacia,
    cp_vaciar,
)
from .tad_lista import (
    NodoLista,
    Tlista,
    lista_buscar_posiciones,
    lista_configurar_insertar_antes_despues_provider,
    lista_eliminar_elemento,
    lista_eliminar_repetidos,
    lista_insertar_elemento,
    lista_insertar_final,
    lista_insertar_inicio,
)
from .tad_lista_circular import (
    ListaCircular as ListaCircularTAD,
    lcir_buscar_posiciones,
    lcir_contar,
    lcir_copiar_valores,
    lcir_destruir,
    lcir_eliminar_primero,
    lcir_inicializar,
    lcir_insertar_final,
    lcir_insertar_inicio,
    lcir_invertir,
    lcir_vacia,
)
from .tad_monticulo_binario import (
    MONTICULO_MAX,
    MONTICULO_MIN,
    MonticuloBinario as MonticuloTAD,
    monticulo_cantidad,
    monticulo_destruir,
    monticulo_extraer_raiz,
    monticulo_inicializar,
    monticulo_insertar,
    monticulo_raiz,
    monticulo_vacio,
)
from .tad_pila import NodoPila, pila_apilar, pila_desapilar, pila_destruir
from .tad_sublista import (
    Nodo as NodoSublistaTAD,
    sublista_buscar_padre,
    sublista_copiar_hijos,
    sublista_eliminar_hijo_primero,
    sublista_eliminar_padre_primero,
    sublista_inicializar,
    sublista_insertar_hijo_final,
    sublista_insertar_padre_final,
)

T = TypeVar("T")


class Pila(Generic[T]):
    """Pila LIFO envuelta sobre `tad_pila`."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._tope_ref: list[NodoPila | None] = [None]
        self._tamano = 0
        if valores is not None:
            for valor in valores:
                self.apilar(valor)

    def apilar(self, dato: T) -> None:
        pila_apilar(self._tope_ref, int(dato))
        self._tamano += 1

    push = apilar

    def desapilar(self) -> T:
        if self._tamano == 0:
            raise EstructuraVaciaError("La pila esta vacia.")
        valor = pila_desapilar(self._tope_ref)
        self._tamano -= 1
        return valor  # type: ignore[return-value]

    pop = desapilar

    def cima(self) -> T:
        if self._tope_ref[0] is None:
            raise EstructuraVaciaError("La pila esta vacia.")
        return self._tope_ref[0].nro  # type: ignore[return-value]

    peek = cima

    def limpiar(self) -> None:
        pila_destruir(self._tope_ref)
        self._tamano = 0

    def vacia(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def a_lista(self) -> list[T]:
        out: list[T] = []
        actual = self._tope_ref[0]
        while actual is not None:
            out.append(actual.nro)  # type: ignore[arg-type]
            actual = actual.sgte
        return out

    def __len__(self) -> int:
        return self._tamano

    def __iter__(self) -> Iterator[T]:
        return iter(self.a_lista())

    def __repr__(self) -> str:
        return f"Pila({self.a_lista()!r})"


class Cola(Generic[T]):
    """Cola FIFO envuelta sobre `tad_cola`."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._cola = ColaTAD()
        self._tamano = 0
        if valores is not None:
            for valor in valores:
                self.encolar(valor)

    def encolar(self, dato: T) -> None:
        cola_encolar(self._cola, int(dato))
        self._tamano += 1

    enqueue = encolar

    def desencolar(self) -> T:
        if self._tamano == 0:
            raise EstructuraVaciaError("La cola esta vacia.")
        valor = cola_desencolar(self._cola)
        self._tamano -= 1
        return valor  # type: ignore[return-value]

    dequeue = desencolar

    def frente(self) -> T:
        if self._cola.delante is None:
            raise EstructuraVaciaError("La cola esta vacia.")
        return self._cola.delante.nro  # type: ignore[return-value]

    def final(self) -> T:
        if self._cola.atras is None:
            raise EstructuraVaciaError("La cola esta vacia.")
        return self._cola.atras.nro  # type: ignore[return-value]

    def limpiar(self) -> None:
        cola_vaciar(self._cola)
        self._tamano = 0

    def vacia(self) -> bool:
        return self._tamano == 0

    def tamano(self) -> int:
        return self._tamano

    def a_lista(self) -> list[T]:
        out: list[T] = []
        actual = self._cola.delante
        while actual is not None:
            out.append(actual.nro)  # type: ignore[arg-type]
            actual = actual.sgte
        return out

    def __len__(self) -> int:
        return self._tamano

    def __iter__(self) -> Iterator[T]:
        return iter(self.a_lista())

    def __repr__(self) -> str:
        return f"Cola({self.a_lista()!r})"


class ColaPrioridad(Generic[T]):
    """Cola de prioridad estable (menor numero = mayor prioridad)."""

    def __init__(self) -> None:
        self._cola = ColaPrioridadTAD()
        cp_inicializar(self._cola)

    def encolar(self, dato: T, prioridad: int) -> None:
        cp_encolar(self._cola, int(dato), int(prioridad))

    def desencolar(self) -> T:
        valor_out: list[int] = []
        pri_out: list[int] = []
        ok = cp_desencolar(self._cola, valor_out, pri_out)
        if not ok:
            raise EstructuraVaciaError("La cola de prioridad esta vacia.")
        return valor_out[0]  # type: ignore[return-value]

    def frente(self) -> T:
        if cp_vacia(self._cola):
            raise EstructuraVaciaError("La cola de prioridad esta vacia.")
        valores: list[int] = []
        prioridades: list[int] = []
        cp_copiar_items(self._cola, valores, prioridades, 1)
        return valores[0]  # type: ignore[return-value]

    def vacia(self) -> bool:
        return cp_vacia(self._cola)

    def tamano(self) -> int:
        return cp_contar(self._cola)

    def limpiar(self) -> None:
        cp_vaciar(self._cola)

    def a_lista(self) -> list[tuple[T, int]]:
        capacidad = max(1, self.tamano())
        valores: list[int] = []
        prioridades: list[int] = []
        usados = cp_copiar_items(self._cola, valores, prioridades, capacidad)
        return [(valores[i], prioridades[i]) for i in range(usados)]  # type: ignore[list-item]

    def __len__(self) -> int:
        return self.tamano()

    def __repr__(self) -> str:
        return f"ColaPrioridad({self.a_lista()!r})"


class ListaCircular(Generic[T]):
    """Lista circular envuelta sobre `tad_lista_circular`."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._lista = ListaCircularTAD()
        lcir_inicializar(self._lista)
        if valores is not None:
            for valor in valores:
                self.insertar_final(valor)

    def insertar_inicio(self, dato: T) -> None:
        lcir_insertar_inicio(self._lista, int(dato))

    def insertar_final(self, dato: T) -> None:
        lcir_insertar_final(self._lista, int(dato))

    def eliminar_inicio(self) -> T:
        if lcir_vacia(self._lista):
            raise EstructuraVaciaError("La lista circular esta vacia.")
        head = self._lista.cabeza.valor
        if not lcir_eliminar_primero(self._lista, head):
            raise EstructuraVaciaError("No se pudo eliminar el inicio.")
        return head  # type: ignore[return-value]

    def eliminar_primero(self, dato: T) -> bool:
        return lcir_eliminar_primero(self._lista, int(dato))

    def buscar_posiciones(self, dato: T) -> list[int]:
        capacidad = max(1, lcir_contar(self._lista))
        out: list[int] = []
        usados = lcir_buscar_posiciones(self._lista, int(dato), out, capacidad)
        return out[:usados]

    def invertir(self) -> None:
        lcir_invertir(self._lista)

    def limpiar(self) -> None:
        lcir_destruir(self._lista)

    def vacia(self) -> bool:
        return lcir_vacia(self._lista)

    def tamano(self) -> int:
        return lcir_contar(self._lista)

    def a_lista(self) -> list[T]:
        capacidad = max(1, self.tamano())
        out: list[int] = []
        usados = lcir_copiar_valores(self._lista, out, capacidad)
        return out[:usados]  # type: ignore[return-value]

    def __len__(self) -> int:
        return self.tamano()

    def __iter__(self) -> Iterator[T]:
        return iter(self.a_lista())

    def __repr__(self) -> str:
        return f"ListaCircular({self.a_lista()!r})"


class ListaEnlazada(Generic[T]):
    """Lista enlazada sobre `tad_lista` y utilidades didacticas de UI."""

    def __init__(self, valores: Iterator[T] | None = None) -> None:
        self._cabeza: Tlista = None
        self._cola: NodoLista | None = None
        self._tamano = 0
        if valores is not None:
            for valor in valores:
                self.insertar_final(valor)

    def insertar_inicio(self, dato: T) -> None:
        ref = [self._cabeza]
        lista_insertar_inicio(ref, int(dato))
        self._cabeza = ref[0]
        self._recalcular_metadata()

    def insertar_final(self, dato: T) -> None:
        ref = [self._cabeza]
        lista_insertar_final(ref, int(dato))
        self._cabeza = ref[0]
        self._recalcular_metadata()

    def insertar_elemento(self, posicion: int, dato: T, desplazamiento: int = 0) -> bool:
        ref = [self._cabeza]
        before = self.a_lista()
        lista_configurar_insertar_antes_despues_provider(lambda: -1 if desplazamiento < 0 else 0)
        lista_insertar_elemento(ref, int(dato), int(posicion))
        self._cabeza = ref[0]
        self._recalcular_metadata()
        return self.a_lista() != before

    def insertar_posicion(self, posicion: int, dato: T) -> None:
        if posicion < 0 or posicion > self._tamano:
            raise PosicionInvalidaError("La posicion esta fuera de rango.")
        if posicion == 0:
            self.insertar_inicio(dato)
            return
        if posicion == self._tamano:
            self.insertar_final(dato)
            return
        anterior = self._nodo_en(posicion - 1)
        anterior.sgte = NodoLista(nro=int(dato), sgte=anterior.sgte)
        self._tamano += 1

    def eliminar_inicio(self) -> T:
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista esta vacia.")
        valor = self._cabeza.nro
        self._cabeza = self._cabeza.sgte
        self._tamano -= 1
        if self._tamano == 0:
            self._cola = None
        return valor  # type: ignore[return-value]

    def eliminar_final(self) -> T:
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista esta vacia.")
        if self._cabeza is self._cola:
            return self.eliminar_inicio()
        actual = self._cabeza
        while actual.sgte is not self._cola:
            actual = actual.sgte
        valor = self._cola.nro
        actual.sgte = None
        self._cola = actual
        self._tamano -= 1
        return valor  # type: ignore[return-value]

    def eliminar_posicion(self, posicion: int) -> T:
        if posicion < 0 or posicion >= self._tamano:
            raise PosicionInvalidaError("La posicion esta fuera de rango.")
        if posicion == 0:
            return self.eliminar_inicio()
        anterior = self._nodo_en(posicion - 1)
        objetivo = anterior.sgte
        anterior.sgte = objetivo.sgte
        if objetivo is self._cola:
            self._cola = anterior
        self._tamano -= 1
        return objetivo.nro  # type: ignore[return-value]

    def eliminar_primero(self, dato: T) -> bool:
        return self.eliminar_elemento(dato)

    def eliminar_elemento(self, dato: T) -> bool:
        ref = [self._cabeza]
        before = self.a_lista()
        lista_eliminar_elemento(ref, int(dato))
        self._cabeza = ref[0]
        self._recalcular_metadata()
        return self.a_lista() != before

    def eliminar_repetidos(self, dato: T) -> int:
        ref = [self._cabeza]
        before = self.a_lista()
        lista_eliminar_repetidos(ref, int(dato))
        self._cabeza = ref[0]
        self._recalcular_metadata()
        return len(before) - self._tamano

    def buscar_posiciones(self, dato: T) -> list[int]:
        posiciones_base_1 = lista_buscar_posiciones(self._cabeza, int(dato))
        return [pos - 1 for pos in posiciones_base_1]

    def buscar_elemento(self, dato: T) -> list[int]:
        return lista_buscar_posiciones(self._cabeza, int(dato))

    def mostrar(self) -> list[int]:
        return self.a_lista()

    def invertir(self) -> None:
        previo = None
        actual = self._cabeza
        self._cola = self._cabeza
        while actual is not None:
            siguiente = actual.sgte
            actual.sgte = previo
            previo = actual
            actual = siguiente
        self._cabeza = previo

    def primero(self) -> T:
        if self._cabeza is None:
            raise EstructuraVaciaError("La lista esta vacia.")
        return self._cabeza.nro  # type: ignore[return-value]

    def ultimo(self) -> T:
        if self._cola is None:
            raise EstructuraVaciaError("La lista esta vacia.")
        return self._cola.nro  # type: ignore[return-value]

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

    def _nodo_en(self, posicion: int) -> NodoLista:
        if posicion < 0 or posicion >= self._tamano:
            raise PosicionInvalidaError("La posicion esta fuera de rango.")
        actual = self._cabeza
        for _ in range(posicion):
            actual = actual.sgte
        return actual

    def _recalcular_metadata(self) -> None:
        actual = self._cabeza
        self._tamano = 0
        self._cola = None
        while actual is not None:
            self._tamano += 1
            self._cola = actual
            actual = actual.sgte

    def __iter__(self) -> Iterator[T]:
        actual = self._cabeza
        while actual is not None:
            yield actual.nro  # type: ignore[misc]
            actual = actual.sgte

    def __len__(self) -> int:
        return self._tamano

    def __contains__(self, dato: object) -> bool:
        return any(item == dato for item in self)

    def __repr__(self) -> str:
        return f"ListaEnlazada({self.a_lista()!r})"


class MonticuloBinario(Generic[T]):
    """Monticulo compatible: usa TAD para enteros y fallback generico opcional."""

    def __init__(
        self,
        valores: Iterator[T] | None = None,
        *,
        prioridad: Callable[[T], object] | None = None,
        min_heap: bool = True,
    ) -> None:
        self._prioridad = prioridad if prioridad is not None else (lambda x: x)
        self._min_heap = min_heap
        self._use_tad = prioridad is None
        self._py_datos: list[T] = []
        self._m = MonticuloTAD()
        monticulo_inicializar(self._m, MONTICULO_MIN if min_heap else MONTICULO_MAX, 16)
        if valores is not None:
            for valor in valores:
                self.insertar(valor)

    def insertar(self, dato: T) -> None:
        if self._use_tad:
            monticulo_insertar(self._m, int(dato))
            return
        self._py_datos.append(dato)
        self._subir_py(len(self._py_datos) - 1)

    def extraer_raiz(self) -> T:
        if self._use_tad:
            out: list[int] = []
            if not monticulo_extraer_raiz(self._m, out):
                raise EstructuraVaciaError("El monticulo esta vacio.")
            return out[0]  # type: ignore[return-value]
        if not self._py_datos:
            raise EstructuraVaciaError("El monticulo esta vacio.")
        raiz = self._py_datos[0]
        ultimo = self._py_datos.pop()
        if self._py_datos:
            self._py_datos[0] = ultimo
            self._bajar_py(0)
        return raiz

    def raiz(self) -> T:
        if self._use_tad:
            out: list[int] = []
            if not monticulo_raiz(self._m, out):
                raise EstructuraVaciaError("El monticulo esta vacio.")
            return out[0]  # type: ignore[return-value]
        if not self._py_datos:
            raise EstructuraVaciaError("El monticulo esta vacio.")
        return self._py_datos[0]

    def vacio(self) -> bool:
        return monticulo_vacio(self._m) if self._use_tad else not self._py_datos

    def tamano(self) -> int:
        return monticulo_cantidad(self._m) if self._use_tad else len(self._py_datos)

    def limpiar(self) -> None:
        if self._use_tad:
            tipo = self._m.tipo
            monticulo_destruir(self._m)
            monticulo_inicializar(self._m, tipo, 16)
            return
        self._py_datos.clear()

    def a_lista(self) -> list[T]:
        return list(self._m.datos) if self._use_tad else list(self._py_datos)  # type: ignore[return-value]

    def __len__(self) -> int:
        return self.tamano()

    def __iter__(self):
        return iter(self.a_lista())

    def __repr__(self) -> str:
        return f"MonticuloBinario({self.a_lista()!r})"

    def _antes_py(self, a: T, b: T) -> bool:
        pa = self._prioridad(a)
        pb = self._prioridad(b)
        return pa < pb if self._min_heap else pa > pb

    def _subir_py(self, idx: int) -> None:
        while idx > 0:
            padre = (idx - 1) // 2
            if not self._antes_py(self._py_datos[idx], self._py_datos[padre]):
                break
            self._py_datos[idx], self._py_datos[padre] = self._py_datos[padre], self._py_datos[idx]
            idx = padre

    def _bajar_py(self, idx: int) -> None:
        n = len(self._py_datos)
        while True:
            izq = 2 * idx + 1
            der = 2 * idx + 2
            mejor = idx
            if izq < n and self._antes_py(self._py_datos[izq], self._py_datos[mejor]):
                mejor = izq
            if der < n and self._antes_py(self._py_datos[der], self._py_datos[mejor]):
                mejor = der
            if mejor == idx:
                break
            self._py_datos[idx], self._py_datos[mejor] = self._py_datos[mejor], self._py_datos[idx]
            idx = mejor


@dataclass(slots=True)
class NodoPadre(Generic[T]):
    dato: T
    hijos: list[T]


class Sublista(Generic[T]):
    """Lista de padres con sublistas de hijos."""

    def __init__(self) -> None:
        self._lista_ref: list[NodoSublistaTAD | None] = [None]
        sublista_inicializar(self._lista_ref)

    def insertar_padre(self, dato: T) -> None:
        sublista_insertar_padre_final(self._lista_ref, int(dato))

    def buscar_padre(self, dato: T) -> NodoPadre[T] | None:
        nodo = sublista_buscar_padre(self._lista_ref[0], int(dato))
        if nodo is None:
            return None
        hijos = self.hijos_de(dato)
        return NodoPadre(dato=nodo.nro, hijos=hijos)  # type: ignore[arg-type]

    def insertar_hijo(self, padre: T, hijo: T) -> None:
        nodo_padre = sublista_buscar_padre(self._lista_ref[0], int(padre))
        if nodo_padre is None:
            raise ElementoNoEncontradoError(f"El padre {padre!r} no existe.")
        sublista_insertar_hijo_final(nodo_padre, int(hijo))

    def eliminar_hijo(self, padre: T, hijo: T) -> bool:
        nodo_padre = sublista_buscar_padre(self._lista_ref[0], int(padre))
        if nodo_padre is None:
            raise ElementoNoEncontradoError(f"El padre {padre!r} no existe.")
        return sublista_eliminar_hijo_primero(nodo_padre, int(hijo))

    def eliminar_padre(self, dato: T) -> bool:
        return sublista_eliminar_padre_primero(self._lista_ref, int(dato))

    def hijos_de(self, padre: T) -> list[T]:
        nodo_padre = sublista_buscar_padre(self._lista_ref[0], int(padre))
        if nodo_padre is None:
            raise ElementoNoEncontradoError(f"El padre {padre!r} no existe.")
        out: list[int] = []
        usados = sublista_copiar_hijos(nodo_padre, out, 1024)
        return out[:usados]  # type: ignore[return-value]

    def a_diccionario(self) -> dict[T, list[T]]:
        resultado: dict[T, list[T]] = {}
        actual = self._lista_ref[0]
        while actual is not None:
            out: list[int] = []
            usados = sublista_copiar_hijos(actual, out, 1024)
            resultado[actual.nro] = out[:usados]  # type: ignore[index]
            actual = actual.sgte
        return resultado

    def limpiar(self) -> None:
        self._lista_ref[0] = None

    def __repr__(self) -> str:
        return f"Sublista({self.a_diccionario()!r})"
