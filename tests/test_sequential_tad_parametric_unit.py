"""Parametric unit tests for low-level sequential `tad_*` modules."""

from __future__ import annotations

import pytest

from app.domain.sequential.tad_cola import Cola, cola_desencolar, cola_encolar, cola_frente, cola_mostrar, cola_vaciar
from app.domain.sequential.tad_cola_prioridad import (
    ColaPrioridad,
    cp_contar,
    cp_copiar_items,
    cp_desencolar,
    cp_encolar,
    cp_formatear,
    cp_inicializar,
    cp_vacia,
    cp_vaciar,
)
from app.domain.sequential.tad_lista import (
    Tlista,
    lista_buscar_elemento,
    lista_buscar_posiciones,
    lista_configurar_insertar_antes_despues_provider,
    lista_eliminar_elemento,
    lista_eliminar_repetidos,
    lista_insertar_elemento,
    lista_insertar_final,
    lista_insertar_inicio,
    lista_mostrar,
)
from app.domain.sequential.tad_lista_circular import (
    ListaCircular,
    lcir_buscar_posiciones,
    lcir_contar,
    lcir_copiar_valores,
    lcir_destruir,
    lcir_eliminar_primero,
    lcir_formatear,
    lcir_inicializar,
    lcir_insertar_final,
    lcir_insertar_inicio,
    lcir_invertir,
    lcir_vacia,
)
from app.domain.sequential.tad_monticulo_binario import (
    MONTICULO_MAX,
    MONTICULO_MIN,
    MonticuloBinario,
    monticulo_capacidad,
    monticulo_construir,
    monticulo_copiar_valores,
    monticulo_eliminar_valor,
    monticulo_extraer_raiz,
    monticulo_formatear_arbol,
    monticulo_formatear_arreglo,
    monticulo_inicializar,
    monticulo_insertar,
    monticulo_raiz,
    monticulo_vacio,
)
from app.domain.sequential.tad_pila import pila_apilar, pila_desapilar, pila_destruir, pila_mostrar
from app.domain.sequential.tad_sublista import (
    sublista_buscar_hijo,
    sublista_buscar_padre,
    sublista_contar_hijos,
    sublista_contar_padres,
    sublista_copiar_hijos,
    sublista_destruir,
    sublista_eliminar_hijo_primero,
    sublista_eliminar_padre_primero,
    sublista_formatear,
    sublista_inicializar,
    sublista_insertar_hijo_final,
    sublista_insertar_padre_final,
)


def _tlista_to_values(head: Tlista) -> list[int]:
    out: list[int] = []
    current = head
    while current is not None:
        out.append(current.nro)
        current = current.sgte
    return out


@pytest.mark.parametrize("values", [[1], [1, 2, 3], [7, 7, -1, 0]])
def test_tad_pila_push_pop_multiple_values(values: list[int]) -> None:
    ref = [None]
    for value in values:
        pila_apilar(ref, value)
    out = [pila_desapilar(ref) for _ in values]
    assert out == list(reversed(values))
    assert pila_desapilar(ref) == -1
    pila_destruir(ref)
    assert ref[0] is None


def test_tad_pila_mostrar_prints(capsys: pytest.CaptureFixture[str]) -> None:
    ref = [None]
    pila_mostrar(ref[0])
    assert "(vacia)" in capsys.readouterr().out
    pila_apilar(ref, 10)
    pila_apilar(ref, 20)
    pila_mostrar(ref[0])
    assert "20 -> 10" in capsys.readouterr().out


@pytest.mark.parametrize("values", [[5], [5, 6, 7], [1, 1, 2, 3]])
def test_tad_cola_enqueue_dequeue_multiple_values(values: list[int]) -> None:
    queue = Cola()
    for value in values:
        cola_encolar(queue, value)
    assert cola_frente(queue) == values[0]
    out = [cola_desencolar(queue) for _ in values]
    assert out == values
    assert cola_desencolar(queue) == -1
    cola_vaciar(queue)
    assert cola_frente(queue) == -1


def test_tad_cola_mostrar_prints(capsys: pytest.CaptureFixture[str]) -> None:
    queue = Cola()
    cola_mostrar(queue)
    assert "(vacia)" in capsys.readouterr().out
    cola_encolar(queue, 1)
    cola_encolar(queue, 2)
    cola_mostrar(queue)
    assert "1 <- 2" in capsys.readouterr().out


def test_tad_lista_insertar_elemento_provider_variants() -> None:
    lista_ref = [None]
    for value in (10, 20, 30):
        lista_insertar_final(lista_ref, value)

    lista_configurar_insertar_antes_despues_provider(lambda: 0)
    lista_insertar_elemento(lista_ref, 99, 2)
    assert _tlista_to_values(lista_ref[0]) == [10, 20, 99, 30]

    lista_configurar_insertar_antes_despues_provider(lambda: -1)
    lista_insertar_elemento(lista_ref, 77, 2)
    assert _tlista_to_values(lista_ref[0]) == [10, 77, 20, 99, 30]

    lista_configurar_insertar_antes_despues_provider(lambda: 999)
    assert lista_configurar_insertar_antes_despues_provider is not None


def test_tad_lista_insertar_y_busqueda_imprime(capsys: pytest.CaptureFixture[str]) -> None:
    lista_ref = [None]
    lista_insertar_inicio(lista_ref, 5)
    lista_insertar_final(lista_ref, 9)
    lista_insertar_final(lista_ref, 5)
    lista_buscar_elemento(lista_ref[0], 5)
    out = capsys.readouterr().out.lower()
    assert "posicion 1" in out
    assert "posicion 3" in out
    assert lista_buscar_posiciones(lista_ref[0], 5) == [1, 3]


def test_tad_lista_mostrar_eliminar_variants(capsys: pytest.CaptureFixture[str]) -> None:
    lista_ref = [None]
    for value in (1, 2, 2, 3):
        lista_insertar_final(lista_ref, value)
    lista_mostrar(lista_ref[0])
    assert "1) 1" in capsys.readouterr().out

    lista_eliminar_elemento(lista_ref, 2)
    assert _tlista_to_values(lista_ref[0]) == [1, 2, 3]
    lista_eliminar_repetidos(lista_ref, 2)
    assert _tlista_to_values(lista_ref[0]) == [1, 3]

    lista_eliminar_elemento(lista_ref, 999)
    assert "no encontrado" in capsys.readouterr().out.lower()


@pytest.mark.parametrize("values,target,expected", [([1, 2, 1], 1, [0, 2]), ([9], 7, []), ([4, 4, 4], 4, [0, 1, 2])])
def test_tad_lista_circular_buscar_posiciones(values: list[int], target: int, expected: list[int]) -> None:
    lista = ListaCircular()
    lcir_inicializar(lista)
    for value in values:
        lcir_insertar_final(lista, value)
    out: list[int] = []
    used = lcir_buscar_posiciones(lista, target, out, 32)
    assert out[:used] == expected


def test_tad_lista_circular_mutation_and_formatting() -> None:
    lista = ListaCircular()
    lcir_inicializar(lista)
    lcir_insertar_inicio(lista, 2)
    lcir_insertar_inicio(lista, 1)
    lcir_insertar_final(lista, 3)
    assert lcir_contar(lista) == 3
    assert lcir_eliminar_primero(lista, 1) is True
    lcir_invertir(lista)
    values: list[int] = []
    copied = lcir_copiar_valores(lista, values, 10)
    assert values[:copied] == [3, 2]
    text: list[str] = []
    lcir_formatear(lista, text, 128)
    assert "HEAD" in text[0]
    lcir_destruir(lista)
    assert lcir_vacia(lista) is True


@pytest.mark.parametrize(
    ("items", "expected_order"),
    [
        ([(10, 2), (20, 1), (30, 3)], [20, 10, 30]),
        ([(5, 1), (6, 1), (7, 1)], [5, 6, 7]),
    ],
)
def test_tad_cola_prioridad_order_and_dequeue(items: list[tuple[int, int]], expected_order: list[int]) -> None:
    queue = ColaPrioridad()
    cp_inicializar(queue)
    for value, priority in items:
        cp_encolar(queue, value, priority)
    out: list[int] = []
    for _ in items:
        value_out: list[int] = []
        pri_out: list[int] = []
        assert cp_desencolar(queue, value_out, pri_out) is True
        out.append(value_out[0])
    assert out == expected_order
    assert cp_desencolar(queue, [], []) is False
    assert cp_vacia(queue) is True


def test_tad_cola_prioridad_copy_and_format() -> None:
    queue = ColaPrioridad()
    cp_inicializar(queue)
    cp_encolar(queue, 11, 2)
    cp_encolar(queue, 22, 1)
    values = [0, 0]
    priorities = [0, 0]
    used = cp_copiar_items(queue, values, priorities, 2)
    assert used == 2
    assert values == [11, 22]
    assert priorities == [2, 1]
    text: list[str] = []
    cp_formatear(queue, text, 120)
    assert "[0]=11" in text[0]
    cp_vaciar(queue)
    assert cp_contar(queue) == 0


def test_tad_sublista_parent_child_branches() -> None:
    lista_ref = [None]
    sublista_inicializar(lista_ref)
    p1 = sublista_insertar_padre_final(lista_ref, 1)
    sublista_insertar_padre_final(lista_ref, 2)
    assert sublista_contar_padres(lista_ref[0]) == 2
    assert sublista_buscar_padre(lista_ref[0], 1) is p1
    assert sublista_insertar_hijo_final(p1, 10) is True
    assert sublista_insertar_hijo_final(p1, 20) is True
    assert sublista_contar_hijos(p1) == 2
    assert sublista_buscar_hijo(p1.sub, 20) is not None
    assert sublista_eliminar_hijo_primero(p1, 10) is True
    assert sublista_eliminar_hijo_primero(p1, 999) is False
    assert sublista_eliminar_padre_primero(lista_ref, 2) is True
    assert sublista_eliminar_padre_primero(lista_ref, 999) is False

    out: list[int] = []
    copied = sublista_copiar_hijos(p1, out, 10)
    assert copied == 1
    assert out == [20]
    text: list[str] = []
    sublista_formatear(lista_ref[0], text, 120)
    assert "1:" in text[0]
    sublista_destruir(lista_ref)
    assert lista_ref[0] is None


def test_tad_sublista_copy_invalid_targets() -> None:
    assert sublista_copiar_hijos(None, [], 10) == 0
    lista_ref = [None]
    sublista_inicializar(lista_ref)
    parent = sublista_insertar_padre_final(lista_ref, 3)
    sublista_insertar_hijo_final(parent, 9)
    assert sublista_copiar_hijos(parent, None, 10) == 0
    assert sublista_copiar_hijos(parent, [], 0) == 0


@pytest.mark.parametrize("values", [[9, 4, 7], [5], [8, 1, 6, 2]])
def test_tad_monticulo_min_heap_basic(values: list[int]) -> None:
    heap = MonticuloBinario()
    monticulo_inicializar(heap, MONTICULO_MIN, 1)
    for value in values:
        assert monticulo_insertar(heap, value) is True
    root_out: list[int] = []
    assert monticulo_raiz(heap, root_out) is True
    assert root_out[0] == min(values)
    assert monticulo_capacidad(heap) >= len(values)

    extracted: list[int] = []
    while not monticulo_vacio(heap):
        out: list[int] = []
        assert monticulo_extraer_raiz(heap, out) is True
        extracted.append(out[0])
    assert extracted == sorted(values)


def test_tad_monticulo_build_copy_delete_and_format() -> None:
    heap = MonticuloBinario()
    monticulo_inicializar(heap, MONTICULO_MAX, 0)
    assert monticulo_construir(heap, [1, 9, 3, 7], 4) is True
    out_vals = [0, 0, 0, 0]
    used = monticulo_copiar_valores(heap, out_vals, 4)
    assert used == 4
    assert monticulo_eliminar_valor(heap, 9) is True
    assert monticulo_eliminar_valor(heap, 999) is False
    arr_text: list[str] = []
    tree_text: list[str] = []
    monticulo_formatear_arreglo(heap, arr_text, 128)
    monticulo_formatear_arbol(heap, tree_text, 128)
    assert arr_text
    assert tree_text
