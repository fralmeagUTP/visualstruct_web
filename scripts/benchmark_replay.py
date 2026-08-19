"""Measure deterministic replay cost for representative structure families."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.graph_structure_service import GraphStructureService
from app.services.hash_structure_service import HashStructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.sorting_structure_service import SortingStructureService
from app.services.structure_service import StructureService


HistoryFactory = Callable[[int], list[dict[str, Any]]]
Replay = Callable[[str, list[dict[str, Any]]], tuple[Any, list[dict[str, Any]]]]

CASES: dict[str, tuple[Replay, str, HistoryFactory]] = {
    "sequential": (StructureService._rebuild_adapter, "stack", lambda n: [{"operation": "apilar", "payload": {"value": i}} for i in range(n)]),
    "tree": (HierarchicalStructureService._rebuild_adapter, "avl", lambda n: [{"operation": "insertar", "payload": {"value": i}} for i in range(n)]),
    "graph": (GraphStructureService._rebuild_adapter, "graph", lambda n: [{"operation": "insert_vertex", "payload": {"vertex": i}} for i in range(n)]),
    "hash": (HashStructureService._rebuild_adapter, "hash_table", lambda n: [{"operation": "insert", "payload": {"key": str(i), "value": str(i)}} for i in range(n)]),
    "sorting": (SortingStructureService._rebuild_adapter, "sorting_array", lambda n: [{"operation": "create_array", "payload": {"values": f"{i},{i + 1}"}} for i in range(n)]),
}


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(len(ordered) * fraction) - 1))
    return ordered[index]


def run(iterations: int) -> dict[str, Any]:
    results: dict[str, Any] = {}
    for family, (rebuild, structure_id, factory) in CASES.items():
        family_results: dict[str, Any] = {}
        for count in (1, 50, 150, 300):
            history = factory(count)
            samples: list[float] = []
            rebuild(structure_id, history)
            for _ in range(iterations):
                started = time.perf_counter_ns()
                _, valid = rebuild(structure_id, history)
                samples.append((time.perf_counter_ns() - started) / 1_000_000)
                if len(valid) != count:
                    raise RuntimeError(f"{family}: replay validó {len(valid)} de {count} operaciones")
            family_results[str(count)] = {
                "median_ms": round(statistics.median(samples), 3),
                "p95_ms": round(percentile(samples, 0.95), 3),
            }
        results[family] = family_results
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "iterations": iterations,
        "environment": "Python 3.10.5, Windows, baseline sin checkpoints",
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.iterations)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()
