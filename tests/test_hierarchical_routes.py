"""Integration tests for hierarchical routes."""

from __future__ import annotations


def test_hierarchical_index_loads(client) -> None:
    """Hierarchical index should return available structures."""
    response = client.get("/hierarchical/")
    assert response.status_code == 200
    assert b"Modulo de Estructuras Jerarquicas" in response.data


def test_hierarchical_structure_page_loads(client) -> None:
    """Hierarchical structure page should load."""
    response = client.get("/hierarchical/abb")
    assert response.status_code == 200
    assert b"ABB" in response.data


def test_hierarchical_operate_insert(client) -> None:
    """Operation endpoint should update hierarchical visual state."""
    response = client.post(
        "/hierarchical/abb/operate",
        json={"operation": "insertar", "payload": {"value": "10"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["visual_state"]["size"] == 1


def test_hierarchical_help_loads(client) -> None:
    """Hierarchical help page should be available."""
    response = client.get("/help/hierarchical")
    assert response.status_code == 200
    assert b"Ayuda del modulo jerarquico" in response.data
