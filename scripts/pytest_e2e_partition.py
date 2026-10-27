"""Deterministic distribution of existing E2E cases; preserves their complete union."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import pytest

ROOT = Path(__file__).resolve().parents[1]
_descriptors = {}

def partition(items, index, count):
    if type(index) is not int or type(count) is not int or count < 1 or not 0 <= index < count:
        raise ValueError("Invalid E2E partition")
    ordered = sorted(items, key=lambda item: item.nodeid)
    return [item for position, item in enumerate(ordered) if position % count == index]

def identity(nodeid):
    return hashlib.sha256(nodeid.encode("utf-8")).hexdigest()

def _path():
    directory = Path(os.environ["VISUALSTRUCT_E2E_DIAGNOSTICS_DIR"])
    suite = os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS_NAME", "probe")
    return directory / (suite + "-selection-result.json")

def pytest_configure(config):
    _path().parent.mkdir(parents=True, exist_ok=True)

@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    index = int(os.environ.get("VISUALSTRUCT_E2E_SHARD_INDEX", "0"))
    count = int(os.environ.get("VISUALSTRUCT_E2E_SHARD_COUNT", "1"))
    complete = list(items)
    for item in complete:
        public = Path(item.path).resolve().is_relative_to(ROOT / "tests")
        function = getattr(item,"originalname",None) or item.name.split("[",1)[0]
        _descriptors[identity(item.nodeid)] = {"file":Path(item.path).name if public else "unknown", "function":function if public else "unknown"}
    selected = partition(complete, index, count)
    selected_ids = {id(item) for item in selected}
    excluded = [item for item in complete if id(item) not in selected_ids]
    if excluded: config.hook.pytest_deselected(items=excluded)
    items[:] = selected
    _path().write_text(json.dumps({"index":index,"count":count,"eligible":sorted(identity(i.nodeid) for i in complete),"selected":sorted(identity(i.nodeid) for i in selected)},indent=2),encoding="utf-8")

_reports = []
_SAFE_EXCEPTIONS = {"AssertionError", "FileNotFoundError", "ModuleNotFoundError", "ImportError", "KeyError", "ValueError", "TypeError", "RuntimeError", "TimeoutError", "TimeoutExpired", "CalledProcessError", "MemoryError", "ZeroDivisionError"}

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    failure = {}
    if call.excinfo is not None:
        kind = call.excinfo.type.__name__
        failure["exception_kind"] = kind if kind in _SAFE_EXCEPTIONS else "other"
        locations = []
        for entry in call.excinfo.traceback:
            try:
                relative = Path(entry.path).resolve().relative_to(ROOT).as_posix()
            except (ValueError, TypeError):
                continue
            if re.fullmatch(r"(?:tests|scripts|app)/[A-Za-z0-9_/.-]+\.py", relative):
                locations.append({"file":relative,"line":int(entry.lineno)+1})
        failure["repo_locations"] = locations[-8:]
    report.publication_failure = failure

def pytest_runtest_logreport(report):
    descriptor = _descriptors.get(identity(report.nodeid), {})
    file = descriptor.get("file", "unknown")
    function = descriptor.get("function", "unknown")
    if not re.fullmatch(r"test_[A-Za-z0-9_]+\.py", file): file = "unknown"
    if not re.fullmatch(r"test_[A-Za-z0-9_]+", function): function = "unknown"
    row = {"id":identity(report.nodeid),"file":file,"function":function,"phase":report.when,"outcome":report.outcome}
    row.update(getattr(report, "publication_failure", {}))
    _reports.append(row)
    print("TEST_EVENT " + json.dumps(row), flush=True)
    path = _path().with_name(_path().name.replace("selection-result.json", "events.jsonl"))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a",encoding="utf-8") as output:
        output.write(json.dumps(row)+"\n")

def pytest_sessionfinish(session, exitstatus):
    path = _path().with_name(_path().name.replace("selection", "execution"))
    path.write_text(json.dumps({"exit":int(exitstatus),"reports":_reports},indent=2),encoding="utf-8")
