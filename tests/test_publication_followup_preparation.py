"""Bounded checks of publication preparation; no algorithm/browser campaigns."""
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from scripts import test_tool_paths as tools
from scripts import pytest_e2e_partition as diagnostics
from scripts.published_test_inputs import audit_input_path
from scripts.verify_test_partition_results import verify

ROOT=Path(__file__).resolve().parents[1]

def test_original_abb_root_one_input_is_present_and_hash_bound():
    relative="openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-abb-delete-baseline-low/abb-delete-root-one-native-low/review.json"
    manifest=json.loads((ROOT/"tests/fixtures/published-audit-inputs/manifest.json").read_text(encoding="utf-8"))
    row=next(row for row in manifest["files"] if row["path"]==relative)
    raw=audit_input_path(ROOT/relative).read_bytes()
    assert hashlib.sha256(raw).hexdigest()==row["sha256"]
    assert json.loads(raw)["cases"]

def test_doxygen_uses_path_and_missing_tool_remains_error(monkeypatch,tmp_path):
    monkeypatch.setattr(tools.shutil,"which",lambda name:"/tools/doxygen")
    assert tools.resolve_doxygen()=="/tools/doxygen"
    monkeypatch.setattr(tools.shutil,"which",lambda name:None)
    monkeypatch.setattr(tools,"_LEGACY_WINDOWS_DOXYGEN",tmp_path/"missing.exe")
    with pytest.raises(RuntimeError): tools.resolve_doxygen()

def test_safe_failure_and_live_record_never_use_private_details(monkeypatch,tmp_path,capsys):
    sentinel="SYNTHETIC_SECRET_NOT_FOR_ARTIFACTS"
    class Unreadable:
        def __str__(self):raise AssertionError("private exception text must not be read")
    report=SimpleNamespace()
    info=SimpleNamespace(type=FileNotFoundError,value=Unreadable(),traceback=[SimpleNamespace(path=ROOT/"tests/test_publication_followup_preparation.py",lineno=10),SimpleNamespace(path=tmp_path/sentinel,lineno=11)])
    hook=diagnostics.pytest_runtest_makereport(None,SimpleNamespace(excinfo=info));next(hook)
    with pytest.raises(StopIteration):hook.send(SimpleNamespace(get_result=lambda:report))
    assert report.publication_failure=={"exception_kind":"FileNotFoundError","repo_locations":[{"file":"tests/test_publication_followup_preparation.py","line":11}]}
    monkeypatch.setenv("VISUALSTRUCT_E2E_DIAGNOSTICS_DIR",str(tmp_path));monkeypatch.setenv("VISUALSTRUCT_E2E_DIAGNOSTICS_NAME","probe")
    monkeypatch.setattr(diagnostics,"_reports",[])
    diagnostics.pytest_runtest_logreport(SimpleNamespace(nodeid="test_private["+sentinel+"]",when="setup",outcome="failed",publication_failure=report.publication_failure))
    public=capsys.readouterr().out+(tmp_path/"probe-events.jsonl").read_text()
    assert sentinel not in public
    assert "FileNotFoundError" in public and '"line": 11' in public

def write_partition(root,index,selected,eligible,*,exit=0,executed=True):
    folder=root/f"coverage-shard-{index}";folder.mkdir(exist_ok=True)
    (folder/"probe-selection-result.json").write_text(json.dumps({"index":index,"count":2,"selected":selected,"eligible":eligible}))
    (folder/"probe-execution-result.json").write_text(json.dumps({"exit":exit,"reports":[{"id":value,"phase":"call","outcome":"passed"} for value in selected] if executed else []}))

def test_coverage_union_requires_every_case_and_real_execution(tmp_path):
    write_partition(tmp_path,0,["a"],["a","b"]);write_partition(tmp_path,1,["b"],["a","b"])
    assert verify(tmp_path,2)==2
    write_partition(tmp_path,1,["b"],["a","b"],executed=False)
    with pytest.raises(ValueError):verify(tmp_path,2)
    write_partition(tmp_path,1,["a"],["a","b"])
    with pytest.raises(ValueError):verify(tmp_path,2)
    write_partition(tmp_path,1,["b"],["a","b"],exit=1)
    with pytest.raises(ValueError):verify(tmp_path,2)
