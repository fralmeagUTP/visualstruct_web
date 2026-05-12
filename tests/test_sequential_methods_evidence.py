"""Evidence-oriented tests for sequential TAD method correctness."""

from __future__ import annotations

import pytest

from app.domain.sequential import (
    Cola,
    ColaPrioridad,
    ElementoNoEncontradoError,
    EstructuraVaciaError,
    ListaCircular,
    ListaEnlazada,
    Pila,
    Sublista,
)
from app.domain.sequential.exceptions import PosicionInvalidaError


def test_lista_enlazada_metodos_consistentes() -> None:
    lista = ListaEnlazada[int]()
    lista.insertar_inicio(2)
    lista.insertar_final(4)
    lista.insertar_posicion(1, 3)
    lista.insertar_posicion(0, 1)

    assert list(lista) == [1, 2, 3, 4]
    assert 3 in lista
    assert lista.primero() == 1
    assert lista.ultimo() == 4
    assert lista.buscar_posiciones(3) == [2]

    assert lista.eliminar_posicion(1) == 2
    assert lista.eliminar_primero(3) is True
    assert lista.eliminar_primero(99) is False
    assert lista.a_lista() == [1, 4]

    lista.invertir()
    assert lista.a_lista() == [4, 1]
    assert len(lista) == 2


def test_lista_enlazada_errores_metodos() -> None:
    lista = ListaEnlazada[int]()
    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_inicio()
    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_final()
    with pytest.raises(PosicionInvalidaError):
        lista.insertar_posicion(-1, 7)
    with pytest.raises(PosicionInvalidaError):
        lista.eliminar_posicion(0)


def test_pila_alias_y_lifo() -> None:
    pila = Pila[int]()
    pila.push(10)
    pila.apilar(20)
    pila.push(30)

    assert pila.peek() == 30
    assert pila.pop() == 30
    assert pila.desapilar() == 20
    assert pila.cima() == 10
    assert pila.a_lista() == [10]
    assert len(pila) == 1


def test_cola_alias_y_fifo() -> None:
    cola = Cola[int]()
    cola.enqueue(10)
    cola.encolar(20)
    cola.enqueue(30)

    assert cola.frente() == 10
    assert cola.final() == 30
    assert cola.dequeue() == 10
    assert cola.desencolar() == 20
    assert cola.a_lista() == [30]
    assert len(cola) == 1


def test_cola_prioridad_prioridad_estable_y_limpiar() -> None:
    cp = ColaPrioridad[int]()
    cp.encolar(50, 5)
    cp.encolar(10, 1)
    cp.encolar(20, 1)
    cp.encolar(30, 3)

    assert cp.frente() == 10
    assert cp.desencolar() == 10
    assert cp.desencolar() == 20
    assert cp.desencolar() == 30
    assert cp.desencolar() == 50

    cp.encolar(99, 9)
    assert cp.tamano() == 1
    cp.limpiar()
    assert cp.vacia() is True


def test_cola_prioridad_errores_en_vacio() -> None:
    cp = ColaPrioridad[int]()
    with pytest.raises(EstructuraVaciaError):
        cp.frente()
    with pytest.raises(EstructuraVaciaError):
        cp.desencolar()


def test_lista_circular_metodos_consistentes() -> None:
    lista = ListaCircular[int]()
    lista.insertar_inicio(2)
    lista.insertar_inicio(1)
    lista.insertar_final(3)
    lista.insertar_final(2)

    assert lista.a_lista() == [1, 2, 3, 2]
    assert lista.buscar_posiciones(2) == [1, 3]
    assert lista.eliminar_primero(2) is True
    assert lista.a_lista() == [1, 3, 2]
    assert lista.eliminar_inicio() == 1
    assert lista.a_lista() == [3, 2]

    lista.invertir()
    assert lista.a_lista() == [2, 3]
    assert len(lista) == 2


def test_lista_circular_error_en_vacio() -> None:
    lista = ListaCircular[int]()
    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_inicio()


def test_sublista_metodos_padres_hijos() -> None:
    sub = Sublista[int]()
    sub.insertar_padre(1)
    sub.insertar_padre(2)
    sub.insertar_hijo(1, 10)
    sub.insertar_hijo(1, 20)
    sub.insertar_hijo(2, 30)

    assert sub.buscar_padre(1) is not None
    assert sub.hijos_de(1) == [10, 20]
    assert sub.eliminar_hijo(1, 10) is True
    assert sub.eliminar_hijo(1, 99) is False
    assert sub.hijos_de(1) == [20]
    assert sub.eliminar_padre(2) is True
    assert sub.a_diccionario() == {1: [20]}


def test_sublista_errores_padre_inexistente() -> None:
    sub = Sublista[int]()
    with pytest.raises(ElementoNoEncontradoError):
        sub.insertar_hijo(99, 1)
    with pytest.raises(ElementoNoEncontradoError):
        sub.eliminar_hijo(99, 1)
    with pytest.raises(ElementoNoEncontradoError):
        sub.hijos_de(99)
