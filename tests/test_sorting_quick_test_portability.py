"""The recovered Quick test preimage admits no case/assertion rewrites."""
from __future__ import annotations
import ast
from pathlib import Path

import pytest

from scripts.published_test_inputs import audit_input_path
from tests._sorting_published_test_contract import assert_archived_quicksort_test_portability

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = Path('openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-quicksort-instructions/before/tests/test_sorting_quicksort_baseline_low.py')
CURRENT = Path('tests/test_sorting_quicksort_baseline_low.py')


def test_archived_quick_test_retains_cases_and_assertions() -> None:
    assert_archived_quicksort_test_portability(ROOT)


@pytest.mark.parametrize('mutation', ['assertion', 'number', 'deleted_case', 'snapshot'])
def test_quick_test_portability_rejects_test_weakening(tmp_path: Path, mutation: str) -> None:
    old = audit_input_path(ROOT / SNAPSHOT).read_bytes()
    source = (ROOT / CURRENT).read_text(encoding='utf-8-sig')
    tree = ast.parse(source)
    if mutation == 'assertion':
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assert))
        node.test = ast.Constant(True)
    elif mutation == 'number':
        node = next(node for node in ast.walk(tree) if isinstance(node, ast.Constant) and type(node.value) is int)
        node.value += 1
    elif mutation == 'deleted_case':
        node = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'))
        tree.body.remove(node)
    else:
        old += b'\n'
    (tmp_path / SNAPSHOT).parent.mkdir(parents=True)
    (tmp_path / SNAPSHOT).write_bytes(old)
    (tmp_path / CURRENT).parent.mkdir(parents=True)
    (tmp_path / CURRENT).write_text(ast.unparse(tree), encoding='utf-8')
    with pytest.raises(AssertionError):
        assert_archived_quicksort_test_portability(tmp_path)
