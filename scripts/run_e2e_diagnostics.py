"""Run pytest with safe live metadata only; propagate its exact exit code."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from scripts.e2e_diagnostics import safe_record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite", choices=("chromium", "firefox", "probe"), required=True)
    parser.add_argument("target")
    parser.add_argument("--case", action="append", default=[], help="Select an existing test function in target; parameterized cases remain intact")
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    args = parser.parse_args()
    target = Path(args.target).resolve()
    if not ((target.is_file() and target.suffix == ".py") or target.is_dir()):
        parser.error("target must be an existing test file or directory")
    if args.shard_count < 1 or not 0 <= args.shard_index < args.shard_count:
        parser.error("invalid E2E partition")
    if args.case and not target.is_file():
        parser.error("--case requires one test file")
    import ast
    import re
    names = {node.name for node in ast.parse(target.read_text(encoding="utf-8-sig")).body
             if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_")} if target.is_file() else set()
    if len(args.case) != len(set(args.case)) or any(not re.fullmatch(r"test_[A-Za-z0-9_]+", name) or name not in names for name in args.case):
        parser.error("--case must name unique existing test functions in target")
    selections = [str(target) + "::" + name for name in args.case] if args.case else [str(target)]
    directory = Path(os.environ.get("VISUALSTRUCT_E2E_DIAGNOSTICS_DIR", "e2e-safe-diagnostics")).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    channel = directory / (args.suite + ".jsonl")
    offset = channel.stat().st_size if channel.exists() else 0
    env = dict(os.environ, PYTHONPATH=str(_ROOT) + os.pathsep + os.environ.get("PYTHONPATH", ""), VISUALSTRUCT_E2E_DIAGNOSTICS="1", VISUALSTRUCT_E2E_DIAGNOSTICS_DIR=str(directory), VISUALSTRUCT_E2E_DIAGNOSTICS_NAME=args.suite, PYTHONUNBUFFERED="1", VISUALSTRUCT_E2E_SHARD_INDEX=str(args.shard_index), VISUALSTRUCT_E2E_SHARD_COUNT=str(args.shard_count))
    # No tee, raw pytest output, longrepr or JUnit artifact: they may contain arbitrary secrets.
    partition_plugins = ["-p", "scripts.pytest_e2e_partition"] if args.shard_count > 1 else []
    child = subprocess.Popen([sys.executable, "-B", "-m", "pytest", "-q", "--tb=no", "--no-summary", "-p", "scripts.e2e_diagnostics", *partition_plugins, *selections],
                             cwd=target.parent, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pending = b""
    while True:
        if channel.exists():
            with channel.open("rb") as stream:
                stream.seek(offset); chunk = stream.read(); offset = stream.tell()
            pending += chunk
            while b"\n" in pending:
                line, pending = pending.split(b"\n", 1)
                try:
                    row = json.loads(line)
                    if type(row) is dict:
                        print("E2E_CHECKPOINT " + json.dumps(safe_record(row.get("stage"), row)), flush=True)
                except (ValueError, TypeError):
                    print("E2E_DIAGNOSTIC_INVALID_RECORD", flush=True)
        if child.poll() is not None:
            if channel.exists() and channel.stat().st_size > offset: continue
            break
        time.sleep(.25)
    code = child.wait()
    result = {"suite": args.suite, "pytest_exit_code": code}
    (directory / (args.suite + "-result.json")).write_text(json.dumps(result), encoding="utf-8")
    print("E2E_RESULT " + json.dumps(result), flush=True)
    return code


if __name__ == "__main__": raise SystemExit(main())
