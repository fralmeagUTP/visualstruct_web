"""Tests for the C/Python canonical-state contract."""

import pytest

from app.services.conformance import CanonicalStateError, canonicalize_state


def test_sequential_state_preserves_contractual_order() -> None:
    result = canonicalize_state("stack", {"items": [{"value": 3}, {"value": 2}], "size": 2})
    assert result["state"] == {"values": [3, 2], "size": 2}


def test_tree_state_records_shape_and_traversals() -> None:
    root = {"value": 2, "left": {"value": 1}, "right": {"value": 3}}
    result = canonicalize_state("abb", {"root": root, "size": 3})
    assert result["state"]["inorder"] == [1, 2, 3]
    assert result["state"]["shape"] == [2, [1, None, None], [3, None, None]]


def test_heap_rejects_invalid_parent_child_order() -> None:
    with pytest.raises(CanonicalStateError, match="min-heap"):
        canonicalize_state("binary_heap", {"array": [4, 1], "size": 2})


def test_hash_state_ignores_bucket_representation_order() -> None:
    state = {"buckets": [{"entries": [{"key": 2, "value": 20}, {"key": 1, "value": 10}]}], "metadata": {"size": 2, "capacity": 3}}
    assert canonicalize_state("hash_table", state)["state"]["pairs"] == [[1, 10], [2, 20]]


def test_undirected_graph_normalizes_edge_orientation() -> None:
    state = {"directed": False, "nodes": [{"id": 2}, {"id": 1}], "edges": [{"source": 2, "target": 1, "weight": 4}]}
    result = canonicalize_state("graph", state)
    assert result["state"] == {
        "directed": False,
        "vertices": ["1", "2"],
        "edges": [["1", "2", 4]],
    }


def test_size_mismatch_is_rejected() -> None:
    with pytest.raises(CanonicalStateError, match="size declarado"):
        canonicalize_state("queue", {"items": [1], "size": 2})
