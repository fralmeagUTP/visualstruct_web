"""Diagnostic controls must not alter the real CI plugin's reporting context."""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.verify_test_partition_results import verify

ROOT = Path(__file__).resolve().parents[1]
CONTROLS = [
    'tests/test_checkpoint_performance_diagnostics.py',
    'tests/test_rbt_capture_safety_contract.py',
    'tests/test_e2e_diagnostics.py::test_checkpoint_never_reads_longrepr_and_drops_arbitrary_details',
    'tests/test_e2e_diagnostics.py::test_approved_test_identity_survives_without_parameter_data',
    'tests/test_publication_followup_preparation.py::test_safe_failure_and_live_record_never_use_private_details',
    'tests/test_publication_followup_preparation.py::test_collection_failure_is_reported_without_reading_private_error',
]
CONTROL_COUNT = 68


@pytest.mark.parametrize('relative_directory', [False, True])
@pytest.mark.parametrize('partitions', [1, 4])
def test_real_partition_plugin_retains_every_control_report(
    tmp_path: Path, relative_directory: bool, partitions: int,
) -> None:
    """Exercise the actual CI command/plugin, not a mocked logreport hook."""
    official_root = tmp_path/'official-artifacts'
    expected_population = None
    all_selected: set[str] = set()
    for index in range(partitions):
        official = official_root/f'coverage-shard-{index}'
        destination = os.path.relpath(official, ROOT) if relative_directory else str(official)
        environment = dict(
            os.environ,
            VISUALSTRUCT_E2E_DIAGNOSTICS_DIR=destination,
            VISUALSTRUCT_E2E_DIAGNOSTICS_NAME='probe',
            VISUALSTRUCT_E2E_SHARD_INDEX=str(index),
            VISUALSTRUCT_E2E_SHARD_COUNT=str(partitions),
        )
        result = subprocess.run(
            [sys.executable, '-m', 'pytest', '-q', *CONTROLS, '-m', 'not e2e',
             '-p', 'scripts.pytest_e2e_partition', '--tb=no', '--no-summary',
             '--basetemp', str(tmp_path/f'child-{index}')],
            cwd=ROOT, env=environment, capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert 'INTERNALERROR' not in result.stdout + result.stderr
        selection = json.loads((official/'probe-selection-result.json').read_text())
        execution = json.loads((official/'probe-execution-result.json').read_text())
        events = [json.loads(line) for line in (official/'probe-events.jsonl').read_text().splitlines()]
        population = set(selection['eligible'])
        assert len(selection['eligible']) == len(population) == CONTROL_COUNT
        if expected_population is None:
            expected_population = population
        assert population == expected_population
        selected = set(selection['selected'])
        assert len(selected) == len(selection['selected'])
        assert not (all_selected & selected)
        all_selected.update(selected)
        assert execution['exit'] == 0 and execution['reports'] == events
        assert len(events) == 3*len(selected)
        assert Counter((row['id'], row['phase']) for row in events) == Counter(
            (identity, phase) for identity in selected for phase in ('setup', 'call', 'teardown')
        )
        assert all(row['outcome'] == 'passed' for row in events)
        # Test fixtures may deliberately create synthetic reports. No real
        # selected control's event may be diverted to those temporary stores.
        for path in (tmp_path/f'child-{index}').rglob('*-events.jsonl'):
            diverted = [json.loads(line) for line in path.read_text().splitlines()]
            assert not any(row.get('id') in population for row in diverted)
        for suffix in ('selection-result.json', 'execution-result.json'):
            assert not list((tmp_path/f'child-{index}').rglob('*-'+suffix))
    assert all_selected == expected_population
    # This is the real post-shard verifier used before combining CI coverage.
    assert verify(official_root, partitions) == CONTROL_COUNT


@pytest.mark.parametrize('relative_directory', [False, True])
def test_scope_restores_all_globals_before_a_failed_call_is_reported(
    tmp_path: Path, relative_directory: bool,
) -> None:
    """An assertion failure must still unwind mutations before real hooks run."""
    probe = tmp_path/'test_expected_failure.py'
    probe.write_text(
        "from pathlib import Path\n"
        "def test_expected_failure(monkeypatch, tmp_path):\n"
        "    with monkeypatch.context() as monkeypatch:\n"
        "        monkeypatch.delenv('VISUALSTRUCT_E2E_DIAGNOSTICS_DIR')\n"
        "        monkeypatch.setenv('VISUALSTRUCT_E2E_DIAGNOSTICS_NAME', 'diverted')\n"
        "        monkeypatch.chdir(tmp_path)\n"
        "        def blocked(*args, **kwargs):\n"
        "            raise RuntimeError('temporary filesystem mock')\n"
        "        monkeypatch.setattr(Path, 'mkdir', blocked)\n"
        "        monkeypatch.setattr(Path, 'write_text', blocked)\n"
        "        assert False, 'intentional probe assertion'\n",
        encoding='utf-8',
    )
    official = tmp_path/'official-artifacts'
    destination = os.path.relpath(official, ROOT) if relative_directory else str(official)
    environment = dict(
        os.environ, VISUALSTRUCT_E2E_DIAGNOSTICS_DIR=destination,
        VISUALSTRUCT_E2E_DIAGNOSTICS_NAME='probe',
        VISUALSTRUCT_E2E_SHARD_INDEX='0', VISUALSTRUCT_E2E_SHARD_COUNT='1',
    )
    result = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', str(probe),
         '-p', 'scripts.pytest_e2e_partition', '--tb=no', '--no-summary',
         '--basetemp', str(tmp_path/'child')],
        cwd=ROOT, env=environment, capture_output=True, text=True, timeout=60,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert 'INTERNALERROR' not in result.stdout + result.stderr
    selection = json.loads((official/'probe-selection-result.json').read_text())
    execution = json.loads((official/'probe-execution-result.json').read_text())
    events = [json.loads(line) for line in (official/'probe-events.jsonl').read_text().splitlines()]
    assert execution['exit'] == 1 and execution['reports'] == events
    assert len(selection['selected']) == len(selection['eligible']) == 1
    assert [row['phase'] for row in events] == ['setup', 'call', 'teardown']
    assert [row['outcome'] for row in events] == ['passed', 'failed', 'passed']
    assert {row['id'] for row in events} == set(selection['selected'])
    assert events[1]['exception_kind'] == 'AssertionError'
    assert {p.name for p in official.iterdir()} == {
        'probe-selection-result.json', 'probe-execution-result.json', 'probe-events.jsonl',
    }
    assert not list((tmp_path/'child').rglob('*-events.jsonl'))
