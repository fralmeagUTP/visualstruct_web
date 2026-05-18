"""Coverage-focused tests for graph TAD aliases (sin wrappers legacy)."""

from __future__ import annotations

from app.domain.graph.tad_lista import NodoLista, lista_buscar_posiciones, lista_configurar_insertar_antes_despues_provider, lista_eliminar_elemento, lista_eliminar_repetidos, lista_insertar_elemento, lista_insertar_final, lista_insertar_inicio
from app.domain.graph.tad_monticulo_binario import MONTICULO_MAX, MONTICULO_MIN, MonticuloBinario, monticulo_cantidad, monticulo_construir, monticulo_destruir, monticulo_eliminar_valor, monticulo_extraer_raiz, monticulo_inicializar, monticulo_insertar, monticulo_raiz, monticulo_vacio


def _to_list(head: NodoLista | None) -> list[int]:
    out: list[int] = []
    cur = head
    while cur is not None:
        out.append(cur.nro)
        cur = cur.sgte
    return out


def test_graph_tad_lista_insert_search_delete_contract() -> None:
    lista_ref = [None]
    lista_insertar_inicio(lista_ref, 2)
    lista_insertar_final(lista_ref, 4)
    lista_configurar_insertar_antes_despues_provider(lambda: -1)
    lista_insertar_elemento(lista_ref, 3, 2)
    lista_insertar_inicio(lista_ref, 1)

    assert _to_list(lista_ref[0]) == [1, 2, 3, 4]
    assert lista_buscar_posiciones(lista_ref[0], 3) == [3]

    lista_eliminar_elemento(lista_ref, 3)
    assert _to_list(lista_ref[0]) == [1, 2, 4]


def test_graph_tad_lista_eliminar_repetidos_contract() -> None:
    lista_ref = [None]
    for value in [5, 3, 5, 7, 5]:
        lista_insertar_final(lista_ref, value)

    lista_eliminar_repetidos(lista_ref, 5)
    assert _to_list(lista_ref[0]) == [3, 7]


def test_graph_tad_monticulo_min_insert_root_extract_contract() -> None:
    heap = MonticuloBinario()
    monticulo_inicializar(heap, MONTICULO_MIN, 2)

    for value in [5, 2, 9, 1]:
        assert monticulo_insertar(heap, value) is True

    root_out: list[int] = []
    assert monticulo_raiz(heap, root_out) is True
    assert root_out[0] == 1

    extraido: list[int] = []
    assert monticulo_extraer_raiz(heap, extraido) is True
    assert extraido[0] == 1
    assert monticulo_cantidad(heap) == 3
    assert monticulo_vacio(heap) is False


def test_graph_tad_monticulo_max_build_remove_destroy_contract() -> None:
    heap = MonticuloBinario()
    monticulo_inicializar(heap, MONTICULO_MAX, 1)
    assert monticulo_construir(heap, [5, 2, 9, 1], 4) is True

    root_out: list[int] = []
    assert monticulo_raiz(heap, root_out) is True
    assert root_out[0] == 9

    assert monticulo_eliminar_valor(heap, 9) is True
    root_out = []
    assert monticulo_raiz(heap, root_out) is True
    assert root_out[0] == 5

    monticulo_destruir(heap)
    assert monticulo_vacio(heap) is True
