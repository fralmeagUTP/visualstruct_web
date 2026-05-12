"""Coverage-focused tests for hierarchical adapters."""

from __future__ import annotations

import pytest

from app.adapters.abb_adapter import ABBAdapter
from app.adapters.avl_adapter import AVLAdapter
from app.adapters.binary_heap_adapter import BinaryHeapAdapter
from app.adapters.red_black_adapter import RedBlackAdapter


def test_abb_adapter_all_operations_and_errors() -> None:
    """ABB adapter should cover all supported operations and invalid branches."""
    adapter = ABBAdapter()

    for value in [10, 5, 15, 12, 18]:
        adapter.execute("insertar", {"value": str(value)})

    assert adapter.execute("buscar", {"value": "12"})["result"] is True
    assert adapter.execute("buscar", {"value": "999"})["result"] is False
    assert adapter.execute("minimo", {})["result"] == 5
    assert adapter.execute("maximo", {})["result"] == 18
    assert adapter.execute("altura", {})["result"] >= 1
    assert adapter.execute("contar_hojas", {})["result"] >= 1
    assert adapter.execute("inorden", {})["result"] == [5, 10, 12, 15, 18]
    assert adapter.execute("preorden", {})["result"][0] == 10
    assert adapter.execute("postorden", {})["result"][-1] == 10
    assert adapter.execute("validar", {})["result"] is True

    adapter.execute("eliminar", {"value": "12"})
    state = adapter.to_visual_state()
    assert state["kind"] == "binary_tree"
    assert "ABB" in state["title"]
    assert state["size"] == 4
    assert state["validation"] is True
    assert state["traversals"]["inorden"] == [5, 10, 15, 18]

    adapter.execute("limpiar", {})
    assert adapter.to_visual_state()["empty"] is True

    with pytest.raises(ValueError, match="soportada"):
        adapter.execute("operacion_inexistente", {})
    with pytest.raises(ValueError, match="entero"):
        adapter.execute("insertar", {"value": "abc"})


def test_avl_adapter_all_operations_and_errors() -> None:
    """AVL adapter should cover all supported operations and state serialization."""
    adapter = AVLAdapter()

    for value in [30, 10, 20, 40, 35, 50]:
        adapter.execute("insertar", {"value": str(value)})

    assert adapter.execute("buscar", {"value": "35"})["result"] is True
    assert adapter.execute("buscar", {"value": "999"})["result"] is False
    assert adapter.execute("minimo", {})["result"] == 10
    assert adapter.execute("maximo", {})["result"] == 50
    assert adapter.execute("altura", {})["result"] >= 1
    assert adapter.execute("inorden", {})["result"] == [10, 20, 30, 35, 40, 50]
    assert adapter.execute("validar", {})["result"] is True

    adapter.execute("eliminar", {"value": "30"})
    state = adapter.to_visual_state()
    assert state["kind"] == "binary_tree"
    assert "AVL" in state["title"]
    assert state["size"] == 5
    assert state["validation"] is True
    assert state["root"] is not None
    assert "height" in state["root"]
    assert "balance_factor" in state["root"]

    adapter.execute("limpiar", {})
    assert adapter.to_visual_state()["empty"] is True

    with pytest.raises(ValueError, match="soportada"):
        adapter.execute("operacion_inexistente", {})
    with pytest.raises(ValueError, match="entero"):
        adapter.execute("insertar", {"value": "abc"})


def test_red_black_adapter_all_operations_and_nil_serialization() -> None:
    """Red-black adapter should expose valid colors and omit sentinel nodes in JSON."""
    adapter = RedBlackAdapter()

    for value in [10, 5, 15, 1, 7, 12, 18]:
        adapter.execute("insertar", {"value": str(value)})

    assert adapter.execute("buscar", {"value": "7"})["result"] is True
    assert adapter.execute("buscar", {"value": "999"})["result"] is False
    assert adapter.execute("inorden", {})["result"] == [1, 5, 7, 10, 12, 15, 18]
    assert adapter.execute("altura", {})["result"] >= 1
    assert adapter.execute("validar", {})["result"] is True

    adapter.execute("eliminar", {"value": "1"})
    state = adapter.to_visual_state()
    assert state["kind"] == "binary_tree"
    assert "Rojo-Negro" in state["title"]
    assert state["size"] == 6
    assert state["validation"] is True
    assert state["root"] is not None
    assert state["root"]["color"] in {"RED", "BLACK"}

    def _collect_nodes(node: dict | None) -> list[dict]:
        if node is None:
            return []
        return [node] + _collect_nodes(node.get("left")) + _collect_nodes(node.get("right"))

    all_nodes = _collect_nodes(state["root"])
    assert all(node["color"] in {"RED", "BLACK"} for node in all_nodes)

    adapter.execute("limpiar", {})
    assert adapter.to_visual_state()["empty"] is True

    with pytest.raises(ValueError, match="soportada"):
        adapter.execute("operacion_inexistente", {})
    with pytest.raises(ValueError, match="entero"):
        adapter.execute("insertar", {"value": "abc"})


def test_binary_heap_adapter_all_operations_and_errors() -> None:
    """Heap adapter should cover every operation, including reset and invalid operation."""
    adapter = BinaryHeapAdapter()

    for value in [9, 4, 8, 1]:
        adapter.execute("insertar", {"value": str(value)})

    assert adapter.execute("raiz", {})["result"] == 1
    assert adapter.execute("a_lista", {})["result"][0] == 1
    assert adapter.execute("extraer_raiz", {})["result"] == 1

    state = adapter.to_visual_state()
    assert state["kind"] == "heap"
    assert "Binario" in state["title"]
    assert state["size"] == 3
    assert state["root"] is not None
    assert "left" in state["root"]

    adapter.reset()
    assert adapter.to_visual_state()["empty"] is True

    with pytest.raises(ValueError, match="soportada"):
        adapter.execute("operacion_inexistente", {})
    with pytest.raises(ValueError, match="entero"):
        adapter.execute("insertar", {"value": "abc"})
