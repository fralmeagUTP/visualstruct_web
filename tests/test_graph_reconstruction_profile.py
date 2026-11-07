"""Privacy, shard selection and unchanged-gate controls for separate profiling."""
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from scripts import profile_graph_reconstruction as diagnostic


def manifest(tmp_path, included=True):
    path = tmp_path / 'selection.json'
    path.write_text(json.dumps({'selected': [sha256(diagnostic.GATE_NODE.encode()).hexdigest()] if included else []}))
    return path


def test_unselected_shard_does_not_profile_or_write(tmp_path, monkeypatch):
    monkeypatch.setattr(diagnostic, 'run', lambda: pytest.fail('Wrong shard profiled'))
    output = tmp_path / 'output'
    assert diagnostic.main(['--selection', str(manifest(tmp_path, False)), '--output-dir', str(output)]) == 0
    assert not output.exists()


def test_profile_exports_only_approved_functions_and_numeric_fields():
    approved = diagnostic.approved_functions()
    code, label = next(iter(approved.items()))
    entries = [SimpleNamespace(code=code, callcount=4, reccallcount=1, inlinetime=.1, totaltime=.2,
                               secret='/home/private/user/session', calls=['PRIVATE']),
               SimpleNamespace(code='/private/credential.py', callcount=999)]
    assert diagnostic.safe_profile(entries, approved) == [{'function': label, 'calls': 4,
        'recursive_calls': 1, 'self_seconds': .1, 'cumulative_seconds': .2}]


@pytest.mark.parametrize('value', [True, -1, float('inf'), float('nan'), 'secret'])
def test_profile_rejects_invalid_numeric_metadata(value):
    code = object()
    with pytest.raises(ValueError):
        diagnostic.safe_profile([SimpleNamespace(code=code, callcount=1, reccallcount=0,
            inlinetime=value, totaltime=0)], {code: 'graph.GraphMachine.eval'})


def test_profile_failure_never_exports_exception_or_stdout(tmp_path, monkeypatch, capsys):
    def fail():
        print('PRIVATE SESSION')
        raise RuntimeError('/home/private/secret')
    monkeypatch.setattr(diagnostic, 'run', fail)
    output = tmp_path / 'output'
    assert diagnostic.main(['--selection', str(manifest(tmp_path)), '--output-dir', str(output)]) == 1
    captured = capsys.readouterr()
    assert captured.out == ''
    assert captured.err == 'Synthetic Graph profile failed; no exception details exported.\n'
    assert not output.exists()


def test_profile_uses_same_factory_rebuild_and_five_complete_replays(monkeypatch):
    from scripts import benchmark_replay
    from scripts.benchmark_checkpoint_reconstruction import HISTORY_SIZE
    history = [{'synthetic': True}] * HISTORY_SIZE
    calls = []
    def factory(count):
        assert count == 300
        return history
    def rebuild(structure_id, actual):
        assert actual is history and structure_id == 'graph'
        calls.append(1)
        return object(), list(actual)
    monkeypatch.setitem(benchmark_replay.CASES, 'graph', (rebuild, 'graph', factory))
    result = diagnostic.run()
    assert len(calls) == 6  # one warm-up, five separately profiled replays
    assert result['history_operations'] == result['replay_operations_per_iteration'] == 300
    assert result['profile_iterations'] == 5


def test_incomplete_replay_is_rejected(monkeypatch):
    from scripts import benchmark_replay
    monkeypatch.setitem(benchmark_replay.CASES, 'graph', (lambda *args: (None, []), 'graph', lambda n: [None] * n))
    with pytest.raises(RuntimeError, match='Incomplete synthetic replay'):
        diagnostic.run()


def test_gate_and_benchmark_are_byte_exact_and_profile_is_after_gate():
    root = Path(__file__).resolve().parents[1]
    expected = {
        'tests/test_checkpoint_reconstruction_performance.py': 'ad2b0dd74a5eb4fbbe91d2242cbfff8af4ad9b56891f1a45aee739f54dec6b0e',
        'scripts/benchmark_checkpoint_reconstruction.py': 'b31fe8d37fca6b5bce94036e56c7e69a4dfe9caff3505708f00aac70cf9a3a49',
        'scripts/benchmark_replay.py': 'b61c85fb05e1d05efe031df2fad570d18d222214d44f3276c024cb7608480a54',
    }
    for name, digest in expected.items():
        assert sha256((root / name).read_bytes()).hexdigest() == digest
    workflow = (root / '.github/workflows/tests-unit-integration.yml').read_text()
    unit = workflow.split('  unit-integration:', 1)[1].split('  coverage:', 1)[0]
    assert unit.index('Run unit/integration tests') < unit.index('Profile synthetic Graph replay separately')
    assert workflow.count('scripts/profile_graph_reconstruction.py') == 1
    profile_step = unit.split('      - name: Profile synthetic Graph replay separately', 1)[1].split('      - name:', 1)[0]
    assert "if: ${{ !cancelled() && hashFiles('ci-safe-diagnostics/probe-selection-result.json') != '' }}" in profile_step
    assert 'always()' not in profile_step
    upload_step = unit.split('      - name: Preserve safe unit diagnostics', 1)[1]
    assert 'if: always()' in upload_step
    assert 'python -m pytest -q tests -m "not e2e" -p scripts.pytest_e2e_partition --tb=no --no-summary' in unit


@pytest.mark.parametrize('exception,expected_code', [
    ('SystemExit', 1), ('GeneratorExit', 1), ('BaseException', 1),
    ('RuntimeError', 1), ('KeyboardInterrupt', 130),
])
def test_real_subprocess_termination_never_leaks_text(tmp_path, exception, expected_code):
    import subprocess
    import sys
    selection = manifest(tmp_path)
    output = tmp_path / 'output'
    program = '''
import sys
from scripts import profile_graph_reconstruction as diagnostic
def terminate():
    print('SYNTHETIC_PRIVATE_DIAGNOSTIC_MARKER')
    print('SYNTHETIC_PRIVATE_DIAGNOSTIC_MARKER', file=sys.stderr)
    raise EXCEPTION('SYNTHETIC_PRIVATE_DIAGNOSTIC_MARKER')
diagnostic.run = terminate
raise SystemExit(diagnostic.main(sys.argv[1:]))
'''.replace('EXCEPTION', exception)
    result = subprocess.run([sys.executable, '-B', '-c', program,
        '--selection', str(selection), '--output-dir', str(output)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=20)
    assert result.returncode == expected_code
    assert result.stdout == ''
    assert result.stderr == ('Synthetic Graph profile interrupted.\n' if expected_code == 130 else
                             'Synthetic Graph profile failed; no exception details exported.\n')
    assert not output.exists()


def test_real_subprocess_sigterm_remains_uncaught(tmp_path):
    import signal
    import subprocess
    import sys
    if sys.platform == 'win32':
        pytest.skip('POSIX runner cancellation contract')
    program = '''
import signal, sys
from scripts import profile_graph_reconstruction as diagnostic
def cancel():
    signal.raise_signal(signal.SIGTERM)
diagnostic.run = cancel
raise SystemExit(diagnostic.main(sys.argv[1:]))
'''
    output = tmp_path / 'output'
    result = subprocess.run([sys.executable, '-B', '-c', program,
        '--selection', str(manifest(tmp_path)), '--output-dir', str(output)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=20)
    assert result.returncode == -signal.SIGTERM
    assert result.stdout == result.stderr == ''
    assert not output.exists()
