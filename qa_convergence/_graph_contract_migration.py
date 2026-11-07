"""Byte-bound custody and finite active-body transition, not historical execution."""
from __future__ import annotations
import ast
import hashlib
import json
from pathlib import Path

_RECEIPT_SHA256 = 'c870b8a137634de3ce6286c83c0a7572311d63dc4a90f0664d5d550db9fe63d7'


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _text(raw: bytes) -> str:
    """Only host line-ending transport is normalized for active source bindings."""
    return raw.replace(b'\r\n', b'\n').decode('utf-8')


def _methods(text: str) -> dict[str, ast.FunctionDef]:
    return {cls.name + '.' + node.name: node
            for cls in ast.parse(text).body if isinstance(cls, ast.ClassDef)
            for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


def assert_graph_contract_migration(root: Path) -> None:
    raw = (root / 'qa_convergence/graph_contract_migration.json').read_bytes()
    assert _digest(_text(raw).encode()) == _RECEIPT_SHA256, 'Reviewed Graph migration decision changed'
    receipt = json.loads(raw)
    assert 'tests/fixtures/graph-history/contract-migration/*.snapshot -text' in (root / '.gitattributes').read_text().splitlines(), 'Literal Graph snapshots lost transport protection'
    assert receipt['historical_equivalence_claimed'] is False
    assert receipt['historical_execution_recovered'] is False
    assert receipt['test_selection_changed'] is False
    ids = []
    for row in receipt['files']:
        original_raw = (root / row['original_snapshot']).read_bytes()
        assert _digest(original_raw) == row['original_sha256'], 'Literal Graph original changed'
        original = _text(original_raw)
        current = _text((root / row['active_path']).read_bytes())
        old_nodes, new_nodes = _methods(original), _methods(current)
        old_lines, new_lines = original.splitlines(keepends=True), current.splitlines(keepends=True)
        replacements = []
        for name, expected in row['allowed_methods'].items():
            assert name in old_nodes and name in new_nodes, 'Declared Graph method missing'
            old, new = old_nodes[name], new_nodes[name]
            segment = ''.join(new_lines[new.lineno - 1:new.end_lineno])
            assert _digest(segment.encode()) == expected, 'Reviewed current acceptance changed'
            replacements.append((new.lineno - 1, new.end_lineno, old_lines[old.lineno - 1:old.end_lineno]))
            if not name.endswith('.setUpClass'):
                ids.append(row['active_path'] + '::' + name.replace('.', '::'))
        for start, end, segment in sorted(replacements, reverse=True):
            new_lines[start:end] = segment
        # This binds every import, fixture, case list, excluded method, decorator,
        # main invocation and all other text, not just the named baseline bodies.
        assert ''.join(new_lines) == original, 'Graph source changed outside the six methods and allocation setup'
        restored = ast.dump(ast.parse(''.join(new_lines)), include_attributes=False)
        assert restored == ast.dump(ast.parse(original), include_attributes=False)
        for name in receipt['excluded_baseline_methods'].get(row['active_path'], []):
            assert name not in row['allowed_methods']
            assert ast.dump(old_nodes[name], include_attributes=False) == ast.dump(new_nodes[name], include_attributes=False), 'Excluded historical baseline body changed'
    assert sorted(ids) == sorted(receipt['six_current_test_ids']) and len(set(ids)) == 6, 'Current acceptance ID set changed'
    prior = receipt['prior_manifest']
    assert _digest((root / prior['snapshot']).read_bytes()) == prior['sha256'], 'Original Graph manifest changed'
    manifest_row = receipt['current_manifest']
    manifest_raw = (root / manifest_row['path']).read_bytes()
    assert _digest(_text(manifest_raw).encode()) == manifest_row['normalized_sha256'], 'Current Graph custody manifest changed'
    manifest = json.loads(manifest_raw)
    assert manifest['historical_files_preserved'] is True and manifest['test_selection_changed'] is False
    assert manifest['historical_execution_recovered'] is False
    assert {x['historical_file'] for x in manifest['pairs']} == {x['active_path'] for x in receipt['files']}
    for row in manifest['pairs']:
        assert row['equivalence_claimed'] is False
        assert _digest((root / row['historical_snapshot']).read_bytes()) == row['historical_sha256']
    harness = receipt['historical_harness']
    assert _digest((root / harness['path']).read_bytes()) == harness['sha256'], 'Historical C harness changed'
