"""Tests for C-code didactic service."""

from __future__ import annotations

from app.services.c_code_service import CCodeService


def test_linked_list_c_code_data_loaded() -> None:
    """Linked list should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("linked_list")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct nodo" in data["record"]
    assert "typedef struct" in data["record"]
    assert "insertar_inicio" in data["operations"]
    assert "lista_insertar_inicio" in data["operations"]["insertar_inicio"]


def test_stack_c_code_data_loaded() -> None:
    """Stack should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("stack")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct nodo" in data["record"]
    assert "typedef struct" in data["record"]
    assert "apilar" in data["operations"]
    assert "pila_push" in data["operations"]["apilar"]


def test_queue_c_code_data_loaded() -> None:
    """Queue should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("queue")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct nodo" in data["record"]
    assert "typedef struct" in data["record"]
    assert "encolar" in data["operations"]
    assert "cola_encolar" in data["operations"]["encolar"]


def test_priority_queue_c_code_data_loaded() -> None:
    """Priority queue should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("priority_queue")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct cp_nodo" in data["record"]
    assert "ColaPrioridad" in data["record"]
    assert "encolar" in data["operations"]
    assert "cp_encolar" in data["operations"]["encolar"]


def test_circular_list_c_code_data_loaded() -> None:
    """Circular list should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("circular_list")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct lcir_nodo" in data["record"]
    assert "ListaCircular" in data["record"]
    assert "insertar_inicio" in data["operations"]
    assert "lcir_insertar_inicio" in data["operations"]["insertar_inicio"]


def test_sublist_c_code_data_loaded() -> None:
    """Sublist should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("sublist")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "typedef struct sublista" in data["record"]
    assert "typedef struct nodo" in data["record"]
    assert "insertar_padre" in data["operations"]
    assert "sublista_insertar_padre_final" in data["operations"]["insertar_padre"]


def test_abb_c_code_data_loaded() -> None:
    """ABB should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("abb")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct Abb" in data["record"]
    assert "NodoAbb" in data["record"]
    assert "insertar" in data["operations"]
    assert "abb_insertar" in data["operations"]["insertar"]


def test_avl_c_code_data_loaded() -> None:
    """AVL should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("avl")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct Avl" in data["record"]
    assert "NodoAvl" in data["record"]
    assert "insertar" in data["operations"]
    assert "avl_insertar" in data["operations"]["insertar"]


def test_red_black_c_code_data_loaded() -> None:
    """Red-black should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("red_black")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "struct RojoNegro" in data["record"]
    assert "NodoRN" in data["record"]
    assert "insertar" in data["operations"]
    assert "rn_insertar" in data["operations"]["insertar"]


def test_binary_heap_c_code_data_loaded() -> None:
    """Binary heap should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("binary_heap")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "TipoMonticulo" in data["record"]
    assert "MonticuloBinario" in data["record"]
    assert "insertar" in data["operations"]
    assert "monticulo_insertar" in data["operations"]["insertar"]


def test_graph_c_code_data_loaded() -> None:
    """Graph should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("graph")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "GrafoArista" in data["record"]
    assert "struct Grafo" in data["record"]
    assert "typedef struct NodoArista" in data["record"]
    assert "typedef struct NodoVertice" in data["record"]
    assert "insert_vertex" in data["operations"]
    assert "grafo_insertar_vertice" in data["operations"]["insert_vertex"]
    assert data["record"].count("} GrafoArista;") == 1
    assert data["record"].count("} GrafoRecorrido;") == 1
    assert data["record"].count("} GrafoCamino;") == 1
    assert data["record"].count("} NodoArista;") == 1
    assert data["record"].count("} NodoVertice;") == 1


def test_hash_table_c_code_data_loaded() -> None:
    """Hash table should expose structure and mapped operations from C files."""
    data = CCodeService.get_structure_data("hash_table")
    assert data is not None
    assert data["code_title"] == "Codigo C"
    assert "THNodo" in data["record"]
    assert "TablaHash" in data["record"]
    assert "THEstadisticas" in data["record"]
    assert "create_table" in data["operations"]
    assert "th_inicializar" in data["operations"]["create_table"]
    assert "insert" in data["operations"]
    assert "th_insertar" in data["operations"]["insert"]
    assert "stats" in data["operations"]
    assert "th_estadisticas" in data["operations"]["stats"]


def test_non_mapped_structure_returns_none() -> None:
    """Structures without C mapping must return None."""
    assert CCodeService.get_structure_data("non_existing_structure") is None
