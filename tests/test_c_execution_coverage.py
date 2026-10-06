"""Tests for compiler-observed C execution paths."""

from __future__ import annotations

from scripts.run_c_execution_coverage import SCHEMA, collect_execution_coverage


def test_gcov_observes_real_stack_lines_and_branches() -> None:
    report = collect_execution_coverage(compiler="gcc", gcov="gcov", selected={"stack"})
    assert report["schema"] == SCHEMA
    assert report["structures_count"] == 1
    stack = report["structures"][0]
    assert stack["structure_id"] == "stack"
    assert stack["executed_lines"] > 0
    assert stack["branches_total"] > 0
    assert 0 < stack["branches_taken"] <= stack["branches_total"]
    source = stack["sources"][0]
    assert source["source"].endswith("docs/tads_C/tad_pila.c")
    assert source["line_counts"]
    functions = {function["name"]: function for function in source["functions"]}
    assert functions["pila_apilar"]["execution_count"] == 2
    assert functions["pila_desapilar"]["execution_count"] == 1
    assert source["calls"]
