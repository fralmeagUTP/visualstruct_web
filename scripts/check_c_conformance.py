"""Compile and execute every C conformance harness with strict flags."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS_DIR = ROOT / "tests" / "conformance" / "c_harnesses"
TAD_DIR = ROOT / "docs" / "tads_C"


@dataclass(frozen=True)
class HarnessCheck:
    tad_sources: tuple[str, ...]
    arguments: tuple[str, ...]


CHECKS: dict[str, HarnessCheck] = {
    "linked_list": HarnessCheck(("tad_lista.c",), (
        "append", "2", "prepend", "1", "append", "2", "insert_at", "9", "2",
        "search", "2", "remove", "9", "remove_all", "2",
    )),
    "stack": HarnessCheck(("tad_pila.c",), ("empty", "push", "1", "push", "2", "peek", "pop", "clear", "empty")),
    "queue": HarnessCheck(("tad_cola.c",), ("empty", "enqueue", "1", "front", "rear", "dequeue", "empty", "enqueue", "2", "enqueue", "3", "front", "rear", "dequeue", "clear", "empty")),
    "priority_queue": HarnessCheck(("tad_cola_prioridad.c",), (
        "empty", "enqueue", "100", "0", "enqueue", "200", "-2147483648",
        "enqueue", "300", "0", "enqueue", "400", "2147483647", "peek",
        "dequeue", "dequeue", "dequeue", "dequeue", "empty", "clear",
    )),
    "circular_list": HarnessCheck(("tad_lista_circular.c",), (
        "append", "1", "search", "1", "remove", "1", "prepend", "2",
        "append", "3", "append", "2", "search", "2", "reverse", "remove", "3", "clear",
    )),
    "sublist": HarnessCheck(("tad_sublista.c",), (
        "add_parent", "1", "add_child", "1", "10", "add_parent", "1",
        "add_parent", "2", "add_child", "2", "20", "get_children", "1",
        "remove_child", "1", "10", "remove_parent", "1", "get_children", "1", "clear",
    )),
    "abb": HarnessCheck(("tad_abb.c",), (
        "insert", "5", "insert", "3", "insert", "7", "insert", "6", "insert", "8",
        "insert", "6", "search", "6", "search", "99", "min", "0", "max", "0",
        "remove", "8", "remove", "7", "remove", "5",
    )),
    "avl": HarnessCheck(("tad_avl.c",), (
        "insert", "30", "insert", "20", "insert", "10", "root", "clear",
        "insert", "10", "insert", "20", "insert", "30", "root", "clear",
        "insert", "30", "insert", "10", "insert", "20", "root", "clear",
        "insert", "10", "insert", "30", "insert", "20", "root", "clear",
        "insert", "20", "insert", "10", "insert", "30", "insert", "5",
        "remove", "30", "root", "clear",
    )),
    "red_black": HarnessCheck(("tad_rojo_negro.c",), (
        "insert", "30", "insert", "20", "insert", "10", "root", "clear",
        "insert", "10", "insert", "20", "insert", "30", "root", "clear",
        "insert", "30", "insert", "10", "insert", "20", "root", "clear",
        "insert", "10", "insert", "30", "insert", "20", "root", "clear",
        "insert", "10", "insert", "5", "insert", "15", "insert", "1", "root", "clear",
        "insert", "7", "insert", "3", "insert", "18", "insert", "10",
        "insert", "22", "insert", "8", "insert", "11", "insert", "26",
        "remove", "3", "remove", "10", "remove", "22", "clear",
    )),
    "binary_heap": HarnessCheck(("tad_monticulo_binario.c",), (
        "insert", "11", "insert", "10", "insert", "9", "insert", "8",
        "insert", "7", "insert", "6", "insert", "5", "insert", "4",
        "insert", "3", "insert", "2", "insert", "1", "root", "extract",
    )),
    "graph": HarnessCheck(("tad_grafo.c", "tad_cola.c"), (
        "empty", "add_edge", "9", "10", "5", "exists_edge", "9", "10",
        "weight", "9", "10", "order", "size", "add_vertex", "9",
        "add_vertex", "9", "order", "add_edge", "9", "10", "7", "size",
        "clear", "add_vertex", "1", "add_vertex", "2", "add_vertex", "3",
        "add_edge", "1", "2", "4", "exists_edge", "2", "1", "order", "size",
        "clear", "add_vertex", "1", "add_vertex", "2", "add_vertex", "3", "add_vertex", "4",
        "add_edge", "1", "2", "1", "add_edge", "2", "1", "1",
        "add_edge", "2", "3", "2", "add_edge", "3", "2", "2",
        "bfs", "1", "dfs", "1", "dijkstra", "1", "3", "bellman", "1", "3",
        "prim", "1", "kruskal", "add_edge", "1", "3", "-5", "dijkstra", "1", "3",
    )),
    "hash_table": HarnessCheck(("tad_tabla_hash.c",), (
        "put", "1", "10", "put", "18", "20", "put", "1", "11",
        "get", "1", "get", "99", "remove", "18",
    )),
    "sorting": HarnessCheck(("tad_ordenamiento.c",), (
        "radix", "-2147483648", "2147483647", "-1", "0", "7", "-2147483648", "7",
    )),
}


def _canonical_outputs(stdout: str) -> list[dict[str, object]]:
    """Return every canonical snapshot emitted in causal order."""
    return [
        json.loads(line)
        for line in stdout.splitlines()
        if line.strip().startswith('{"schema":"canonical-state/v1"')
    ]


def _canonical_output(stdout: str) -> dict[str, object]:
    outputs = _canonical_outputs(stdout)
    if outputs:
        return outputs[-1]
    raise RuntimeError("el harness no emitió JSON canónico")


def _printf_outputs(stdout: str) -> list[str]:
    """Capture program output while excluding canonical-state transport."""
    return [
        line for line in stdout.splitlines()
        if line and not line.strip().startswith('{"schema":"canonical-state/v1"')
    ]


def _qa_events(stderr: str) -> list[dict[str, object]]:
    """Parse the optional versioned NDJSON audit channel."""
    events: list[dict[str, object]] = []
    for line in stderr.splitlines():
        if line.startswith('{"schema":"didactic-c-event/v1"'):
            events.append(json.loads(line))
    return events


def run_checks(
    *, compiler: str, sanitizers: bool, only: set[str] | None = None,
    qa_events: bool = False,
) -> None:
    manifest = json.loads((HARNESS_DIR / "manifest.json").read_text(encoding="utf-8"))
    registered = manifest["structures"]
    if set(registered) != set(CHECKS) or any(not value for value in registered.values()):
        raise RuntimeError("manifiesto y matriz de verificación no cubren los mismos 13 TAD")

    with tempfile.TemporaryDirectory(prefix="visualestruct-c17-") as directory:
        output_dir = Path(directory)
        selected = sorted(only or CHECKS)
        unknown = set(selected) - set(CHECKS)
        if unknown:
            raise RuntimeError(f"TAD no registrado: {', '.join(sorted(unknown))}")
        for structure_id in selected:
            check = CHECKS[structure_id]
            executable = output_dir / structure_id
            flags = ["-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror"]
            if sanitizers:
                flags.extend(["-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-g"])
            command = [
                compiler,
                *flags,
                "-I", str(TAD_DIR),
                "-I", str(HARNESS_DIR),
                str(HARNESS_DIR / registered[structure_id]),
                *(str(TAD_DIR / source) for source in check.tad_sources),
                "-o", str(executable),
            ]
            try:
                compiled = subprocess.run(
                    command, capture_output=True, text=True, check=False, timeout=60
                )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"{structure_id}: compilación excedió 60 segundos"
                ) from error
            if compiled.returncode != 0:
                raise RuntimeError(f"{structure_id}: compilación fallida\n{compiled.stderr}")
            environment = os.environ.copy()
            if sanitizers:
                environment.update({"ASAN_OPTIONS": "detect_leaks=0:halt_on_error=1", "UBSAN_OPTIONS": "halt_on_error=1:print_stacktrace=1"})
            if qa_events:
                environment["VISUALESTRUCT_QA_EVENTS"] = "1"
            stdout_path = output_dir / f"{structure_id}.stdout"
            stderr_path = output_dir / f"{structure_id}.stderr"
            try:
                with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open(
                    "w", encoding="utf-8"
                ) as stderr_file:
                    executed = subprocess.run(
                        [str(executable), *check.arguments],
                        stdout=stdout_file,
                        stderr=stderr_file,
                        text=True,
                        check=False,
                        env=environment,
                        timeout=30,
                    )
            except subprocess.TimeoutExpired as error:
                raise RuntimeError(
                    f"{structure_id}: ejecución excedió 30 segundos"
                ) from error
            executed_stdout = stdout_path.read_text(encoding="utf-8")
            executed_stderr = stderr_path.read_text(encoding="utf-8")
            if executed.returncode != 0:
                raise RuntimeError(f"{structure_id}: ejecución fallida\n{executed_stderr}")
            state = _canonical_output(executed_stdout)
            if state.get("structure_id") != structure_id:
                raise RuntimeError(f"{structure_id}: identificador canónico incorrecto")
            if qa_events:
                events = _qa_events(executed_stderr)
                if not events or events[0].get("phase") != "begin" or events[-1].get("phase") != "end":
                    raise RuntimeError(f"{structure_id}: canal QA incompleto")
                if any(event.get("structure_id") != structure_id for event in events):
                    raise RuntimeError(f"{structure_id}: evento QA con identificador incorrecto")
                if [event.get("sequence") for event in events] != list(range(len(events))):
                    raise RuntimeError(f"{structure_id}: secuencia QA no contigua")
                operation_phases = {
                    event.get("phase") for event in events if event.get("event") == "operation"
                }
                if operation_phases != {"before", "after"}:
                    raise RuntimeError(f"{structure_id}: eventos de operación QA incompletos")
                if not any(event.get("event") == "free" for event in events):
                    raise RuntimeError(f"{structure_id}: liberación final no observada")
                if not any(event.get("event") == "allocation" for event in events):
                    raise RuntimeError(f"{structure_id}: dynamic allocation event missing")
                details = [str(event.get("detail")) for event in events]
                if structure_id == "binary_heap" and "reallocated heap backing array" not in details:
                    raise RuntimeError("binary_heap: backing-array growth was not observed")
                if structure_id == "binary_heap" and "root=1" not in details:
                    raise RuntimeError("binary_heap: exact root query return was not observed")
                if structure_id == "stack":
                    for expected in ("empty=1", "top=2", "value=2"):
                        if expected not in details:
                            raise RuntimeError(f"stack: missing exact LIFO observation {expected}")
                if structure_id == "queue":
                    for expected in ("front=1", "rear=1", "value=1", "front=2", "rear=3"):
                        if expected not in details:
                            raise RuntimeError(f"queue: missing exact FIFO observation {expected}")
                    if "rear set to NULL after removing last node" not in details:
                        raise RuntimeError("queue: last-node rear reset was not observed")
                if structure_id == "priority_queue":
                    returned_values = [detail for event, detail in zip(events, details) if event.get("event") == "return" and detail.startswith("value=")]
                    if returned_values != ["value=100", "value=200", "value=100", "value=300", "value=400"]:
                        raise RuntimeError(f"priority_queue: unstable C priority order {returned_values}")
                if structure_id == "linked_list":
                    for expected in ("matches=2", "removed=2"):
                        if expected not in details:
                            raise RuntimeError(f"linked_list: missing observation {expected}")
                if structure_id == "circular_list":
                    returned_matches = [detail for event, detail in zip(events, details) if event.get("event") == "return" and detail.startswith("matches=")]
                    if returned_matches != ["matches=1", "matches=2"]:
                        raise RuntimeError(f"circular_list: incorrect bounded search {returned_matches}")
                if structure_id == "sublist":
                    for expected in ("children=1", "removed_child=1", "removed_parent=1", "children=0"):
                        if expected not in details:
                            raise RuntimeError(f"sublist: missing hierarchical observation {expected}")
                if structure_id == "abb":
                    for expected in ("found=1", "found=0", "min=3", "max=8"):
                        if expected not in details:
                            raise RuntimeError(f"abb: missing query observation {expected}")
                if structure_id == "avl":
                    roots = [
                        detail for event, detail in zip(events, details)
                        if event.get("event") == "return" and detail.startswith("root=")
                    ]
                    if roots != ["root=20", "root=20", "root=20", "root=20", "root=10"]:
                        raise RuntimeError(f"avl: incorrect LL/RR/LR/RL/delete roots {roots}")
                if structure_id == "red_black":
                    roots = [
                        detail for event, detail in zip(events, details)
                        if event.get("event") == "return" and detail.startswith("root=")
                    ]
                    if roots != ["root=20", "root=20", "root=20", "root=20", "root=10"]:
                        raise RuntimeError(f"red_black: incorrect rotation/recolor roots {roots}")
                if structure_id == "graph":
                    returns = [detail for event, detail in zip(events, details) if event.get("event") == "return"]
                    expected = [
                        "empty=1", "exists_edge=1", "weight=5", "order=2", "size=1",
                        "order=2", "size=1", "exists_edge=0", "order=3", "size=1",
                        "bfs=1,2,3", "dfs=1,2,3", "dijkstra_edges=2,cost=3",
                        "bellman_edges=2,cost=3", "prim_edges=2,cost=3",
                        "kruskal_edges=2,cost=3", "dijkstra_edges=0,cost=0",
                    ]
                    if returns != expected:
                        raise RuntimeError(f"graph: incorrect construction/query observations {returns}")
                if structure_id == "sorting":
                    if state.get("state", {}).get("values") != [
                        -2147483648, -2147483648, -1, 0, 7, 7, 2147483647,
                    ]:
                        raise RuntimeError(f"sorting/radix: INT_MIN boundary order is incorrect {state}")
                    algorithms = (
                        "exchange", "selection", "insertion", "bubble", "shell", "quick",
                        "merge", "heap", "counting", "bin", "radix",
                    )
                    for algorithm_name in algorithms:
                        matrix_run = subprocess.run(
                            [str(executable), algorithm_name, "5", "-1", "4", "2", "2", "0"],
                            capture_output=True, text=True, check=False, env=environment, timeout=30,
                        )
                        if matrix_run.returncode != 0:
                            raise RuntimeError(f"sorting/{algorithm_name}: execution failed\n{matrix_run.stderr}")
                        matrix_state = _canonical_output(matrix_run.stdout).get("state", {})
                        if matrix_state.get("values") != [-1, 0, 2, 2, 4, 5]:
                            raise RuntimeError(f"sorting/{algorithm_name}: incorrect final order {matrix_state}")
                        matrix_events = _qa_events(matrix_run.stderr)
                        if algorithm_name in {"merge", "counting", "bin", "radix"} and not any(
                            event.get("event") == "return" and event.get("detail") == "status=1"
                            for event in matrix_events
                        ):
                            raise RuntimeError(f"sorting/{algorithm_name}: success return was not observed")
                    for algorithm_name in ("counting", "bin"):
                        rejected = subprocess.run(
                            [str(executable), algorithm_name, "-2147483648", "2147483647"],
                            capture_output=True, text=True, check=False, env=environment, timeout=30,
                        )
                        if rejected.returncode != 0:
                            raise RuntimeError(f"sorting/{algorithm_name}: bounded rejection execution failed")
                        rejected_events = _qa_events(rejected.stderr)
                        if not any(event.get("event") == "return" and event.get("detail") == "status=0" for event in rejected_events):
                            raise RuntimeError(f"sorting/{algorithm_name}: excessive range was not rejected before allocation")
                if structure_id == "hash_table" and any("rehash" in detail for detail in details):
                    raise RuntimeError("hash_table: the fixed-capacity C TAD cannot report rehash")
                if structure_id == "hash_table":
                    returns = [detail for event, detail in zip(events, details) if event.get("event") == "return"]
                    for expected in ("found=1", "value=11", "found=0"):
                        if expected not in returns:
                            raise RuntimeError(f"hash_table: missing exact lookup return {expected}")
                snapshots = [event for event in events if event.get("event") == "snapshot"]
                canonical_outputs = _canonical_outputs(executed_stdout)
                if not snapshots or len(canonical_outputs) < len(snapshots):
                    raise RuntimeError(f"{structure_id}: snapshots canónicos QA incompletos")
                if structure_id != "sorting" and len(canonical_outputs) != len(snapshots) + 1:
                    raise RuntimeError(f"{structure_id}: estado final no sigue a snapshots intermedios")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compiler", default=shutil.which("gcc") or "gcc")
    parser.add_argument("--sanitizers", action="store_true")
    parser.add_argument("--qa-events", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--only", action="append", choices=sorted(CHECKS))
    args = parser.parse_args()
    if args.list:
        print("\n".join(sorted(CHECKS)))
        return 0
    run_checks(
        compiler=args.compiler,
        sanitizers=args.sanitizers,
        only=set(args.only) if args.only else None,
        qa_events=args.qa_events,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
