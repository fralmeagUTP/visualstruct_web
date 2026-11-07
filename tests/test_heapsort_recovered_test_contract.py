"""Fail-closed controls for authentic Heap recovery and current-case preservation."""
from pathlib import Path
import hashlib
import json
import shutil
import pytest
from tests._heapsort_recovered_test_contract import assert_recovered_heapsort_test_successor

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def recovered(tmp_path):
    folder = tmp_path / 'tests/fixtures/sorting-history'
    shutil.copytree(ROOT / 'tests/fixtures/sorting-history', folder)
    for relative in ('tests/test_sorting_heapsort_baseline_low.py', 'tests/_sorting_published_test_contract.py'):
        shutil.copyfile(ROOT / relative, tmp_path / relative)
    receipt = json.loads((folder / 'heapsort-test-migration.json').read_text())
    record = {'path': receipt['source']['path'], 'sha256': receipt['original_declared_sha256']}
    return tmp_path, folder, receipt, record


def test_exact_original_and_current_cases_preserved(recovered):
    root, folder, receipt, record = recovered
    assert_recovered_heapsort_test_successor(root, record)
    original = (folder / receipt['original_snapshot']).read_bytes()
    published = (folder / receipt['source']['snapshot']).read_bytes()
    assert len(original) == 7562 and len(published) == 7493
    assert hashlib.sha256(original).hexdigest() == '8a59530b549cf79ed726e9be3f5d5311b47a5bbea46882e2d038f3361007b637'


@pytest.mark.parametrize('target', ['receipt', 'original', 'published', 'pin', 'path', 'adapter'])
def test_corrupted_authority_or_adapter_rejected(recovered, target):
    root, folder, receipt, record = recovered
    if target == 'pin':
        record['sha256'] = 'changed'
    elif target == 'path':
        record['path'] = 'tests/another_test.py'
    else:
        path = {'receipt': folder / 'heapsort-test-migration.json',
                'original': folder / receipt['original_snapshot'],
                'published': folder / receipt['source']['snapshot'],
                'adapter': root / 'tests/_sorting_published_test_contract.py'}[target]
        path.write_bytes(path.read_bytes() + b'\n')
    with pytest.raises(AssertionError):
        assert_recovered_heapsort_test_successor(root, record)


@pytest.mark.parametrize('old,new', [
    ("==19", "==18"),
    ("list(CASES)", "list(CASES)[:1]"),
    ("def test_real_helper_NULL_guards_or_shortcircuit_without_array_mutation(observed):", "def omitted_helper_guards(observed):"),
    ("assert all(c['array']==[42]", "assert all(c['array']==[43]"),
    ("current_swap_display(old)=={'values':p.values", "current_swap_display(old)=={'values':current_swap_display(p.values)"),
    ("assert row['native_moves']==3*row['native_swaps']==3*row['native_helper_calls']", "assert True"),
])
def test_changed_cases_conditions_parameters_and_wider_adaptation_rejected(recovered, old, new):
    root, _, receipt, record = recovered
    path = root / receipt['source']['path']
    text = path.read_text()
    assert old in text
    path.write_text(text.replace(old, new))
    with pytest.raises(AssertionError):
        assert_recovered_heapsort_test_successor(root, record)


def test_added_executable_behavior_rejected(recovered):
    root, _, receipt, record = recovered
    path = root / receipt['source']['path']
    path.write_text(path.read_text() + '\nraise RuntimeError("new behavior")\n')
    with pytest.raises(AssertionError):
        assert_recovered_heapsort_test_successor(root, record)
