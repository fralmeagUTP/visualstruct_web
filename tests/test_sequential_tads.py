"""Behavioral tests for core sequential TAD implementations."""

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


def test_lista_enlazada_operaciones_principales() -> None:
    """La lista enlazada debe mantener orden, posiciones y operaciones basicas."""
    lista = ListaEnlazada[int]()

    lista.insertar_inicio(20)
    lista.insertar_final(40)
    lista.insertar_posicion(1, 30)
    lista.insertar_posicion(0, 10)
    lista.insertar_final(30)

    assert lista.a_lista() == [10, 20, 30, 40, 30]
    assert lista.primero() == 10
    assert lista.ultimo() == 30
    assert lista.buscar_posiciones(30) == [2, 4]

    assert lista.eliminar_primero(30) is True
    assert lista.a_lista() == [10, 20, 40, 30]
    assert lista.eliminar_posicion(2) == 40
    assert lista.eliminar_final() == 30
    assert lista.eliminar_inicio() == 10
    assert lista.a_lista() == [20]

    lista.invertir()
    assert lista.a_lista() == [20]
    assert lista.tamano() == 1

    lista.limpiar()
    assert lista.vacia() is True
    assert lista.tamano() == 0


def test_lista_enlazada_errores_en_vacio_y_posicion() -> None:
    """La lista enlazada debe fallar con errores claros en casos invalidos."""
    lista = ListaEnlazada[int]()

    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_inicio()
    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_final()
    with pytest.raises(EstructuraVaciaError):
        lista.primero()
    with pytest.raises(EstructuraVaciaError):
        lista.ultimo()
    with pytest.raises(PosicionInvalidaError):
        lista.insertar_posicion(1, 99)
    with pytest.raises(PosicionInvalidaError):
        lista.eliminar_posicion(0)


def test_pila_comportamiento_lifo_y_limpiar() -> None:
    """La pila debe atender en orden LIFO y limpiar correctamente."""
    pila = Pila[int]([1, 2, 3])

    assert pila.a_lista() == [3, 2, 1]
    assert pila.cima() == 3
    assert pila.desapilar() == 3
    assert pila.desapilar() == 2
    assert pila.tamano() == 1

    pila.apilar(9)
    assert pila.cima() == 9
    assert pila.a_lista() == [9, 1]

    pila.limpiar()
    assert pila.vacia() is True
    assert pila.tamano() == 0

    with pytest.raises(EstructuraVaciaError):
        pila.desapilar()


def test_cola_comportamiento_fifo_y_extremos() -> None:
    """La cola debe conservar orden FIFO y exponer frente/final."""
    cola = Cola[int]([10, 20, 30])

    assert cola.a_lista() == [10, 20, 30]
    assert cola.frente() == 10
    assert cola.final() == 30
    assert cola.desencolar() == 10
    assert cola.desencolar() == 20

    cola.encolar(40)
    assert cola.a_lista() == [30, 40]
    assert cola.frente() == 30
    assert cola.final() == 40

    cola.limpiar()
    assert cola.vacia() is True
    assert cola.tamano() == 0

    with pytest.raises(EstructuraVaciaError):
        cola.desencolar()


def test_cola_prioridad_respeta_prioridad_y_estabilidad() -> None:
    """La cola de prioridad debe usar menor prioridad primero y estabilidad por llegada."""
    cola = ColaPrioridad[int]()
    cola.encolar(100, 3)
    cola.encolar(200, 1)
    cola.encolar(300, 1)
    cola.encolar(400, 2)

    assert cola.frente() == 200
    assert cola.desencolar() == 200
    assert cola.desencolar() == 300
    assert cola.desencolar() == 400
    assert cola.desencolar() == 100
    assert cola.vacia() is True

    with pytest.raises(EstructuraVaciaError):
        cola.frente()
    with pytest.raises(EstructuraVaciaError):
        cola.desencolar()


def test_lista_circular_operaciones_principales() -> None:
    """La lista circular debe mantener ciclo, orden y operaciones expuestas."""
    lista = ListaCircular[int]()
    lista.insertar_inicio(20)
    lista.insertar_final(30)
    lista.insertar_inicio(10)
    lista.insertar_final(30)

    assert lista.a_lista() == [10, 20, 30, 30]
    assert lista.buscar_posiciones(30) == [2, 3]

    assert lista.eliminar_primero(30) is True
    assert lista.a_lista() == [10, 20, 30]
    assert lista.eliminar_inicio() == 10
    assert lista.a_lista() == [20, 30]

    lista.invertir()
    assert lista.a_lista() == [30, 20]
    assert lista.tamano() == 2

    lista.limpiar()
    assert lista.vacia() is True
    assert lista.tamano() == 0


def test_lista_circular_errores_en_vacio() -> None:
    """La lista circular debe fallar en vacio para operaciones que requieren nodos."""
    lista = ListaCircular[int]()

    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_inicio()
    assert lista.eliminar_primero(1) is False


def test_sublista_operaciones_principales() -> None:
    """La sublista debe gestionar padres e hijos segun el contrato del TAD."""
    estructura = Sublista[int]()
    estructura.insertar_padre(1)
    estructura.insertar_padre(2)
    estructura.insertar_hijo(1, 10)
    estructura.insertar_hijo(1, 20)
    estructura.insertar_hijo(2, 30)

    assert estructura.hijos_de(1) == [10, 20]
    assert estructura.hijos_de(2) == [30]

    assert estructura.eliminar_hijo(1, 10) is True
    assert estructura.hijos_de(1) == [20]
    assert estructura.eliminar_hijo(1, 99) is False

    assert estructura.eliminar_padre(2) is True
    assert estructura.a_diccionario() == {1: [20]}

    estructura.limpiar()
    assert estructura.a_diccionario() == {}


def test_sublista_errores_de_padre_inexistente() -> None:
    """Sublista debe fallar didacticamente cuando el padre no existe."""
    estructura = Sublista[int]()

    with pytest.raises(ElementoNoEncontradoError):
        estructura.insertar_hijo(99, 1)
    with pytest.raises(ElementoNoEncontradoError):
        estructura.hijos_de(99)
    with pytest.raises(ElementoNoEncontradoError):
        estructura.eliminar_hijo(99, 1)
