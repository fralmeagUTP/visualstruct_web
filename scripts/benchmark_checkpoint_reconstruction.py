"""Benchmark worst-case reconstruction with checkpoints enabled."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import statistics
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.benchmark_replay import CASES, percentile


HISTORY_SIZE = 300
DEFAULT_BUDGET_MS = 200.0


def run(*, iterations: int, budget_ms: float = DEFAULT_BUDGET_MS) -> dict[str, Any]:
    """Measure full replay, the safe worst case when no checkpoint is usable."""
    if iterations <= 0:
        raise ValueError("iterations debe ser mayor que cero")
    if budget_ms <= 0:
        raise ValueError("budget_ms debe ser mayor que cero")

    results: dict[str, Any] = {}
    for family, (rebuild, structure_id, factory) in CASES.items():
        history = factory(HISTORY_SIZE)
        rebuild(structure_id, history)  # warm-up outside measured samples
        samples: list[float] = []
        for _ in range(iterations):
            started = time.perf_counter_ns()
            _, valid_history = rebuild(structure_id, history)
            samples.append((time.perf_counter_ns() - started) / 1_000_000)
            if len(valid_history) != HISTORY_SIZE:
                raise RuntimeError(
                    f"{family}: replay valido {len(valid_history)} de {HISTORY_SIZE} operaciones"
                )

        p95_ms = percentile(samples, 0.95)
        results[family] = {
            "history_operations": HISTORY_SIZE,
            "replay_operations": HISTORY_SIZE,
            "checkpoint_enabled": True,
            "checkpoint_used": False,
            "fallback_reason": "missing",
            "median_ms": round(statistics.median(samples), 3),
            "p95_ms": round(p95_ms, 3),
            "budget_ms": budget_ms,
            "passed": p95_ms < budget_ms,
        }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "iterations": iterations,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "mode": "checkpoints enabled; missing checkpoint forces worst-case full replay",
        },
        "budget_ms": budget_ms,
        "passed": all(result["passed"] for result in results.values()),
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--budget-ms", type=float, default=DEFAULT_BUDGET_MS)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = run(iterations=args.iterations, budget_ms=args.budget_ms)
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
