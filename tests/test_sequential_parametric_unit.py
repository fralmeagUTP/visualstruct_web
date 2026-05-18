"""Parametric unit tests for sequential structures using multiple datasets."""

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


@pytest.mark.parametrize(
    ("values", "expected_pop_order"),
    [
        ([1], [1]),
        ([5, 3, 9], [9, 3, 5]),
        ([0, -2, 7, 7], [7, 7, -2, 0]),
    ],
)
def test_stack_lifo_multiple_datasets(values: list[int], expected_pop_order: list[int]) -> None:
    stack = Pila[int]()
    for value in values:
        stack.apilar(value)

    out = [stack.desapilar() for _ in range(len(values))]
    assert out == expected_pop_order
    assert stack.vacia() is True


@pytest.mark.parametrize(
    "values",
    [
        [1],
        [10, 20, 30],
        [4, 4, -1, 9],
    ],
)
def test_queue_fifo_multiple_datasets(values: list[int]) -> None:
    queue = Cola[int]()
    for value in values:
        queue.encolar(value)

    out = [queue.desencolar() for _ in range(len(values))]
    assert out == values
    assert queue.vacia() is True


@pytest.mark.parametrize(
    ("items", "expected_values"),
    [
        ([(10, 3), (20, 1), (30, 2)], [20, 30, 10]),
        ([(5, 1), (6, 1), (7, 1)], [5, 6, 7]),
        ([(1, 5), (2, 4), (3, 3), (4, 2), (5, 1)], [5, 4, 3, 2, 1]),
    ],
)
def test_priority_queue_order_multiple_datasets(
    items: list[tuple[int, int]],
    expected_values: list[int],
) -> None:
    pq = ColaPrioridad[int]()
    for value, priority in items:
        pq.encolar(value, priority)

    out = [pq.desencolar() for _ in range(len(items))]
    assert out == expected_values
    assert pq.vacia() is True


@pytest.mark.parametrize(
    ("base", "pos", "value", "expected"),
    [
        ([10, 20, 30], 1, 99, [99, 10, 20, 30]),
        ([10, 20, 30], 2, 99, [10, 20, 99, 30]),
        ([10, 20, 30], 3, 99, [10, 20, 30, 99]),
    ],
)
def test_linked_list_insertar_elemento_new_contract(
    base: list[int],
    pos: int,
    value: int,
    expected: list[int],
) -> None:
    linked = ListaEnlazada[int](base)
    changed = linked.insertar_elemento(pos, value)
    assert changed is True
    assert linked.a_lista() == expected


def test_linked_list_insertar_elemento_position_not_found_returns_false() -> None:
    linked = ListaEnlazada[int]([10, 20, 30])
    changed = linked.insertar_elemento(8, 99)
    assert changed is False
    assert linked.a_lista() == [10, 20, 30]


@pytest.mark.parametrize(
    ("values", "target", "expected_removed", "expected_after"),
    [
        ([1, 2, 2, 3], 2, 2, [1, 3]),
        ([5, 5, 5], 5, 3, []),
        ([7, 8, 9], 1, 0, [7, 8, 9]),
    ],
)
def test_linked_list_eliminar_repetidos_multiple_datasets(
    values: list[int],
    target: int,
    expected_removed: int,
    expected_after: list[int],
) -> None:
    linked = ListaEnlazada[int](values)
    removed = linked.eliminar_repetidos(target)
    assert removed == expected_removed
    assert linked.a_lista() == expected_after


@pytest.mark.parametrize(
    ("values", "target", "expected_positions"),
    [
        ([10, 20, 10, 30], 10, [0, 2]),
        ([1, 2, 3], 4, []),
        ([5, 5, 5, 5], 5, [0, 1, 2, 3]),
    ],
)
def test_circular_list_search_positions_multiple_datasets(
    values: list[int],
    target: int,
    expected_positions: list[int],
) -> None:
    circular = ListaCircular[int](values)
    assert circular.buscar_posiciones(target) == expected_positions


def test_sublist_parent_child_lifecycle_with_multiple_values() -> None:
    sub = Sublista[int]()
    for parent in (1, 2, 3):
        sub.insertar_padre(parent)
    for child in (10, 20, 30):
        sub.insertar_hijo(1, child)
    sub.insertar_hijo(2, 40)

    assert sub.hijos_de(1) == [10, 20, 30]
    assert sub.hijos_de(2) == [40]
    assert sub.eliminar_hijo(1, 20) is True
    assert sub.hijos_de(1) == [10, 30]
    assert sub.eliminar_padre(3) is True
    assert sub.a_diccionario() == {1: [10, 30], 2: [40]}


def test_sublist_raises_for_missing_parent_in_multiple_operations() -> None:
    sub = Sublista[int]()
    with pytest.raises(ElementoNoEncontradoError):
        sub.insertar_hijo(99, 1)
    with pytest.raises(ElementoNoEncontradoError):
        sub.hijos_de(99)
    with pytest.raises(ElementoNoEncontradoError):
        sub.eliminar_hijo(99, 1)


def test_pop_from_empty_stack_and_queue_raises_consistent_errors() -> None:
    stack = Pila[int]()
    queue = Cola[int]()
    with pytest.raises(EstructuraVaciaError):
        stack.desapilar()
    with pytest.raises(EstructuraVaciaError):
        queue.desencolar()
