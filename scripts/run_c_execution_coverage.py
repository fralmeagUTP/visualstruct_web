"""Observe real C lines and branches with compiler instrumentation."""

from __future__ import annotations

import argparse
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_c_conformance import CHECKS, HARNESS_DIR, TAD_DIR


SCHEMA = "didactic-c-execution-coverage/v1"


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, timeout=60, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"falló {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
    return completed


def _summarize_gcov(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        payload = json.load(stream)
    source = payload["files"][0]
    lines = source["lines"]
    functions = [
        {
            "name": function["name"],
            "start_line": function.get("start_line"),
            "end_line": function.get("end_line"),
            "execution_count": function.get("execution_count", 0),
            "blocks": function.get("blocks", 0),
            "blocks_executed": function.get("blocks_executed", 0),
        }
        for function in source.get("functions", [])
    ]
    branches = [
        {
            "line": line["line_number"],
            "branch": index,
            "count": branch["count"],
            "taken": branch["count"] > 0,
            "fallthrough": branch.get("fallthrough", False),
            "throw": branch.get("throw", False),
        }
        for line in lines
        for index, branch in enumerate(line.get("branches", []))
    ]
    executed_lines = [line["line_number"] for line in lines if line["count"] > 0]
    calls = [
        {"line": line["line_number"], "count": call.get("returned", call.get("count", 0))}
        for line in lines for call in line.get("calls", [])
    ]
    conditions = [
        {"line": line["line_number"], **condition}
        for line in lines for condition in line.get("conditions", [])
    ]
    return {
        "source": Path(source["file"]).as_posix(),
        "executable_lines": len(lines),
        "executed_lines": executed_lines,
        "line_counts": {str(line["line_number"]): line["count"] for line in lines if line["count"] > 0},
        "functions": functions,
        "calls": calls,
        "conditions": conditions,
        "branches": branches,
        "branches_total": len(branches),
        "branches_taken": sum(1 for branch in branches if branch["taken"]),
    }


def collect_execution_coverage(*, compiler: str, gcov: str, selected: set[str] | None = None) -> dict[str, Any]:
    """Compile and run selected harnesses, returning real line/branch counts."""
    ids = sorted(selected or CHECKS)
    unknown = set(ids) - set(CHECKS)
    if unknown:
        raise ValueError(f"TAD no registrado: {', '.join(sorted(unknown))}")
    manifest = json.loads((HARNESS_DIR / "manifest.json").read_text(encoding="utf-8"))["structures"]
    results: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="visualestruct-c-gcov-") as directory:
        work = Path(directory)
        for structure_id in ids:
            check = CHECKS[structure_id]
            executable = work / (f"{structure_id}.exe" if os.name == "nt" else structure_id)
            sources = [TAD_DIR / source for source in check.tad_sources]
            _run([
                compiler, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror",
                "--coverage", "-fcondition-coverage", "-O0", "-I", str(TAD_DIR), "-I", str(HARNESS_DIR),
                str(HARNESS_DIR / manifest[structure_id]), *(str(source) for source in sources),
                "-o", str(executable),
            ], cwd=ROOT)
            environment = os.environ.copy()
            environment["VISUALESTRUCT_QA_EVENTS"] = "1"
            _run([str(executable), *check.arguments], cwd=work, env=environment)
            source_reports: list[dict[str, Any]] = []
            for source in sources:
                notes = work / f"{structure_id}-{source.stem}.gcno"
                _run([gcov, "-j", "-b", "-c", "-g", "-o", str(work), str(notes)], cwd=work)
                report_path = work / f"{structure_id}-{source.stem}.gcov.json.gz"
                source_reports.append(_summarize_gcov(report_path))
            results.append({
                "structure_id": structure_id,
                "arguments": list(check.arguments),
                "sources": source_reports,
                "executed_lines": sum(len(report["executed_lines"]) for report in source_reports),
                "branches_total": sum(report["branches_total"] for report in source_reports),
                "branches_taken": sum(report["branches_taken"] for report in source_reports),
            })
    return {"schema": SCHEMA, "structures_count": len(results), "structures": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default=shutil.which("gcc") or "gcc")
    parser.add_argument("--gcov", default=shutil.which("gcov") or "gcov")
    parser.add_argument("--only", action="append", choices=sorted(CHECKS))
    parser.add_argument("--output", default="docs/qa/c-execution-coverage.json")
    args = parser.parse_args()
    report = collect_execution_coverage(
        compiler=args.compiler, gcov=args.gcov, selected=set(args.only) if args.only else None
    )
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{report['structures_count']} structures observed with gcov")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
