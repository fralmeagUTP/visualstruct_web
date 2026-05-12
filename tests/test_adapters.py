"""Unit tests for sequential adapters."""

from __future__ import annotations

import pytest

from app.adapters.linked_list_adapter import LinkedListAdapter
from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.adapters.queue_adapter import QueueAdapter
from app.adapters.stack_adapter import StackAdapter
from app.adapters.circular_list_adapter import CircularListAdapter
from app.adapters.sublist_adapter import SublistAdapter


def test_stack_adapter_push_pop() -> None:
    """Stack adapter should push and pop correctly."""
    adapter = StackAdapter()
    adapter.execute("apilar", {"value": "10"})
    adapter.execute("apilar", {"value": "20"})
    result = adapter.execute("desapilar", {})
    assert result["result"] == 20
    assert adapter.to_visual_state()["size"] == 1


def test_queue_adapter_enqueue_dequeue() -> None:
    """Queue adapter should preserve FIFO behavior."""
    adapter = QueueAdapter()
    adapter.execute("encolar", {"value": "10"})
    adapter.execute("encolar", {"value": "20"})
    result = adapter.execute("desencolar", {})
    assert result["result"] == 10
    assert adapter.to_visual_state()["size"] == 1


def test_priority_queue_adapter_front() -> None:
    """Priority queue should return lower priority value first."""
    adapter = PriorityQueueAdapter()
    adapter.execute("encolar", {"value": "30", "priority": 3})
    adapter.execute("encolar", {"value": "10", "priority": 1})
    result = adapter.execute("frente", {})
    assert result["result"] == 10


def test_linked_list_position_is_one_based() -> None:
    """Linked-list adapter should accept UI positions starting at 1."""
    adapter = LinkedListAdapter()
    adapter.execute("insertar_final", {"value": "40"})
    adapter.execute("insertar_posicion", {"value": "20", "position": "1"})
    state = adapter.to_visual_state()
    assert state["items"][0]["value"] == 20
    assert state["items"][1]["value"] == 40


def test_linked_list_rejects_zero_position() -> None:
    """Linked-list adapter should reject position 0 from UI."""
    adapter = LinkedListAdapter()
    with pytest.raises(ValueError, match="iniciar en 1"):
        adapter.execute("insertar_posicion", {"value": "5", "position": "0"})


def test_sequential_adapters_reject_non_integer_value() -> None:
    """Adapters with node values should reject non-integer input."""
    stack = StackAdapter()
    queue = QueueAdapter()
    linked = LinkedListAdapter()

    with pytest.raises(ValueError, match="entero"):
        stack.execute("apilar", {"value": "abc"})
    with pytest.raises(ValueError, match="entero"):
        queue.execute("encolar", {"value": "abc"})
    with pytest.raises(ValueError, match="entero"):
        linked.execute("insertar_inicio", {"value": "abc"})


def test_circular_list_adapter_search_one_based_and_extra_ops() -> None:
    """Circular-list adapter should expose one-based search and extra core operations."""
    adapter = CircularListAdapter()
    adapter.execute("insertar_final", {"value": "10"})
    adapter.execute("insertar_inicio", {"value": "5"})
    adapter.execute("insertar_final", {"value": "10"})

    search = adapter.execute("buscar_posiciones", {"value": "10"})
    assert search["result"] == [2, 3]

    adapter.execute("invertir", {})
    assert [item["value"] for item in adapter.to_visual_state()["items"]] == [10, 10, 5]

    adapter.execute("eliminar_primero", {"value": "10"})
    assert [item["value"] for item in adapter.to_visual_state()["items"]] == [10, 5]


def test_sublist_adapter_exposes_hijo_lifecycle() -> None:
    """Sublist adapter should add/list/remove children using parent context."""
    adapter = SublistAdapter()
    adapter.execute("insertar_padre", {"parent": "1"})
    adapter.execute("insertar_hijo", {"parent": "1", "child": "7"})
    adapter.execute("insertar_hijo", {"parent": "1", "child": "8"})

    listed = adapter.execute("hijos_de", {"parent": "1"})
    assert listed["result"] == [7, 8]

    adapter.execute("eliminar_hijo", {"parent": "1", "child": "7"})
    listed_after = adapter.execute("hijos_de", {"parent": "1"})
    assert listed_after["result"] == [8]
