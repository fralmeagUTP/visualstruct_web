"""Regression tests for help pages with C TAD structure/methods."""

from __future__ import annotations



def test_sequential_help_structure_includes_c_tad_content(client) -> None:
    """Sequential help page should expose C struct and methods for the selected TAD."""
    response = client.get("/help/sequential/linked_list")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "NodoLista".encode("utf-8") in response.data
    assert "lista_insertar_inicio".encode("utf-8") in response.data



def test_hierarchical_help_structure_includes_c_tad_content(client) -> None:
    """Hierarchical help page should expose C struct and methods for ABB."""
    response = client.get("/help/hierarchical/abb")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "ABBNodo".encode("utf-8") in response.data
    assert "abb_insertar".encode("utf-8") in response.data



def test_graph_help_structure_includes_c_tad_content(client) -> None:
    """Graph help page should expose C graph struct and operation snippets."""
    response = client.get("/help/graph/graph")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "nodoGrafo".encode("utf-8") in response.data
    assert "grafo_insertar_vertice".encode("utf-8") in response.data



def test_hash_help_structure_includes_c_tad_content(client) -> None:
    """Hash help should expose C hash-table structure and methods."""
    response = client.get("/help/hash/hash_table")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "TablaHash".encode("utf-8") in response.data
    assert "th_insertar".encode("utf-8") in response.data


def test_hierarchical_help_red_black_uses_new_tads_c_content(client) -> None:
    """Red-black help should render new C TAD symbols, not fallback placeholders."""
    response = client.get("/help/hierarchical/red_black")
    assert response.status_code == 200
    assert "nodoRBT".encode("utf-8") in response.data
    assert "rbt_insertar".encode("utf-8") in response.data
    assert "Estructura en C no encontrada para RojoNegro.".encode("utf-8") not in response.data
    assert (
        "Codigo C no disponible para esta operacion en docs/tads_C/tad_rojo_negro.c.".encode("utf-8")
        not in response.data
    )


def test_help_pages_include_tad_introduction_and_method_explanation(client) -> None:
    """Help page should render unified TAD description and per-method explanation text."""
    response = client.get("/help/sequential/linked_list")
    assert response.status_code == 200
    assert "Descripcion del TAD".encode("utf-8") in response.data
    assert "Este metodo del TAD".encode("utf-8") in response.data or "Inserta".encode("utf-8") in response.data


def test_graph_help_supported_operations_use_c_tad_names(client) -> None:
    """Graph help should list supported operations using C TAD function names."""
    response = client.get("/help/graph/graph")
    assert response.status_code == 200
    assert "grafo_crear".encode("utf-8") in response.data
    assert "grafo_insertar_vertice".encode("utf-8") in response.data
    assert "grafo_dijkstra".encode("utf-8") in response.data
    assert b"<li>/**" not in response.data
