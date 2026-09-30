"""Run deterministic generated QA sequences without changing product state."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import random
import subprocess
import sys
from typing import Callable, TypeVar

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.adapters.graph_adapter import GraphAdapter
from app.adapters.stack_adapter import StackAdapter
from app.domain.hash.tad_wrappers import TablaHash
from app.domain.hierarchical.tad_wrappers import AVL
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS, SortingInterpreter


T = TypeVar("T")
FAMILY_SEEDS = {
    "sequential": 810_001,
    "hierarchical": 820_001,
    "graph": 830_001,
    "hash": 840_001,
    "sorting": 850_001,
}


def ddmin(items: list[T], still_fails: Callable[[list[T]], bool]) -> list[T]:
    """Reduce a failing operation list using deterministic delta debugging."""
    current = list(items)
    granularity = 2
    while len(current) >= 2:
        chunk_size = (len(current) + granularity - 1) // granularity
        reduced = False
        for start in range(0, len(current), chunk_size):
            candidate = current[:start] + current[start + chunk_size:]
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


def _audit_sequential(seed: int) -> None:
    rng = random.Random(seed); adapter = StackAdapter(); model: list[int] = []
    for _ in range(24):
        if not model or rng.random() < 0.65:
            value = rng.randint(-50, 50); adapter.execute("apilar", {"value": value}); model.insert(0, value)
        else:
            assert adapter.execute("desapilar", {})["result"] == model.pop(0)
        state = adapter.to_visual_state(); assert [item["value"] for item in state["items"]] == model; assert state["size"] == len(model)


def _audit_hierarchical(seed: int) -> None:
    rng = random.Random(seed); tree = AVL[int](); model: set[int] = set()
    for _ in range(24):
        value = rng.randint(-60, 60)
        if value not in model and (not model or rng.random() < 0.65): tree.insertar(value); model.add(value)
        elif value in model: tree.eliminar(value); model.remove(value)
        assert tree.inorden() == sorted(model); assert tree.validar(); assert tree.tamano() == len(model)


def _audit_graph(seed: int) -> None:
    rng = random.Random(seed); adapter = GraphAdapter(); adapter.execute("create_graph", {"directed": True})
    vertices: set[int] = set(); edges: dict[tuple[int, int], int] = {}
    for _ in range(18):
        if rng.random() < 0.35:
            vertex = rng.randint(0, 12); adapter.execute("insert_vertex", {"vertex": vertex}); vertices.add(vertex)
        else:
            origin, target, weight = rng.randint(0, 12), rng.randint(0, 12), rng.randint(-5, 15)
            adapter.execute("insert_edge", {"origin": origin, "target": target, "weight": weight})
            vertices.update((origin, target)); edges[(origin, target)] = weight
        state = adapter.to_visual_state()
        assert {int(node["id"]) for node in state["nodes"]} == vertices
        assert {(int(edge["source"]), int(edge["target"])): int(edge["weight"]) for edge in state["edges"]} == edges


def _audit_hash(seed: int) -> None:
    rng = random.Random(seed); table = TablaHash[int, int](17); model: dict[int, int] = {}
    for _ in range(24):
        key = rng.randint(-30, 30)
        if rng.random() < 0.7:
            value = rng.randint(-100, 100); table.insertar(key, value); model[key] = value
        else:
            assert table.eliminar(key) == (key in model); model.pop(key, None)
        assert table.tamano() == len(model)
        for expected_key, expected_value in model.items(): assert table.buscar(expected_key) == expected_value


def _audit_sorting(seed: int) -> None:
    rng = random.Random(seed); size = rng.randint(1, 18); values = [rng.randint(-80, 80) for _ in range(size)]
    algorithm = rng.choice([item["id"] for item in SORTING_ALGORITHMS])
    result = SortingInterpreter(values, algorithm).run()["final_state"]["items"]
    assert result == sorted(values); assert Counter(result) == Counter(values)


AUDITORS = {
    "sequential": _audit_sequential,
    "hierarchical": _audit_hierarchical,
    "graph": _audit_graph,
    "hash": _audit_hash,
    "sorting": _audit_sorting,
}


def _minimized_findings() -> list[dict[str, object]]:
    findings = []
    for path in sorted((ROOT / "docs" / "qa" / "findings").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        findings.append({"case_id": data["case_id"], "minimal_input": data.get("input"), "reducer": "documented-minimal-or-ddmin"})
    return findings


def _product_logic_changes() -> list[str]:
    run = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, capture_output=True, text=True, check=False)
    return [line for line in run.stdout.splitlines() if line.startswith(("app/", "static/", "templates/"))]


def run_audit(sequences: int) -> dict[str, object]:
    product_changes_before = set(_product_logic_changes())
    families = {}
    for family, auditor in AUDITORS.items():
        base_seed = FAMILY_SEEDS[family]; failures = []
        for offset in range(sequences):
            seed = base_seed + offset
            try: auditor(seed)
            except Exception as error: failures.append({"seed": seed, "error": f"{type(error).__name__}: {error}"})
        families[family] = {"base_seed": base_seed, "last_seed": base_seed + sequences - 1, "sequences": sequences, "failures": failures}
    return {
        "schema": "didactic-generated-audit/v1",
        "families": families,
        "total_sequences": sequences * len(AUDITORS),
        "minimized_findings": _minimized_findings(),
        "product_logic_changes": sorted(set(_product_logic_changes()) - product_changes_before),
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--sequences", type=int, default=1000); parser.add_argument("--output", type=Path)
    args = parser.parse_args(); report = run_audit(args.sequences)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output: args.output.write_text(text, encoding="utf-8")
    else: print(text, end="")
    if any(item["failures"] for item in report["families"].values()): return 1
    if report["product_logic_changes"]: return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
