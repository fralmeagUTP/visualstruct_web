"""Seeded conformance scenarios and deterministic failure reduction."""

from __future__ import annotations

import random
from collections.abc import Callable

from app.services.conformance.runner import ScenarioOperation, SPECS


def generate_scenario(
    structure_id: str, *, seed: int, length: int = 20
) -> list[ScenarioOperation]:
    """Generate one valid, deterministic mutating scenario for a registered TAD."""
    normalized_id = str(structure_id).strip().lower()
    if normalized_id not in SPECS:
        raise ValueError(f"TAD no registrado: {structure_id}")
    if length <= 0:
        raise ValueError("length debe ser positivo")
    rng = random.Random(seed)
    values = [rng.randint(-100, 100) for _ in range(length)]

    if normalized_id == "stack":
        return [ScenarioOperation("apilar", {"value": value}) for value in values]
    if normalized_id == "queue":
        return [ScenarioOperation("encolar", {"value": value}) for value in values]
    if normalized_id == "linked_list":
        return [ScenarioOperation("insertar_final", {"value": value}) for value in values]
    if normalized_id == "circular_list":
        return [ScenarioOperation("insertar_final", {"value": value}) for value in values]
    if normalized_id == "priority_queue":
        return [
            ScenarioOperation("encolar", {"value": value, "priority": rng.randint(0, 9)})
            for value in values
        ]
    if normalized_id == "sublist":
        parents = rng.sample(range(-10_000, 10_000), length)
        return [ScenarioOperation("insertar_padre", {"parent": value}) for value in parents]
    if normalized_id == "binary_heap":
        return [ScenarioOperation("insertar", {"value": value}) for value in values]
    if normalized_id in {"abb", "avl", "red_black"}:
        unique_values = list(dict.fromkeys(values))
        while len(unique_values) < length:
            candidate = rng.randint(-10_000, 10_000)
            if candidate not in unique_values:
                unique_values.append(candidate)
        return [ScenarioOperation("insertar", {"value": value}) for value in unique_values]
    if normalized_id == "graph":
        vertices = rng.sample(range(-10_000, 10_000), length)
        return [
            ScenarioOperation("create_graph", {"directed": True}),
            *[
                ScenarioOperation("insert_vertex", {"vertex": vertex})
                for vertex in vertices
            ],
        ]
    if normalized_id == "hash_table":
        return [
            ScenarioOperation("insert", {"key": str(index), "value": str(value)})
            for index, value in enumerate(values, start=1)
        ]
    if normalized_id == "sorting":
        return [
            ScenarioOperation("create_array", {"values": values}),
            ScenarioOperation("select_algorithm", {"algorithm_id": "quicksort"}),
            ScenarioOperation("run", {"mode": "fast"}),
        ]
    raise AssertionError("registro de generador incompleto")


def reduce_failing_sequence(
    operations: list[ScenarioOperation],
    still_fails: Callable[[list[ScenarioOperation]], bool],
) -> list[ScenarioOperation]:
    """Return a 1-minimal failing subsequence using deterministic chunk removal."""
    current = list(operations)
    if not current or not still_fails(current):
        raise ValueError("la secuencia inicial debe reproducir el fallo")
    granularity = 2
    while len(current) >= 2:
        chunk_size = max(1, (len(current) + granularity - 1) // granularity)
        reduced = False
        for start in range(0, len(current), chunk_size):
            candidate = current[:start] + current[start + chunk_size :]
            if candidate and still_fails(candidate):
                current = candidate
                granularity = max(2, granularity - 1)
                reduced = True
                break
        if not reduced:
            if granularity >= len(current):
                break
            granularity = min(len(current), granularity * 2)
    return current
