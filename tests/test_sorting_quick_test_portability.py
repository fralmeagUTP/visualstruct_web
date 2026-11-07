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


@pytest.mark.parametrize('mutation', ['assertion', 'number', 'deleted_case', 'snapshot', 'normalize_current', 'normalize_both', 'reverse_operands', 'move_wrapper'])
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
    elif mutation == 'snapshot':
        old += b'\n'
    else:
        target = next(node for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'current_swap_display')
        comparison = next(node for node in ast.walk(tree) if isinstance(node, ast.Compare) and node.left is target)
        if mutation in {'normalize_current', 'normalize_both'}:
            if mutation == 'normalize_current':
                comparison.left = target.args[0]
            comparison.comparators[0] = ast.Call(func=ast.Name(id='current_swap_display', ctx=ast.Load()), args=[comparison.comparators[0]], keywords=[])
        elif mutation == 'reverse_operands':
            comparison.left, comparison.comparators[0] = comparison.comparators[0], comparison.left
        else:
            comparison.left = target.args[0]
            # Relocating the wrapper to another occurrence would be erased by
            # the old generic visitor even though the approved assertion lost it.
            later = next(node for node in ast.walk(tree) if isinstance(node, ast.Compare) and isinstance(node.left, ast.Attribute) and node.left.attr == 'values')
            later.left = ast.Call(func=ast.Name(id='current_swap_display', ctx=ast.Load()), args=[later.left], keywords=[])
    (tmp_path / SNAPSHOT).parent.mkdir(parents=True)
    (tmp_path / SNAPSHOT).write_bytes(old)
    (tmp_path / CURRENT).parent.mkdir(parents=True)
    (tmp_path / CURRENT).write_text(ast.unparse(tree), encoding='utf-8')
    with pytest.raises(AssertionError):
        assert_archived_quicksort_test_portability(tmp_path)
