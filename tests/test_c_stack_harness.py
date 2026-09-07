"""Compilation and protocol tests for the non-interactive C stack harness."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "tests" / "conformance" / "c_harnesses"
C_TADS = ROOT / "docs" / "tads_C"


def test_harness_manifest_registers_exactly_thirteen_tads() -> None:
    manifest = json.loads((HARNESS / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest["structures"]) == 13
    assert manifest["structures"]["stack"] == "stack_harness.c"


def test_stack_harness_emits_canonical_state(tmp_path: Path) -> None:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.skip("gcc no está instalado")
    executable = tmp_path / "stack_harness.exe"
    compile_result = subprocess.run(
        [gcc, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-I", str(C_TADS), "-I", str(HARNESS), str(HARNESS / "stack_harness.c"), str(C_TADS / "tad_pila.c"), "-o", str(executable)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    run = subprocess.run([str(executable), "push", "1", "push", "2", "pop", "push", "3"], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    state = json.loads(run.stdout)
    assert state["state"] == {"values": [3, 1], "size": 2}


@pytest.mark.parametrize(
    ("name", "source", "tad_source", "arguments", "expected"),
    [
        ("queue", "queue_harness.c", "tad_cola.c", ["enqueue", "4", "enqueue", "7", "dequeue"], {"values": [7], "size": 1}),
        ("sorting", "sorting_harness.c", "tad_ordenamiento.c", ["quick", "5", "-1", "3", "3"], {"values": [-1, 3, 3, 5], "size": 4}),
        ("linked_list", "linked_list_harness.c", "tad_lista.c", ["append", "2", "prepend", "1", "append", "3", "remove", "2"], {"values": [1, 3], "size": 2}),
        ("circular_list", "circular_list_harness.c", "tad_lista_circular.c", ["append", "1", "append", "2", "append", "3", "reverse"], {"values": [3, 2, 1], "size": 3}),
        ("priority_queue", "priority_queue_harness.c", "tad_cola_prioridad.c", ["enqueue", "10", "3", "enqueue", "20", "1", "enqueue", "30", "2"], {"items": [{"value": 10, "priority": 3}, {"value": 20, "priority": 1}, {"value": 30, "priority": 2}], "size": 3}),
        ("sublist", "sublist_harness.c", "tad_sublista.c", ["add_parent", "1", "add_child", "1", "8", "add_child", "1", "9", "add_parent", "2"], {"parents": [{"parent": 1, "children": [8, 9]}, {"parent": 2, "children": []}], "size": 2}),
        ("binary_heap", "binary_heap_harness.c", "tad_monticulo_binario.c", ["insert", "5", "insert", "1", "insert", "3", "extract"], {"values": [3, 5], "size": 2}),
        ("abb", "abb_harness.c", "tad_abb.c", ["insert", "2", "insert", "1", "insert", "3", "remove", "2"], {"inorder": [1, 3], "preorder": [3, 1], "shape": [3, [1, None, None], None], "size": 2}),
        ("avl", "avl_harness.c", "tad_avl.c", ["insert", "30", "insert", "20", "insert", "10"], {"inorder": [10, 20, 30], "preorder": [20, 10, 30], "shape": [20, [10, None, None], [30, None, None]], "size": 3}),
        ("red_black", "red_black_harness.c", "tad_rojo_negro.c", ["insert", "10", "insert", "20", "insert", "30"], {"inorder": [10, 20, 30], "preorder": [20, 10, 30], "shape": [20, [10, None, None], [30, None, None]], "size": 3}),
        ("graph", "graph_harness.c", "tad_grafo.c", ["add_vertex", "2", "add_vertex", "1", "add_edge", "1", "2", "7"], {"directed": True, "vertices": ["1", "2"], "edges": [["1", "2", 7]]}),
        ("hash_table", "hash_table_harness.c", "tad_tabla_hash.c", ["put", "2", "20", "put", "1", "10", "put", "2", "22"], {"pairs": [[1, "10"], [2, "22"]], "size": 2, "capacity": 17}),
    ],
)
def test_additional_harnesses_emit_canonical_state(
    tmp_path: Path,
    name: str,
    source: str,
    tad_source: str,
    arguments: list[str],
    expected: dict[str, object],
) -> None:
    gcc = shutil.which("gcc")
    if gcc is None:
        pytest.skip("gcc no está instalado")
    executable = tmp_path / f"{name}_harness.exe"
    tad_sources = [str(C_TADS / tad_source)]
    if name == "graph":
        tad_sources.append(str(C_TADS / "tad_cola.c"))
    compile_result = subprocess.run(
        [gcc, "-std=c17", "-Wall", "-Wextra", "-Wpedantic", "-Werror", "-I", str(C_TADS), "-I", str(HARNESS), str(HARNESS / source), *tad_sources, "-o", str(executable)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert compile_result.returncode == 0, compile_result.stderr
    run = subprocess.run([str(executable), *arguments], capture_output=True, text=True, check=False)
    assert run.returncode == 0, run.stderr
    canonical_line = next(line for line in reversed(run.stdout.splitlines()) if line.strip())
    assert json.loads(canonical_line)["state"] == expected
