"""Adversarial guards for the explicit six-method transition and old snapshots."""
from pathlib import Path
import json
import shutil
import pytest
from qa_convergence._graph_contract_migration import assert_graph_contract_migration

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def custody(tmp_path):
    receipt = json.loads((ROOT / 'qa_convergence/graph_contract_migration.json').read_text())
    paths = ['.gitattributes', 'qa_convergence/graph_contract_migration.json', receipt['prior_manifest']['snapshot'],
             receipt['current_manifest']['path'], receipt['historical_harness']['path']]
    paths += [row[key] for row in receipt['files'] for key in ('active_path', 'original_snapshot')]
    for path in paths:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / path, target)
    return tmp_path, receipt


def test_real_transition_preserves_exact_originals_and_excluded_bodies(custody):
    root, _ = custody
    assert_graph_contract_migration(root)


@pytest.mark.parametrize('kind', ['snapshot', 'prior_manifest', 'harness', 'current_manifest', 'decision'])
def test_literal_or_authority_corruption_is_rejected(custody, kind):
    root, receipt = custody
    path = {'snapshot': receipt['files'][0]['original_snapshot'],
            'prior_manifest': receipt['prior_manifest']['snapshot'],
            'harness': receipt['historical_harness']['path'],
            'current_manifest': receipt['current_manifest']['path'],
            'decision': 'qa_convergence/graph_contract_migration.json'}[kind]
    with (root / path).open('ab') as output:
        output.write(b' ')
    with pytest.raises(AssertionError):
        assert_graph_contract_migration(root)


@pytest.mark.parametrize('mutation', ['historical_pin', 'remove_id', 'expanded_method', 'invented_equivalence'])
def test_decision_cannot_change_scope_or_authority(custody, mutation):
    root, receipt = custody
    if mutation == 'historical_pin':
        receipt['files'][0]['original_sha256'] = '0' * 64
    elif mutation == 'remove_id':
        receipt['six_current_test_ids'].pop()
    elif mutation == 'expanded_method':
        receipt['files'][1]['allowed_methods']['Receipt.test_only_receipt_description_changes'] = '0' * 64
    else:
        receipt['historical_equivalence_claimed'] = True
    (root / 'qa_convergence/graph_contract_migration.json').write_text(json.dumps(receipt))
    with pytest.raises(AssertionError):
        assert_graph_contract_migration(root)


@pytest.mark.parametrize('path,old,new', [
    ('qa/test_graph_numeric_receipt.py', 'numeric-null-baseline.py', 'made-up.py'),
    ('qa/test_graph_vertex_publication.py', 'graph-vertex-note-baseline.py', 'made-up.py'),
    ('qa/test_graph_query_publication.py', 'graph-query-note-baseline.py', 'made-up.py'),
    ('qa/test_graph_numeric_receipt.py', 'import importlib,unittest', 'import importlib,unittest\nassert False'),
    ('qa/test_graph_vertex_publication.py', "('insert_vertex',3,H)", "('insert_vertex',4,H)"),
    ('qa/test_graph_query_publication.py', 'CurrentContract.test_typed_results(self)', 'pass'),
])
def test_excluded_bodies_dependencies_cases_and_active_oracles_are_bound(custody, path, old, new):
    root, _ = custody
    target = root / path
    text = target.read_text(); assert old in text
    target.write_text(text.replace(old, new))
    with pytest.raises(AssertionError):
        assert_graph_contract_migration(root)


def test_active_text_crlf_transport_does_not_rewrite_literal_snapshots(custody):
    root, receipt = custody
    paths = [row['active_path'] for row in receipt['files']]
    paths += ['qa_convergence/graph_contract_migration.json', receipt['current_manifest']['path']]
    for path in paths:
        file = root / path
        file.write_bytes(file.read_bytes().replace(b'\n', b'\r\n'))
    assert_graph_contract_migration(root)


def test_snapshot_line_ending_changes_remain_rejected(custody):
    root, receipt = custody
    file = root / receipt['files'][0]['original_snapshot']
    file.write_bytes(file.read_bytes().replace(b'\n', b'\r\n'))
    with pytest.raises(AssertionError):
        assert_graph_contract_migration(root)


def test_snapshot_transport_protection_cannot_be_removed(custody):
    root, _ = custody
    path = root / '.gitattributes'
    path.write_text(path.read_text().replace('tests/fixtures/graph-history/contract-migration/*.snapshot -text', ''))
    with pytest.raises(AssertionError):
        assert_graph_contract_migration(root)
