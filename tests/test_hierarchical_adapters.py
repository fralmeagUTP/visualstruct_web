"""Unit tests for hierarchical adapters."""

from __future__ import annotations

from app.adapters.abb_adapter import ABBAdapter
from app.adapters.avl_adapter import AVLAdapter
from app.adapters.binary_heap_adapter import BinaryHeapAdapter
from app.adapters.red_black_adapter import RedBlackAdapter


def test_abb_adapter_insert_and_validate() -> None:
    """ABB adapter should insert and keep structure valid."""
    adapter = ABBAdapter()
    adapter.execute("insertar", {"value": "5"})
    adapter.execute("insertar", {"value": "3"})
    adapter.execute("insertar", {"value": "8"})
    state = adapter.to_visual_state()
    assert state["size"] == 3
    assert state["validation"] is True


def test_avl_adapter_balance_validation() -> None:
    """AVL adapter should remain valid after insertions."""
    adapter = AVLAdapter()
    for value in ["10", "20", "30"]:
        adapter.execute("insertar", {"value": value})
    state = adapter.to_visual_state()
    assert state["validation"] is True
    assert state["height"] >= 1


def test_avl_adapter_uses_fe_contract_right_minus_left() -> None:
    """AVL visual FE must follow C contract: FE = altura(der) - altura(izq)."""
    adapter = AVLAdapter()
    for value in ["60", "50", "70", "80"]:
        adapter.execute("insertar", {"value": value})
    state = adapter.to_visual_state()
    root = state["root"]
    assert root["value"] == 60
    assert root["balance_factor"] == 1
    assert root["right"]["balance_factor"] == 1


def test_red_black_adapter_validate() -> None:
    """Red-black adapter should validate after operations."""
    adapter = RedBlackAdapter()
    adapter.execute("insertar", {"value": "7"})
    adapter.execute("insertar", {"value": "3"})
    adapter.execute("insertar", {"value": "11"})
    result = adapter.execute("validar", {})
    assert result["result"] is True


def test_heap_adapter_array_and_tree() -> None:
    """Heap adapter should expose array and tree state."""
    adapter = BinaryHeapAdapter()
    adapter.execute("insertar", {"value": "9"})
    adapter.execute("insertar", {"value": "4"})
    adapter.execute("insertar", {"value": "8"})
    state = adapter.to_visual_state()
    assert state["array"][0] == 4
    assert state["root"]["value"] == 4
