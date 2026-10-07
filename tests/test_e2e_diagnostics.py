"""Safe metadata retains real failure/exit code without publishing exception text."""
import json
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace


def test_runner_records_timeout_and_exit1_without_token_password_or_raw_artifacts(tmp_path):
    root = Path(__file__).resolve().parents[1]
    sentinel = "SYNTHETIC_" + "SECRET_SENTINEL"
    password = "SYNTHETIC_" + "PASSWORD_SENTINEL"
    probe = tmp_path / "test_probe.py"
    probe.write_text("import pytest\nfrom scripts.e2e_diagnostics import checkpoint\n@pytest.mark.parametrize('value', [" + repr(sentinel) + "])\ndef test_timeout(value):\n    checkpoint('manual_finish_start')\n    print('Authorization: Bearer ' + value)\n    raise TimeoutError('password=' + " + repr(password) + ")\ndef test_pass():\n    assert True\n", encoding="utf-8")
    directory = tmp_path / "diagnostics"
    env = dict(os.environ, PYTHONPATH=str(root), VISUALSTRUCT_E2E_DIAGNOSTICS_DIR=str(directory),
               PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    result = subprocess.run([sys.executable, "-B", str(root / "scripts/run_e2e_diagnostics.py"),
                             "--suite", "probe", str(probe)],
                            cwd=tmp_path, env=env, capture_output=True, text=True, timeout=15)
    assert result.returncode == 1
    rows = [json.loads(line) for line in (directory / "probe.jsonl").read_text().splitlines()]
    assert rows[0]["stage"] == "session_start" and rows[0]["stack_dump_seconds"] == 90
    wait = next(row for row in rows if row["stage"] == "manual_finish_start")
    assert wait["test"] == "unknown_test"  # Arbitrary external nodeids/parameters never get published.
    failed = [row for row in rows if row["stage"] == "test_report" and row.get("outcome") == "failed"]
    assert len(failed) == 1 and failed[0]["phase"] == "call" and failed[0]["error_category"] == "timeout"
    assert sum(row["stage"] == "test_start" for row in rows) == 2
    assert sum(row["stage"] == "test_end" for row in rows) == 2
    assert rows[-1]["stage"] == "session_end"
    assert json.loads((directory / "probe-result.json").read_text())["pytest_exit_code"] == 1
    assert {p.name for p in directory.iterdir()} == {"probe.jsonl", "probe-result.json"}
    public = result.stdout + result.stderr + "".join(p.read_text() for p in directory.iterdir())
    leaked = sentinel in public or password in public
    assert not leaked
    assert "E2E_CHECKPOINT" in result.stdout and '"pytest_exit_code": 1' in result.stdout


def test_checkpoint_never_reads_longrepr_and_drops_arbitrary_details(capsys, monkeypatch, tmp_path):
    from scripts import e2e_diagnostics as diagnostics
    class UnreadableError:
        def __str__(self): raise RuntimeError("longrepr must not be read")
    sentinel = "SYNTHETIC_" + "SECRET_SENTINEL"
    monkeypatch.setenv("VISUALSTRUCT_E2E_DIAGNOSTICS", "1")
    monkeypatch.setenv("VISUALSTRUCT_E2E_DIAGNOSTICS_DIR", str(tmp_path))
    diagnostics.pytest_runtest_logreport(SimpleNamespace(when="call", outcome="failed", failed=True,
                                                        longrepr=UnreadableError()))
    diagnostics.checkpoint("manual_navigation", token=sentinel, password=sentinel, counter=sentinel,
                           path="/" + sentinel, stack=[{"file": sentinel, "line": 1}], error=sentinel)
    output = capsys.readouterr().out
    persisted = (tmp_path / "probe.jsonl").read_text()
    leaked = sentinel in output or sentinel in persisted
    assert not leaked
    rows = [json.loads(line) for line in persisted.splitlines()]
    assert rows[0]["outcome"] == "failed" and rows[0]["phase"] == "call"
    assert rows[0]["error_category"] == "failure"
    assert rows[1]["path"] == "other" and rows[1]["stack"] == []
    assert "token" not in rows[1] and "password" not in rows[1] and "error" not in rows[0]


def test_approved_test_identity_survives_without_parameter_data(capsys, monkeypatch, tmp_path):
    from scripts import e2e_diagnostics as diagnostics
    monkeypatch.setenv("VISUALSTRUCT_E2E_DIAGNOSTICS", "1")
    monkeypatch.setenv("VISUALSTRUCT_E2E_DIAGNOSTICS_DIR", str(tmp_path))
    nodeid = sorted(diagnostics._TEST_IDS)[0]
    sentinel = "SYNTHETIC_" + "SECRET_SENTINEL"
    diagnostics.pytest_runtest_logstart(nodeid + "[" + sentinel + "]", None)
    diagnostics.checkpoint("server_shutdown_start")
    diagnostics.pytest_runtest_logfinish(nodeid, None)
    rows = [json.loads(line) for line in (tmp_path / "probe.jsonl").read_text().splitlines()]
    assert all(row["test"] == nodeid for row in rows)
    assert rows[1]["stage"] == "server_shutdown_start"
    output = capsys.readouterr().out
    assert sentinel not in output
