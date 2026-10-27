"""Deterministic, address-free logical identities for canonical C snapshots."""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Any


def _entities(state: dict[str, Any]) -> list[tuple[str, Any, dict[str, Any]]]:
    if "items" in state:
        return [("item", item.get("value"), {"position": i, **item})
                for i, item in enumerate(state["items"])]
    if "values" in state:
        return [("node", value, {"position": i, "value": value})
                for i, value in enumerate(state["values"])]
    if "pairs" in state:
        result = []
        for i, item in enumerate(state["pairs"]):
            if isinstance(item, dict):
                key, value = item.get("key"), item.get("value")
            else:
                key, value = item[0], item[1]
            result.append(("entry", key, {"position": i, "key": key, "value": value}))
        return result
    if "vertices" in state:
        return [("vertex", value, {"position": i, "value": value})
                for i, value in enumerate(state["vertices"])]
    if "inorder" in state:
        return [("node", value, {"position": i, "value": value})
                for i, value in enumerate(state["inorder"])]
    if "parents" in state:
        result: list[tuple[str, Any, dict[str, Any]]] = []
        for parent_index, parent in enumerate(state["parents"]):
            parent_value = parent.get("parent", parent.get("value"))
            result.append(("parent", parent_value, {"position": parent_index, "value": parent_value}))
            for child_index, child in enumerate(parent.get("children", [])):
                result.append((f"child@{parent_value}", child,
                               {"position": child_index, "value": child, "parent": parent_value}))
        return result
    return []


def logical_identity_frames(snapshots: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep an entity id when its semantic value moves to the next snapshot."""
    next_id = 1
    previous: dict[tuple[str, str], deque[str]] = {}
    frames: list[dict[str, Any]] = []
    for step, snapshot in enumerate(snapshots):
        available = {key: deque(ids) for key, ids in previous.items()}
        current: dict[tuple[str, str], deque[str]] = defaultdict(deque)
        output = []
        state = snapshot.get("state", snapshot)
        for kind, semantic_value, attributes in _entities(state):
            key = (kind, repr(semantic_value))
            queue = available.get(key)
            if queue:
                logical_id = queue.popleft()
            else:
                logical_id = f"{kind}:{next_id}"
                next_id += 1
            current[key].append(logical_id)
            output.append({"id": logical_id, "kind": kind, **attributes})
        frames.append({"step": step, "entities": output})
        previous = dict(current)
    return frames
