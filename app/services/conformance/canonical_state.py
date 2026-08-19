"""Canonical, UI-independent state representation used by C/Python comparisons."""

from __future__ import annotations

from typing import Any


SCHEMA = "canonical-state/v1"
SEQUENTIAL_IDS = {
    "linked_list", "stack", "queue", "priority_queue", "circular_list", "sublist"
}
TREE_IDS = {"abb", "avl", "red_black"}


class CanonicalStateError(ValueError):
    """Raised when a state violates its cross-language contract."""


def _value(item: Any) -> Any:
    return item.get("value") if isinstance(item, dict) and "value" in item else item


def _tree_values(node: Any, traversal: str) -> list[Any]:
    if not isinstance(node, dict):
        return []
    left = _tree_values(node.get("left"), traversal)
    right = _tree_values(node.get("right"), traversal)
    value = [_value(node)]
    if traversal == "preorder":
        return value + left + right
    if traversal == "postorder":
        return left + right + value
    return left + value + right


def _tree_shape(node: Any) -> Any:
    if not isinstance(node, dict):
        return None
    return [_value(node), _tree_shape(node.get("left")), _tree_shape(node.get("right"))]


def _declared_size(state: dict[str, Any], fallback: int) -> int:
    metadata = state.get("metadata")
    candidate = metadata.get("size") if isinstance(metadata, dict) else state.get("size")
    return fallback if candidate is None else int(candidate)


def _assert_size(state: dict[str, Any], actual: int) -> None:
    declared = _declared_size(state, actual)
    if declared != actual:
        raise CanonicalStateError(f"size declarado {declared} != size real {actual}")


def _canonical_sequential(structure_id: str, state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    if structure_id == "priority_queue":
        items = [
            {"value": item.get("value"), "priority": item.get("priority")}
            for item in state.get("items", [])
            if isinstance(item, dict)
        ]
        _assert_size(state, len(items))
        return {"items": items, "size": len(items)}, {"size_matches": True}
    if structure_id == "sublist":
        parents = [
            {"parent": item.get("parent"), "children": list(item.get("children", []))}
            for item in state.get("items", [])
            if isinstance(item, dict)
        ]
        _assert_size(state, len(parents))
        return {"parents": parents, "size": len(parents)}, {"size_matches": True}
    items = [_value(item) for item in state.get("items", [])]
    _assert_size(state, len(items))
    return {"values": items, "size": len(items)}, {"size_matches": True}


def _canonical_tree(structure_id: str, state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    root = state.get("root")
    inorder = _tree_values(root, "inorder")
    preorder = _tree_values(root, "preorder")
    _assert_size(state, len(inorder))
    bst_order = all(inorder[index] < inorder[index + 1] for index in range(len(inorder) - 1))
    if not bst_order:
        raise CanonicalStateError("el recorrido in-order no cumple orden BST estricto")
    invariants = {"size_matches": True, "bst_order": True}
    if structure_id == "avl":
        invariants["avl_valid"] = bool(state.get("validation", True))
    if structure_id == "red_black":
        invariants["red_black_valid"] = bool(state.get("validation", True))
    if not all(invariants.values()):
        raise CanonicalStateError("el árbol reporta una invariante de balance o color inválida")
    return {
        "inorder": inorder,
        "preorder": preorder,
        "shape": _tree_shape(root),
        "size": len(inorder),
    }, invariants


def _canonical_heap(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    values = list(state.get("array", []))
    _assert_size(state, len(values))
    heap_order = all(values[(index - 1) // 2] <= values[index] for index in range(1, len(values)))
    if not heap_order:
        raise CanonicalStateError("el arreglo no cumple la propiedad min-heap")
    return {"values": values, "size": len(values)}, {"size_matches": True, "min_heap": True}


def _canonical_hash(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    pairs: list[list[Any]] = []
    for bucket in state.get("buckets", []):
        if not isinstance(bucket, dict):
            continue
        for entry in bucket.get("entries", []):
            if isinstance(entry, dict):
                pairs.append([entry.get("key"), entry.get("value")])
    pairs.sort(key=lambda pair: (str(pair[0]), str(pair[1])))
    _assert_size(state, len(pairs))
    metadata = state.get("metadata", {})
    capacity = int(metadata.get("capacity", len(state.get("buckets", []))))
    if capacity <= 0:
        raise CanonicalStateError("la capacidad hash debe ser positiva")
    return {"pairs": pairs, "size": len(pairs), "capacity": capacity}, {"size_matches": True, "capacity_positive": True}


def _canonical_graph(state: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    def vertex_key(value: Any) -> tuple[int, int | str]:
        text = str(value)
        try:
            return (0, int(text))
        except ValueError:
            return (1, text)

    directed = bool(state.get("directed", False))
    vertices = [
        str(node.get("id", node.get("value")) if isinstance(node, dict) else node)
        for node in state.get("nodes", [])
    ]
    vertices.sort(key=vertex_key)
    edges: list[list[Any]] = []
    for edge in state.get("edges", []):
        if not isinstance(edge, dict):
            continue
        source, target = str(edge.get("source")), str(edge.get("target"))
        if not directed and vertex_key(source) > vertex_key(target):
            source, target = target, source
        edges.append([source, target, edge.get("weight", 1)])
    edges.sort(key=lambda edge: (vertex_key(edge[0]), vertex_key(edge[1]), str(edge[2])))
    return {"directed": directed, "vertices": vertices, "edges": edges}, {"unique_vertices": len(vertices) == len(set(map(str, vertices)))}


def canonicalize_state(structure_id: str, state: dict[str, Any]) -> dict[str, Any]:
    """Normalize one adapter/C-harness state and enforce family invariants."""
    if not isinstance(state, dict):
        raise CanonicalStateError("el estado debe ser un objeto")
    normalized_id = str(structure_id).strip().lower()
    if normalized_id in SEQUENTIAL_IDS:
        data, invariants = _canonical_sequential(normalized_id, state)
        family = "sequential"
    elif normalized_id in TREE_IDS:
        data, invariants = _canonical_tree(normalized_id, state)
        family = "tree"
    elif normalized_id == "binary_heap":
        data, invariants = _canonical_heap(state)
        family = "heap"
    elif normalized_id == "hash_table":
        data, invariants = _canonical_hash(state)
        family = "hash"
    elif normalized_id == "graph":
        data, invariants = _canonical_graph(state)
        family = "graph"
    elif normalized_id == "sorting":
        values = list(state.get("array", state.get("items", [])))
        data, invariants, family = {"values": values, "size": len(values)}, {"size_matches": True}, "sorting"
    else:
        raise CanonicalStateError(f"TAD no registrado: {structure_id}")
    return {"schema": SCHEMA, "structure_id": normalized_id, "family": family, "state": data, "invariants": invariants}
