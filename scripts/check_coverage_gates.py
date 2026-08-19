"""Enforce global and critical-component coverage thresholds."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


GLOBAL_MINIMUM = 83.0
COMPONENT_MINIMUMS = {
    "app/domain/sorting/tad_ordenamiento.py": 85.0,
    "app/domain/graph/tad_grafo.py": 85.0,
    "app/domain/hash/tad_tabla_hash.py": 85.0,
    "app/domain/hierarchical/tad_monticulo_binario.py": 85.0,
}


def _percentage(summary: dict[str, Any]) -> float:
    statements = int(summary.get("num_statements", 0))
    covered = int(summary.get("covered_lines", 0))
    return 100.0 if statements == 0 else covered * 100.0 / statements


def evaluate(report: dict[str, Any]) -> list[str]:
    """Return human-readable gate failures; an empty list means success."""
    failures: list[str] = []
    totals = report.get("totals")
    files = report.get("files")
    if not isinstance(totals, dict) or not isinstance(files, dict):
        return ["El reporte de cobertura no contiene 'totals' y 'files' validos."]

    global_percentage = _percentage(totals)
    if global_percentage < GLOBAL_MINIMUM:
        failures.append(
            f"Cobertura global {global_percentage:.2f}% < {GLOBAL_MINIMUM:.2f}%."
        )

    normalized_files = {
        str(path).replace("\\", "/"): details for path, details in files.items()
    }
    for component, minimum in COMPONENT_MINIMUMS.items():
        details = normalized_files.get(component)
        if not isinstance(details, dict) or not isinstance(details.get("summary"), dict):
            failures.append(f"Componente ausente del reporte: {component}.")
            continue
        percentage = _percentage(details["summary"])
        if percentage < minimum:
            failures.append(f"{component}: {percentage:.2f}% < {minimum:.2f}%.")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=Path("coverage.json"))
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        print(f"No se pudo leer el reporte de cobertura: {error}")
        return 2

    failures = evaluate(report)
    if failures:
        print("Coverage gates fallidos:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        f"Coverage gates aprobados: global >= {GLOBAL_MINIMUM:.0f}% y "
        f"{len(COMPONENT_MINIMUMS)} componentes >= 85%."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
