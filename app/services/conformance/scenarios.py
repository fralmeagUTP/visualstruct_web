"""Deterministic scenario catalog for every registered TAD."""

from __future__ import annotations

from dataclasses import dataclass

from app.services.conformance.runner import ScenarioOperation


@dataclass(frozen=True)
class DeterministicCases:
    success: tuple[ScenarioOperation, ...]
    boundary: tuple[ScenarioOperation, ...]
    error: tuple[ScenarioOperation, ...]


def op(name: str, **payload: object) -> ScenarioOperation:
    return ScenarioOperation(name, dict(payload))


CASES: dict[str, DeterministicCases] = {
    "linked_list": DeterministicCases((op("insertar_final", value=2), op("insertar_inicio", value=1)), (), (op("insertar_final", value="x"),)),
    "stack": DeterministicCases((op("apilar", value=1), op("apilar", value=2), op("desapilar")), (), (op("desapilar"),)),
    "queue": DeterministicCases((op("encolar", value=1), op("encolar", value=2), op("desencolar")), (), (op("desencolar"),)),
    "priority_queue": DeterministicCases((op("encolar", value=1, priority=2), op("encolar", value=2, priority=1)), (), (op("desencolar"),)),
    "circular_list": DeterministicCases((op("insertar_final", value=1), op("insertar_final", value=2), op("invertir")), (), (op("insertar_final", value="x"),)),
    "sublist": DeterministicCases((op("insertar_padre", parent=1), op("insertar_hijo", parent=1, child=2)), (), (op("insertar_hijo", parent=99, child=2),)),
    "binary_heap": DeterministicCases((op("insertar", value=2), op("insertar", value=1), op("extraer_raiz")), (), (op("extraer_raiz"),)),
    "abb": DeterministicCases((op("insertar", value=2), op("insertar", value=1), op("insertar", value=3)), (), (op("insertar", value="x"),)),
    "avl": DeterministicCases((op("insertar", value=30), op("insertar", value=20), op("insertar", value=10)), (), (op("insertar", value="x"),)),
    "red_black": DeterministicCases((op("insertar", value=10), op("insertar", value=20), op("insertar", value=30)), (), (op("insertar", value="x"),)),
    "graph": DeterministicCases((op("create_graph", directed=True), op("insert_vertex", vertex=1)), (op("create_graph", directed=True),), (op("create_graph", directed=True), op("insert_vertex", vertex="x"))),
    "hash_table": DeterministicCases((op("insert", key="1", value="10"),), (), (op("insert", key="", value="10"),)),
    "sorting": DeterministicCases((op("create_array", values=[2, 1]), op("select_algorithm", algorithm_id="quicksort"), op("run", mode="fast")), (op("create_array", values=[1]), op("select_algorithm", algorithm_id="burbuja"), op("run", mode="fast")), (op("create_array", values=[]), op("select_algorithm", algorithm_id="burbuja"), op("run", mode="fast"))),
}
