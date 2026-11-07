"""Numeric diagnostics preserve the original gate and exclude non-metric data."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from typing import Any

import pytest

from scripts.checkpoint_performance_diagnostics import (
    COUNT_FIELDS, FAMILIES, OUTPUT_NAME, TIME_FIELDS, write_checkpoint_diagnostics,
)

ENV = 'VISUALSTRUCT_E2E_DIAGNOSTICS_DIR'


def report() -> dict[str, Any]:
    return {
        'iterations': 5, 'budget_ms': 200.0, 'passed': True,
        'results': {
            family: {'history_operations': 300, 'replay_operations': 300,
                     'median_ms': 10.25, 'p95_ms': 11.75, 'budget_ms': 200.0,
                     'passed': True, 'checkpoint_enabled': True, 'checkpoint_used': False}
            for family in FAMILIES
        },
    }


def test_absent_opt_in_does_not_inspect_or_write(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        monkeypatch.delenv(ENV, raising=False)
        monkeypatch.chdir(tmp_path)
        write_checkpoint_diagnostics(object())
        assert list(tmp_path.iterdir()) == []


def test_output_is_exact_numeric_whitelist_without_private_extras(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        monkeypatch.setenv(ENV, str(tmp_path))
        source = report()
        secret = 'PRIVATE_SESSION_SOURCE_PATH'
        source.update(environment={'path': secret}, generated_at=secret, session=secret)
        source['results'][secret] = {'p95_ms': secret}
        for family in FAMILIES:
            source['results'][family].update(path=secret, source=secret, session=secret, fallback_reason=secret)
        before = deepcopy(source)
        write_checkpoint_diagnostics(source)
        assert source == before
        files = list(tmp_path.iterdir())
        assert [p.name for p in files] == [OUTPUT_NAME]
        raw = files[0].read_text(encoding='utf-8')
        assert secret not in raw
        actual = json.loads(raw)
        assert set(actual) == {'iterations', 'budget_ms', 'results'}
        assert actual['iterations'] == 5 and actual['budget_ms'] == 200.0
        assert set(actual['results']) == set(FAMILIES)
        for family in FAMILIES:
            assert actual['results'][family] == {
                key: source['results'][family][key] for key in (*COUNT_FIELDS, *TIME_FIELDS)
            }
            assert all(type(value) in (int, float) for value in actual['results'][family].values())
        assert capsys.readouterr() == ('', '')


class NumberSubclass(float):
    def __repr__(self) -> str:
        raise AssertionError('Sensitive repr must never run')


@pytest.mark.parametrize('field', ['iterations', 'budget_ms', 'history_operations', 'p95_ms'])
@pytest.mark.parametrize('invalid', ['PRIVATE', {'session': 'PRIVATE'}, [1], True, -1, float('nan'), float('inf'), pytest.param(NumberSubclass(1.0), id='float-subclass')])
def test_invalid_metric_cannot_serialize_or_create_output(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, field: str, invalid: Any, capsys: pytest.CaptureFixture[str]) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        monkeypatch.setenv(ENV, str(tmp_path/'output'))
        source = report()
        target = source if field in {'iterations', 'budget_ms'} else source['results']['graph']
        target[field] = invalid
        with pytest.raises(ValueError) as error:
            write_checkpoint_diagnostics(source)
        assert str(error.value) in {'Invalid numeric diagnostic count', 'Invalid numeric diagnostic time'}
        assert not (tmp_path/'output').exists()
        assert capsys.readouterr() == ('', '')


def test_empty_destination_never_defaults_to_current_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        monkeypatch.setenv(ENV, '')
        monkeypatch.chdir(tmp_path)
        with pytest.raises(ValueError, match='must not be empty'):
            write_checkpoint_diagnostics(report())
        assert list(tmp_path.iterdir()) == []


def test_failed_budget_is_recorded_before_original_assertion(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        import test_checkpoint_reconstruction_performance as gate
        monkeypatch.setenv(ENV, str(tmp_path))
        source = report()
        source['passed'] = False
        source['results']['graph']['p95_ms'] = 201.25
        source['results']['graph']['passed'] = False
        calls = []
        def measured(**kwargs: Any) -> dict[str, Any]:
            calls.append(kwargs)
            return source
        monkeypatch.setattr(gate, 'run', measured)
        with pytest.raises(AssertionError) as error:
            gate.test_reconstruction_p95_stays_below_200_ms_for_all_families()
        assert error.traceback[-1].frame.code.name == 'test_reconstruction_p95_stays_below_200_ms_for_all_families'
        assert calls == [{'iterations': 5, 'budget_ms': 200.0}]
        assert json.loads((tmp_path/OUTPUT_NAME).read_text())['results']['graph']['p95_ms'] == 201.25


@pytest.mark.parametrize('fault', ['history_operations', 'replay_operations', 'p95_ms', 'extra_family'])
def test_original_gate_still_rejects_invalid_history_budget_or_selection(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, fault: str) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        import test_checkpoint_reconstruction_performance as gate
        monkeypatch.setenv(ENV, str(tmp_path))
        source = report()
        if fault == 'extra_family':
            source['results']['unapproved'] = {'private': 'DO_NOT_COPY'}
        else:
            source['results']['graph'][fault] = 200.0 if fault == 'p95_ms' else 299
        monkeypatch.setattr(gate, 'run', lambda **kwargs: source)
        with pytest.raises(AssertionError):
            gate.test_reconstruction_p95_stays_below_200_ms_for_all_families()
        raw = (tmp_path/OUTPUT_NAME).read_text()
        assert 'unapproved' not in raw and 'DO_NOT_COPY' not in raw


def test_benchmark_exception_is_not_caught_or_replaced(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        import test_checkpoint_reconstruction_performance as gate
        monkeypatch.setenv(ENV, str(tmp_path))
        failure = RuntimeError('benchmark failed')
        def fail(**kwargs: Any) -> None:
            raise failure
        monkeypatch.setattr(gate, 'run', fail)
        with pytest.raises(RuntimeError) as error:
            gate.test_reconstruction_p95_stays_below_200_ms_for_all_families()
        assert error.value is failure
        assert list(tmp_path.iterdir()) == []


def test_output_error_is_not_silently_ignored(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Restore globals before pytest call-report hooks, not fixture teardown.
    with monkeypatch.context() as monkeypatch:
        monkeypatch.setenv(ENV, str(tmp_path))
        failure = OSError('write failed')
        def fail(*args: Any, **kwargs: Any) -> None:
            raise failure
        monkeypatch.setattr(Path, 'write_text', fail)
        with pytest.raises(OSError) as error:
            write_checkpoint_diagnostics(report())
        assert error.value is failure
