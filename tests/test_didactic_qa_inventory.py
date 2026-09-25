"""Tests for the reproducible didactic QA inventory."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.build_didactic_qa_inventory import SCHEMA_VERSION, build_inventory


ROOT = Path(__file__).resolve().parents[1]


def test_inventory_discovers_all_supported_structures_and_sorting_algorithms() -> None:
    inventory = build_inventory()
    assert inventory["schema"] == SCHEMA_VERSION
    assert inventory["structures_count"] == 13
    structures = {item["id"]: item for item in inventory["structures"]}
    assert set(structures) == {
        "stack", "queue", "priority_queue", "linked_list", "circular_list", "sublist",
        "abb", "avl", "red_black", "binary_heap", "graph", "hash_table", "sorting_array",
    }
    algorithms = {row["name"] for row in structures["sorting_array"]["operations"] if row["kind"] == "algorithm"}
    assert len(algorithms) == 11


def test_every_structure_has_c_source_strategy_renderer_and_endpoints() -> None:
    for structure in build_inventory()["structures"]:
        assert structure["c_sources"]
        assert structure["trace_strategy"].endswith("TraceStrategy")
        assert structure["renderer"]["file"].endswith(".js")
        assert {"page", "operate", "reset"} <= set(structure["endpoints"])


def test_all_sorting_algorithms_have_c_mapping() -> None:
    sorting = next(item for item in build_inventory()["structures"] if item["id"] == "sorting_array")
    algorithms = [row for row in sorting["operations"] if row["kind"] == "algorithm"]
    assert all(row["mapping_status"] == "mapped" for row in algorithms)
    assert all(row["didactic_source"] == "c" for row in algorithms)


def test_inventory_classifies_mapping_and_didactic_source_gaps() -> None:
    inventory = build_inventory()
    gaps = inventory["gaps"]
    assert "stack::limpiar" in gaps["unmapped_public_operations"]
    # `limpiar` is composed from real C snippets even without a direct symbol map.
    assert "stack::limpiar" not in gaps["fallback_or_derived_operations"]
    assert "graph::generate_random_graph" in gaps["fallback_or_derived_operations"]
    assert gaps["orphan_c_mappings"]["sorting_array"] == [
        "copiar_arreglo", "imprimir_arreglo", "probar_algoritmo_int", "probar_algoritmo_void"
    ]


def test_qa_result_protocol_v1_requires_all_report_fields() -> None:
    schema = json.loads(
        (ROOT / "docs/qa/didactic-qa-result-schema-v1.json").read_text(encoding="utf-8")
    )
    assert schema["$id"] == "didactic-qa-result/v1"
    required = set(schema["required"])
    assert {"case_id", "structure_id", "operation", "expected", "observed", "result"} <= required
    assert set(schema["properties"]["severity"]["enum"]) == {
        "critical", "high", "medium", "low", "none"
    }
    assert set(schema["$defs"]["layerState"]["properties"]["layer"]["enum"]) == {
        "c", "backend", "trace", "history", "console", "frontend"
    }
