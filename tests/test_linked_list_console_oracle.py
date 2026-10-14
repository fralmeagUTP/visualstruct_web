"""Positive and corrupted-console controls, without new runtime cases."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from _linked_list_console_oracle import assert_lista_console

FIXTURES = Path(__file__).resolve().parents[1] / "openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-linked-list-console-consumers-low/console-reopen/positive-fixtures.json"

from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize("operation", ["buscar_elemento", "eliminar_repetidos"])
@pytest.mark.parametrize("mutation", [None, "truncate", "duplicate", "late", "missing", "wrong_source", "leading"])
def test_exact_console_controls(operation, mutation):
    steps = deepcopy(json.loads(audit_input_path(FIXTURES).read_text(encoding="utf-8"))[operation])
    emitted = next(s for s in steps if s.get("console"))
    if mutation == "truncate": emitted["console"][0] = emitted["console"][0].rstrip("\n")
    elif mutation == "duplicate": emitted["console"] *= 2
    elif mutation == "late": steps[-1]["console"] = emitted["console"]; emitted["console"] = []
    elif mutation == "missing": emitted["console"] = []
    elif mutation == "wrong_source": emitted["line_text"] = 'printf("\\n Numero no encontrado..\\n");'
    elif mutation == "leading": emitted["console"][0] = emitted["console"][0].lstrip("\n")
    if mutation is None: assert_lista_console(steps, operation)
    else:
        with pytest.raises(AssertionError): assert_lista_console(steps, operation)

@pytest.mark.parametrize("literal,expected", [('printf("\\n\\n x\\n\\n");', "\n\n x\n\n"), ('printf("x");', "x")])
def test_literal_preservation_and_legacy_default(literal, expected):
    from app.services.execution_trace_service import ExecutionTraceService
    assert ExecutionTraceService._printf_literal(literal, preserve_trailing_newlines=True) == expected
    assert ExecutionTraceService._printf_literal(literal) == expected.rstrip("\n")
