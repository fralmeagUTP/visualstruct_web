"""Opt-in metadata-only E2E diagnostics; never serialize error/input text."""
from __future__ import annotations
import ast
import json
import os
import re
import sys
import threading
import time
from pathlib import Path
import pytest

_ROOT = Path(__file__).resolve().parents[1]
_TEST_FILES = ("tests/test_ui_playwright_e2e.py", "tests/test_playwright_firefox_smoke.py")
_TEST_IDS = set()
for _relative in _TEST_FILES:
    for _node in ast.parse((_ROOT / _relative).read_text(encoding="utf-8-sig")).body:
        if isinstance(_node, ast.FunctionDef) and _node.name.startswith("test_"):
            _TEST_IDS.add(_relative + "::" + _node.name)
_SOURCE_FILES = {str((_ROOT / p).resolve()): p for p in _TEST_FILES}
_SOURCE_FILES.update({str(p.resolve()): p.relative_to(_ROOT).as_posix() for p in (_ROOT / "app").rglob("*.py")})
_SOURCE_FILES[str(Path(__file__).resolve())] = "scripts/e2e_diagnostics.py"
_SOURCE_NAMES = set(_SOURCE_FILES.values())
_STAGES = frozenset({"session_start", "session_end", "test_start", "test_report", "test_end", "collection_report", "thread_stacks", "server_create_start", "server_ready", "server_shutdown_start", "server_shutdown_end", "server_thread_join_end", "http_start", "http_end", "manual_prepare_start", "manual_finish_start", "manual_navigation", "manual_finish_end"})
_active_test = None
_stop = threading.Event()
_worker = None


def _test_id(value):
    if type(value) is not str: return "unknown_test"
    value = value.replace("\\", "/").split("[", 1)[0]
    return value if value in _TEST_IDS else "unknown_test"


def safe_record(stage, details):
    row = {"time_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "test": _test_id(details.get("test", _active_test)),
           "stage": stage if type(stage) is str and stage in _STAGES else "other"}
    for key, allowed in {"phase": {"setup", "call", "teardown", "collection"}, "outcome": {"passed", "failed", "skipped"},
                         "error_category": {"none", "timeout", "assertion", "exception", "failure", "collection"},
                         "module": {"seq", "hier", "graph", "hash", "sorting"},
                         "method": {"GET", "POST", "HEAD", "OPTIONS", "PUT", "DELETE", "PATCH"}}.items():
        value = details.get(key)
        if type(value) is str and value in allowed: row[key] = value
    for key in ("status", "port", "navigation_index", "stack_dump_seconds"):
        value = details.get(key)
        if type(value) is int and 0 <= value <= 65535: row[key] = value
    if type(details.get("alive")) is bool: row["alive"] = details["alive"]
    path = details.get("path")
    if type(path) is str:
        match = re.fullmatch(r"/(sequential|hierarchical|graph|hash|sorting)/(stack|queue|priority_queue|linked_list|circular_list|sublist|abb|avl|red_black|binary_heap|graph|hash_table|visualizador)(?:/(operate|code|help|state|reset|recorridos))?", path)
        row["path"] = path if match else "other"
    counter = details.get("counter")
    if type(counter) is str:
        match = re.fullmatch(r"Paso:\s*([0-9]{1,8})\s*/\s*([0-9]{1,8})", counter.strip())
        if match: row["current"], row["total"] = map(int, match.groups())
    for key in ("current", "total"):
        value = details.get(key)
        if type(value) is int and 0 <= value <= 99999999: row[key] = value
    stack = details.get("stack")
    if type(stack) is list:
        row["stack"] = [{"file": f["file"], "line": f["line"]} for f in stack[:100]
                        if type(f) is dict and type(f.get("file")) is str and f["file"] in _SOURCE_NAMES
                        and type(f.get("line")) is int and 0 < f["line"] < 1000000]
    return row


def channel_path():
    directory = Path(os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS_DIR", ".pytest-e2e-safe-diagnostics"))
    name = os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS_NAME", "probe")
    if name not in {"chromium", "firefox", "probe"}: name = "probe"
    return directory / (name + ".jsonl")


def checkpoint(stage, **details):
    if os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS") != "1": return
    line = json.dumps(safe_record(stage, details), ensure_ascii=True)
    print("E2E_CHECKPOINT " + line, flush=True)
    try:
        path = channel_path(); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as stream: stream.write(line + "\n")
    except OSError:
        print("E2E_DIAGNOSTIC_WRITE_ERROR", flush=True)


def _thread_locations():
    while not _stop.wait(90):
        stack = []
        for frame in sys._current_frames().values():
            while frame is not None:
                source = _SOURCE_FILES.get(str(Path(frame.f_code.co_filename).resolve()))
                if source: stack.append({"file": source, "line": frame.f_lineno})
                frame = frame.f_back
        checkpoint("thread_stacks", stack=stack)


def pytest_configure(config):
    global _worker
    if os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS") == "1":
        checkpoint("session_start", stack_dump_seconds=90)
        _stop.clear(); _worker = threading.Thread(target=_thread_locations, daemon=True)
        _worker.start()


def pytest_unconfigure(config):
    if os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS") == "1":
        _stop.set()
        checkpoint("session_end")


def pytest_runtest_logstart(nodeid, location):
    global _active_test
    _active_test = _test_id(nodeid)
    checkpoint("test_start")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    category = "none"
    if call.excinfo is not None:
        exception_type = call.excinfo.type
        category = "timeout" if exception_type.__name__ == "TimeoutError" else "assertion" if issubclass(exception_type, AssertionError) else "exception"
    report.e2e_error_category = category


def pytest_runtest_logreport(report):
    checkpoint("test_report", phase=report.when, outcome=report.outcome,
               error_category=getattr(report, "e2e_error_category", "failure" if report.failed else "none"))


def pytest_runtest_logfinish(nodeid, location):
    global _active_test
    checkpoint("test_end")
    _active_test = None


def pytest_collectreport(report):
    if report.failed:
        checkpoint("collection_report", phase="collection", outcome="failed", error_category="collection")
