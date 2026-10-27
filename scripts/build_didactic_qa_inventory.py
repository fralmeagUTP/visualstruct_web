"""Build the reproducible C-to-visual QA coverage inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.c_code_service import CCodeService
from app.services.graph_structure_service import GraphStructureService
from app.services.hash_structure_service import HashStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.sorting_structure_service import SortingStructureService
from app.services.structure_service import StructureService
from app.services.trace import TraceStrategyRegistry


SCHEMA_VERSION = "didactic-qa-inventory/v1"

SERVICES: tuple[tuple[str, type[Any]], ...] = (
    ("sequential", StructureService),
    ("hierarchical", HierarchicalStructureService),
    ("graph", GraphStructureService),
    ("hash", HashStructureService),
    ("sorting", SortingStructureService),
)

C_MAPS: dict[str, str] = {
    "stack": "_STACK_OPERATION_MAP",
    "queue": "_QUEUE_OPERATION_MAP",
    "priority_queue": "_PRIORITY_QUEUE_OPERATION_MAP",
    "linked_list": "_LINKED_LIST_OPERATION_MAP",
    "circular_list": "_CIRCULAR_LIST_OPERATION_MAP",
    "sublist": "_SUBLIST_OPERATION_MAP",
    "abb": "_ABB_OPERATION_MAP",
    "avl": "_AVL_OPERATION_MAP",
    "red_black": "_RED_BLACK_OPERATION_MAP",
    "binary_heap": "_BINARY_HEAP_OPERATION_MAP",
    "graph": "_GRAPH_OPERATION_MAP",
    "hash_table": "_HASH_TABLE_OPERATION_MAP",
    "sorting_array": "_SORTING_OPERATION_MAP",
}

C_SOURCES: dict[str, tuple[str, ...]] = {
    "stack": ("docs/tads_C/tad_pila.c",),
    "queue": ("docs/tads_C/tad_cola.c",),
    "priority_queue": ("docs/tads_C/tad_cola_prioridad.c",),
    "linked_list": ("docs/tads_C/tad_lista.c",),
    "circular_list": ("docs/tads_C/tad_lista_circular.c",),
    "sublist": ("docs/tads_C/tad_sublista.c",),
    "abb": ("docs/tads_C/tad_abb.c",),
    "avl": ("docs/tads_C/tad_avl.c",),
    "red_black": ("docs/tads_C/tad_rojo_negro.c",),
    "binary_heap": ("docs/tads_C/tad_monticulo_binario.c",),
    "graph": ("docs/tads_C/tad_grafo.c", "docs/tads_C/tad_cola.c"),
    "hash_table": ("docs/tads_C/tad_tabla_hash.c",),
    "sorting_array": ("docs/tads_C/tad_ordenamiento.c",),
}

RENDERERS: dict[str, dict[str, str]] = {
    "sequential": {"file": "static/js/sequential.js", "function": "renderVisualState"},
    "hierarchical": {"file": "static/js/hierarchical.js", "function": "renderHierState"},
    "graph": {"file": "static/js/graph.js", "function": "renderGraphState"},
    "hash": {"file": "static/js/hash.js", "function": "renderHashState"},
    "sorting": {"file": "static/js/sorting.js", "function": "renderSortingVisualState"},
}

ENDPOINTS: dict[str, dict[str, str]] = {
    "sequential": {"page": "/sequential/<structure_id>", "operate": "/sequential/<structure_id>/operate", "reset": "/sequential/<structure_id>/reset"},
    "hierarchical": {"page": "/hierarchical/<structure_id>", "operate": "/hierarchical/<structure_id>/operate", "reset": "/hierarchical/<structure_id>/reset"},
    "graph": {"page": "/graph/<structure_id>/<phase>", "operate": "/graph/<structure_id>/operate", "reset": "/graph/<structure_id>/reset"},
    "hash": {"page": "/hash/<structure_id>", "operate": "/hash/<structure_id>/operate", "reset": "/hash/<structure_id>/reset"},
    "sorting": {"page": "/sorting/visualizador", "operate": "/api/ordenamiento/<action>", "reset": "/api/ordenamiento/reset"},
}


def _test_references(*tokens: str) -> list[str]:
    references: list[str] = []
    for test_file in sorted((ROOT / "tests").glob("test_*.py")):
        text = test_file.read_text(encoding="utf-8")
        if all(token in text for token in tokens):
            references.append(test_file.relative_to(ROOT).as_posix())
    return references


def build_inventory() -> dict[str, Any]:
    """Return the deterministic inventory derived from runtime registries."""
    structures: list[dict[str, Any]] = []
    for family, service in SERVICES:
        registry = service._REGISTRY  # type: ignore[attr-defined]
        for structure_id, metadata in registry.items():
            adapter_class = metadata["adapter"]
            adapter = adapter_class()
            operations = list(adapter.get_supported_operations())
            c_map = dict(getattr(CCodeService, C_MAPS[structure_id]))
            c_payload = CCodeService.get_structure_data(structure_id) or {}
            c_operation_code = c_payload.get("operations", {})
            strategy = TraceStrategyRegistry.resolve(structure_id)
            operation_rows: list[dict[str, Any]] = []
            for operation in operations:
                name = str(operation["name"])
                operation_rows.append(
                    {
                        "name": name,
                        "kind": "operation",
                        "mutates": bool(operation.get("mutates", False)),
                        "c_function": c_map.get(name),
                        "mapping_status": "mapped" if name in c_map else "unmapped",
                        "didactic_source": "c" if c_operation_code.get(name) else "fallback_or_derived",
                        "tests": _test_references(structure_id, name),
                    }
                )
            if structure_id == "sorting_array":
                for algorithm in adapter.get_supported_algorithms():
                    name = str(algorithm["id"])
                    operation_rows.append(
                        {
                            "name": name,
                            "kind": "algorithm",
                            "mutates": True,
                            "c_function": c_map.get(name),
                            "mapping_status": "mapped" if name in c_map else "unmapped",
                            "didactic_source": "c" if c_operation_code.get(name) else "fallback_or_derived",
                            "tests": _test_references(name),
                        }
                    )
            public_names = {row["name"] for row in operation_rows}
            orphan_mappings = sorted(name for name in c_map if name not in public_names)
            structures.append(
                {
                    "id": structure_id,
                    "family": family,
                    "adapter": f"{adapter_class.__module__}.{adapter_class.__name__}",
                    "trace_strategy": strategy.__class__.__name__,
                    "renderer": RENDERERS[family],
                    "endpoints": ENDPOINTS[family],
                    "c_sources": list(C_SOURCES[structure_id]),
                    "operations": operation_rows,
                    "orphan_c_mappings": orphan_mappings,
                }
            )
    unmapped = [
        f"{structure['id']}::{operation['name']}"
        for structure in structures
        for operation in structure["operations"]
        if operation["mapping_status"] == "unmapped"
    ]
    return {
        "schema": SCHEMA_VERSION,
        "structures_count": len(structures),
        "operations_count": sum(len(item["operations"]) for item in structures),
        "structures": structures,
        "gaps": {
            "unmapped_public_operations": unmapped,
            "fallback_or_derived_operations": [
                f"{structure['id']}::{operation['name']}"
                for structure in structures
                for operation in structure["operations"]
                if operation["didactic_source"] != "c"
            ],
            "orphan_c_mappings": {
                item["id"]: item["orphan_c_mappings"]
                for item in structures
                if item["orphan_c_mappings"]
            },
        },
    }


def render_markdown(inventory: dict[str, Any]) -> str:
    """Render a compact human-readable coverage matrix."""
    lines = [
        "# Inventario QA de fidelidad didáctica C",
        "",
        f"Esquema: `{inventory['schema']}`.",
        f"Cobertura descubierta: **{inventory['structures_count']} estructuras** y "
        f"**{inventory['operations_count']} operaciones/algoritmos**.",
        "",
        "| Familia | TAD | Operación/algoritmo | Mutación | Función C | Fuente didáctica | Estrategia | Renderer | Tests existentes |",
        "|---|---|---|---:|---|---|---|---|---:|",
    ]
    for structure in inventory["structures"]:
        for operation in structure["operations"]:
            lines.append(
                "| {family} | `{sid}` | `{operation}` | {mutates} | `{c_function}` | `{source}` | "
                "`{strategy}` | `{renderer}` | {tests} |".format(
                    family=structure["family"], sid=structure["id"],
                    operation=operation["name"], mutates="sí" if operation["mutates"] else "no",
                    c_function=operation["c_function"] or "SIN_MAPEO",
                    source=operation["didactic_source"],
                    strategy=structure["trace_strategy"], renderer=structure["renderer"]["function"],
                    tests=len(operation["tests"]),
                )
            )
    lines.extend(["", "## Huecos detectados", ""])
    gaps = inventory["gaps"]["unmapped_public_operations"]
    lines.append("Operaciones públicas sin mapeo C: " + (", ".join(f"`{item}`" for item in gaps) if gaps else "ninguna."))
    lines.append("")
    lines.append("Los mapeos C huérfanos se conservan en el JSON para revisión y clasificación explícita.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", default="docs/qa/didactic-c-trace-inventory.json")
    parser.add_argument("--markdown", default="docs/qa/didactic-c-trace-inventory.md")
    args = parser.parse_args()
    inventory = build_inventory()
    json_path = ROOT / args.json
    markdown_path = ROOT / args.markdown
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(inventory), encoding="utf-8")
    print(f"{inventory['structures_count']} structures; {inventory['operations_count']} operations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
