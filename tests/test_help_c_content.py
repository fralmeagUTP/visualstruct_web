"""Regression tests for help pages with C TAD structure/methods."""

from __future__ import annotations



def test_sequential_help_structure_includes_c_tad_content(client) -> None:
    """Sequential help page should expose C struct and methods for the selected TAD."""
    response = client.get("/help/sequential/linked_list")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "struct nodo".encode("utf-8") in response.data
    assert "lista_insertar_inicio".encode("utf-8") in response.data



def test_hierarchical_help_structure_includes_c_tad_content(client) -> None:
    """Hierarchical help page should expose C struct and methods for ABB."""
    response = client.get("/help/hierarchical/abb")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "struct Abb".encode("utf-8") in response.data
    assert "abb_insertar".encode("utf-8") in response.data



def test_graph_help_structure_includes_c_tad_content(client) -> None:
    """Graph help page should expose C graph struct and operation snippets."""
    response = client.get("/help/graph/graph")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "struct Grafo".encode("utf-8") in response.data
    assert "grafo_insertar_vertice".encode("utf-8") in response.data



def test_hash_help_structure_includes_c_tad_content(client) -> None:
    """Hash help should expose C hash-table structure and methods."""
    response = client.get("/help/hash/hash_table")
    assert response.status_code == 200
    assert "Estructura del TAD en C".encode("utf-8") in response.data
    assert "Metodos del TAD en C".encode("utf-8") in response.data
    assert "TablaHash".encode("utf-8") in response.data
    assert "th_insertar".encode("utf-8") in response.data
