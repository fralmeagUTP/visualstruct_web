"""Integration tests for Flask routes."""

from __future__ import annotations


def test_homepage_loads(client) -> None:
    """Home page should return 200."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Visualizador Web de Estructuras de Datos".encode("utf-8") in response.data


def test_global_didactic_switch_is_rendered_in_layout(client) -> None:
    """Base layout should include global didactic mode switch."""
    response = client.get("/sequential/stack")
    assert response.status_code == 200
    assert b"didactic-mode-switch" in response.data
    assert "Mostrar codigo y detalles tecnicos".encode("utf-8") in response.data


def test_sequential_index_loads(client) -> None:
    """Sequential index should return cards."""
    response = client.get("/sequential/")
    assert response.status_code == 200
    assert "Módulo de Estructuras Secuenciales".encode("utf-8") in response.data


def test_structure_page_loads(client) -> None:
    """Each structure page should load."""
    response = client.get("/sequential/stack")
    assert response.status_code == 200
    assert "Pila".encode("utf-8") in response.data


def test_linked_list_page_shows_c_code_panel(client) -> None:
    """Linked-list page should render C code instead of pseudocode."""
    response = client.get("/sequential/linked_list")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "lista_insertar_inicio".encode("utf-8") in response.data


def test_circular_list_page_shows_c_code_panel(client) -> None:
    """Circular-list page should render C code instead of pseudocode."""
    response = client.get("/sequential/circular_list")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "lcir_insertar_inicio".encode("utf-8") in response.data


def test_sublist_page_shows_c_code_panel(client) -> None:
    """Sublist page should render C code instead of pseudocode."""
    response = client.get("/sequential/sublist")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "sublista_insertar_padre_final".encode("utf-8") in response.data


def test_abb_page_shows_c_code_panel(client) -> None:
    """ABB page should render C code instead of pseudocode."""
    response = client.get("/hierarchical/abb")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "abb_insertar".encode("utf-8") in response.data


def test_avl_page_shows_c_code_panel(client) -> None:
    """AVL page should render C code instead of pseudocode."""
    response = client.get("/hierarchical/avl")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "avl_insertar".encode("utf-8") in response.data


def test_red_black_page_shows_c_code_panel(client) -> None:
    """Red-black page should render C code instead of pseudocode."""
    response = client.get("/hierarchical/red_black")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "rbt_insertar".encode("utf-8") in response.data


def test_binary_heap_page_shows_c_code_panel(client) -> None:
    """Binary-heap page should render C code instead of pseudocode."""
    response = client.get("/hierarchical/binary_heap")
    assert response.status_code == 200
    assert "Codigo C:".encode("utf-8") in response.data
    assert "monticulo_insertar".encode("utf-8") in response.data


def test_operate_stack_success(client) -> None:
    """Stack operation endpoint should mutate state."""
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "10"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["visual_state"]["size"] == 1


def test_operate_stack_empty_error(client) -> None:
    """Empty stack pop should return didactic error."""
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "desapilar", "payload": {}},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "vacía" in data["message"]


def test_sequential_page_renders_interpreter_controls(client) -> None:
    """Sequential structure page should include interpreter simulation controls."""
    response = client.get("/sequential/stack")
    assert response.status_code == 200
    assert b"seq-sim-play" in response.data
    assert b"seq-sim-prev" in response.data
    assert b"seq-sim-step" in response.data
    assert b"reset-button" in response.data
    assert b"seq-sim-counter" in response.data
    assert b"seq-step-toggle" in response.data


def test_hierarchical_page_renders_interpreter_controls(client) -> None:
    """Hierarchical structure page should include interpreter simulation controls."""
    response = client.get("/hierarchical/abb")
    assert response.status_code == 200
    assert b"hier-sim-play" in response.data
    assert b"hier-sim-prev" in response.data
    assert b"hier-sim-step" in response.data
    assert b"reset-button" in response.data
    assert b"hier-sim-counter" in response.data
    assert b"hier-step-toggle" in response.data


def test_hash_page_renders_interpreter_controls(client) -> None:
    """Hash structure page should include interpreter simulation controls."""
    response = client.get("/hash/hash_table")
    assert response.status_code == 200
    assert b"hash-sim-play" in response.data
    assert b"hash-sim-prev" in response.data
    assert b"hash-sim-step" in response.data
    assert b"hash-reset-button" in response.data
    assert b"hash-sim-counter" in response.data
    assert b"hash-step-toggle" in response.data


def test_graph_page_renders_interpreter_counter(client) -> None:
    """Graph page should include interpreter step counter.""" 
    response = client.get("/graph/graph")
    assert response.status_code == 200
    assert b"graph-sim-counter" in response.data
    assert b"graph-step-toggle" in response.data


def test_sorting_page_renders_interpreter_controls(client) -> None:
    """Sorting visualizer page should include interpreter controls."""
    response = client.get("/sorting/visualizador")
    assert response.status_code == 200
    assert b"sorting-sim-play" in response.data
    assert b"sorting-sim-prev" in response.data
    assert b"sorting-sim-step" in response.data
    assert b"sorting-step-toggle" in response.data
