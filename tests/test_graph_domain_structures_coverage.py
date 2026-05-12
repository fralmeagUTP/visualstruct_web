"""Coverage-focused tests for internal graph helper structures."""

from __future__ import annotations

import pytest

from app.domain.graph.exceptions import EstructuraVaciaError, PosicionInvalidaError
from app.domain.graph.lista_enlazada import ListaEnlazada
from app.domain.graph.monticulo_binario import MonticuloBinario


def test_graph_linked_list_full_lifecycle_and_contract() -> None:
    """Linked list helper should support insert/delete/search/reverse workflows."""
    lista = ListaEnlazada([2, 3])

    lista.insertar_inicio(1)
    lista.insertar_final(4)
    lista.insertar_posicion(2, 99)

    assert lista.a_lista() == [1, 2, 99, 3, 4]
    assert lista.buscar_posiciones(2) == [1]
    assert lista.buscar_posiciones(7) == []
    assert lista.primero() == 1
    assert lista.ultimo() == 4
    assert 99 in lista
    assert list(iter(lista)) == [1, 2, 99, 3, 4]
    assert len(lista) == 5
    assert "ListaEnlazada(" in repr(lista)

    assert lista.eliminar_posicion(2) == 99
    assert lista.eliminar_inicio() == 1
    assert lista.eliminar_final() == 4
    assert lista.eliminar_primero(3) is True
    assert lista.eliminar_primero(777) is False

    assert lista.a_lista() == [2]

    lista.invertir()
    assert lista.a_lista() == [2]

    assert lista.eliminar_final() == 2
    assert lista.vacia() is True
    assert lista.tamano() == 0

    lista.limpiar()
    assert lista.a_lista() == []


def test_graph_linked_list_invalid_positions_and_empty_errors() -> None:
    """Linked list helper should raise didactic exceptions on invalid access."""
    lista = ListaEnlazada[int]()

    with pytest.raises(PosicionInvalidaError):
        lista.insertar_posicion(-1, 1)
    with pytest.raises(PosicionInvalidaError):
        lista.insertar_posicion(1, 1)

    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_inicio()
    with pytest.raises(EstructuraVaciaError):
        lista.eliminar_final()
    with pytest.raises(EstructuraVaciaError):
        lista.primero()
    with pytest.raises(EstructuraVaciaError):
        lista.ultimo()

    lista.insertar_final(10)
    lista.insertar_final(20)

    with pytest.raises(PosicionInvalidaError):
        lista.eliminar_posicion(5)
    with pytest.raises(PosicionInvalidaError):
        lista.eliminar_posicion(-1)

    lista.eliminar_posicion(0)
    assert lista.a_lista() == [20]


def test_graph_linked_list_insert_at_edges_and_reverse_multiple() -> None:
    """Edge insertions should route through dedicated fast paths."""
    lista = ListaEnlazada[int]()

    lista.insertar_posicion(0, 10)
    lista.insertar_posicion(1, 30)
    lista.insertar_posicion(1, 20)

    assert lista.a_lista() == [10, 20, 30]

    lista.invertir()
    assert lista.a_lista() == [30, 20, 10]


def test_graph_heap_min_max_priority_and_empty_errors() -> None:
    """Graph heap helper should support min/max behavior and custom priorities."""
    min_heap = MonticuloBinario[int]([5, 2, 9])
    min_heap.insertar(1)

    assert min_heap.raiz() == 1
    assert min_heap.tamano() == 4
    assert min_heap.vacio() is False
    assert list(iter(min_heap))[0] == 1

    extracted = [min_heap.extraer_raiz(), min_heap.extraer_raiz()]
    assert extracted == [1, 2]

    max_heap = MonticuloBinario[int](min_heap=False)
    for value in [5, 2, 9, 1]:
        max_heap.insertar(value)
    assert max_heap.raiz() == 9

    weighted_heap = MonticuloBinario[dict[str, int]](
        prioridad=lambda item: item["weight"],
        min_heap=True,
    )
    weighted_heap.insertar({"id": 1, "weight": 8})
    weighted_heap.insertar({"id": 2, "weight": 3})
    assert weighted_heap.extraer_raiz()["id"] == 2

    assert "MonticuloBinario(" in repr(weighted_heap)

    min_heap.limpiar()
    assert min_heap.vacio() is True

    with pytest.raises(EstructuraVaciaError):
        min_heap.raiz()
    with pytest.raises(EstructuraVaciaError):
        min_heap.extraer_raiz()

