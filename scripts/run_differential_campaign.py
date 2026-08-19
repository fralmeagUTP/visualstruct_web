"""Run a reproducible 1,000-sequence campaign for each structure family."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.conformance.generated import generate_scenario
from app.services.conformance.runner import CompiledConformanceRunner


FAMILIES: dict[str, tuple[str, ...]] = {
    "sequential": (
        "stack", "queue", "linked_list", "circular_list", "priority_queue", "sublist"
    ),
    "hierarchical": ("binary_heap", "abb", "avl", "red_black"),
    "graph": ("graph",),
    "hash": ("hash_table",),
    "sorting": ("sorting",),
}


def run_campaign(*, sequences: int, length: int, base_seed: int) -> dict:
    if sequences < 1:
        raise ValueError("sequences debe ser positivo")
    started = perf_counter()
    family_results: dict[str, dict] = {}
    with CompiledConformanceRunner() as runner:
        runner.compile_all()
        for family_index, (family, structures) in enumerate(FAMILIES.items()):
            counts = {structure_id: 0 for structure_id in structures}
            family_started = perf_counter()
            for index in range(sequences):
                structure_id = structures[index % len(structures)]
                seed = base_seed + family_index * 1_000_000 + index
                operations = generate_scenario(structure_id, seed=seed, length=length)
                result = runner.compare(structure_id, operations)
                if not result.equivalent:
                    raise RuntimeError(
                        f"divergencia family={family} structure={structure_id} seed={seed}"
                    )
                counts[structure_id] += 1
            family_results[family] = {
                "sequences": sequences,
                "divergences": 0,
                "structures": counts,
                "duration_seconds": round(perf_counter() - family_started, 3),
            }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_seed": base_seed,
        "sequence_length": length,
        "sequences_per_family": sequences,
        "total_sequences": sequences * len(FAMILIES),
        "divergences": 0,
        "duration_seconds": round(perf_counter() - started, 3),
        "families": family_results,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sequences", type=int, default=1000)
    parser.add_argument("--length", type=int, default=5)
    parser.add_argument("--base-seed", type=int, default=20260819)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.sequences < 1000:
        raise SystemExit("la campaña de cierre requiere al menos 1000 secuencias por familia")
    report = run_campaign(
        sequences=args.sequences,
        length=args.length,
        base_seed=args.base_seed,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
