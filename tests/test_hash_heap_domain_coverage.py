"""Boundary coverage for hash table and hierarchical binary heap domains."""

from __future__ import annotations

from app.domain.hash.tad_tabla_hash import (
    TablaHash,
    th_buscar,
    th_cantidad,
    th_capacidad,
    th_contiene,
    th_destruir,
    th_eliminar,
    th_estadisticas,
    th_formatear,
    th_formatear_estadisticas,
    th_indice,
    th_inicializar,
    th_insertar,
    th_vacia,
    th_vaciar,
)
from app.domain.hierarchical.tad_monticulo_binario import (
    MONTICULO_MAX,
    MONTICULO_MIN,
    MonticuloBinario,
    monticulo_cantidad,
    monticulo_capacidad,
    monticulo_construir,
    monticulo_copiar_valores,
    monticulo_destruir,
    monticulo_eliminar_valor,
    monticulo_extraer_raiz,
    monticulo_formatear_arbol,
    monticulo_formatear_arreglo,
    monticulo_inicializar,
    monticulo_insertar,
    monticulo_raiz,
    monticulo_vacio,
)


def test_hash_uninitialized_collision_update_search_and_delete_chain() -> None:
    table = TablaHash()
    assert th_indice(table, 5) == 0
    assert th_buscar(table, 5, []) is False
    assert th_eliminar(table, 5) is False
    assert th_vacia(table) is True

    # Lazy initialization uses capacity 17; keys form one collision chain.
    assert th_insertar(table, 1, 10) is True
    th_insertar(table, 18, 20)
    th_insertar(table, 35, 30)
    assert th_capacidad(table) == 17
    assert th_cantidad(table) == 3
    assert th_contiene(table, 18) is True
    assert th_contiene(table, 99) is False

    empty_out: list[int] = []
    assert th_buscar(table, 18, empty_out) is True
    assert empty_out == [20]
    existing_out = [0]
    assert th_buscar(table, 1, existing_out) is True
    assert existing_out == [10]

    th_insertar(table, 18, 200)
    assert th_buscar(table, 18, empty_out) is True
    assert empty_out == [200]

    # Remove a middle node and then the bucket head.
    assert th_eliminar(table, 18) is True
    assert th_eliminar(table, 35) is True
    assert th_eliminar(table, 999) is False
    assert th_cantidad(table) == 1


def test_hash_statistics_formatting_vaciar_and_destroy() -> None:
    table = TablaHash()
    th_inicializar(table, 0)
    assert th_capacidad(table) == 1
    for key in (1, 2, 3):
        th_insertar(table, key, key * 10)

    stats = th_estadisticas(table)
    assert stats.buckets_ocupados == 1
    assert stats.colisiones == 2
    assert stats.factor_carga == 3.0

    assert th_formatear(table, None, 80) is None
    assert th_formatear(table, [], 0) is None
    formatted: list[str] = []
    th_formatear(table, formatted, 80)
    assert "(3:30)" in formatted[0]
    replacement = ["old"]
    th_formatear(table, replacement, 8)
    assert replacement[0] != "old"

    stats_text: list[str] = []
    th_formatear_estadisticas(table, stats_text, 100)
    assert "colisiones=2" in stats_text[0]
    th_formatear_estadisticas(table, stats_text, 20)
    assert len(stats_text[0]) <= 19
    assert th_formatear_estadisticas(table, None, 10) is None
    assert th_formatear_estadisticas(table, [], 0) is None

    th_vaciar(table)
    assert th_vacia(table) is True
    th_vaciar(TablaHash())  # no-op for an uninitialized table
    th_destruir(table)
    assert th_capacidad(table) == 0
    assert th_estadisticas(table).factor_carga == 0.0


def test_min_heap_growth_outputs_copy_and_formatting_boundaries() -> None:
    heap = MonticuloBinario()
    monticulo_inicializar(heap, MONTICULO_MIN, 0)
    assert monticulo_raiz(heap, []) is False
    assert monticulo_extraer_raiz(heap, []) is False
    assert monticulo_eliminar_valor(heap, 99) is False

    for value in (8, 3, 5, 1, 7, 2):
        assert monticulo_insertar(heap, value) is True
    assert monticulo_capacidad(heap) >= 6
    assert monticulo_cantidad(heap) == 6
    assert monticulo_vacio(heap) is False

    root: list[int] = []
    assert monticulo_raiz(heap, root) is True
    assert root == [1]
    assert monticulo_raiz(heap, None) is True
    existing = [999]
    assert monticulo_extraer_raiz(heap, existing) is True
    assert existing == [1]

    copied = [0]
    count = monticulo_copiar_valores(heap, copied, 3)
    assert count == 3
    assert len(copied) == 3
    assert monticulo_copiar_valores(heap, None, 3) == 0
    assert monticulo_copiar_valores(heap, [], 0) == 0

    array_text: list[str] = []
    monticulo_formatear_arreglo(heap, array_text, 100)
    assert array_text[0].startswith("[")
    monticulo_formatear_arreglo(heap, array_text, 5)
    assert len(array_text[0]) <= 4
    assert monticulo_formatear_arreglo(heap, None, 10) is None

    tree_text: list[str] = []
    monticulo_formatear_arbol(heap, tree_text, 100)
    assert "\n" in tree_text[0]
    replacement = ["old"]
    monticulo_formatear_arbol(heap, replacement, 5)
    assert replacement[0] != "old"
    assert monticulo_formatear_arbol(heap, None, 10) is None


def test_heap_build_max_delete_reheapify_and_empty_format() -> None:
    heap = MonticuloBinario()
    monticulo_inicializar(heap, MONTICULO_MAX, 1)
    assert monticulo_construir(heap, [4, 9, 3, 8, 7], 99) is True
    root: list[int] = []
    monticulo_raiz(heap, root)
    assert root == [9]

    assert monticulo_eliminar_valor(heap, 4) is True
    assert monticulo_eliminar_valor(heap, 9) is True
    extracted: list[int] = []
    while monticulo_extraer_raiz(heap, extracted):
        pass
    assert monticulo_vacio(heap) is True

    empty_tree: list[str] = []
    monticulo_formatear_arbol(heap, empty_tree, 30)
    assert empty_tree == ["(vacio)"]
    assert monticulo_formatear_arbol(heap, [], 0) is None
    assert monticulo_formatear_arreglo(heap, [], 0) is None

    monticulo_destruir(heap)
    assert monticulo_capacidad(heap) == 0
