"""Read-only continuity checkpoint; never imports or runs the application."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "openspec/continuity/index.json"

class GuardError(ValueError):
    """An explicit continuity precondition failed."""

def read_source(root: Path, relative: str) -> tuple[str, dict[str, Any]]:
    """Read a contained source and detect concurrent modification."""
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise GuardError("Missing or escaping source: " + relative)
    before = path.stat()
    raw = path.read_bytes()
    after = path.stat()
    if (before.st_mtime_ns, before.st_size) != (after.st_mtime_ns, after.st_size):
        raise GuardError("Source changed during reading; retry: " + relative)
    return raw.decode("utf-8-sig"), {
        "path": relative, "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw), "mtime_ns": after.st_mtime_ns,
    }

def checkpoint(root: Path, config: dict[str, Any], change: str,
               operation: str, cwd: Path, reason: str = "",
               decision_ref: str = "", previous: dict[str, Any] | None = None,
               phase: str = "before", assignment_id: str = "") -> dict[str, Any]:
    """Derive source state; fail closed on invalid identity or reopening."""
    root = root.resolve()
    if root != Path(config["canonical_project"]).resolve() or cwd.resolve() != root:
        raise GuardError("Wrong project/cwd; expected " + config["canonical_project"])
    if change not in config["changes"]:
        raise GuardError("Unregistered change; review source bindings")
    if not (root / "openspec" / "changes" / change).is_dir():
        raise GuardError("Change is not active; review archive/consolidation before continuing")
    entry = config["changes"][change]
    if operation not in entry["operations"]:
        raise GuardError("Unregistered operation; do not infer it from prose")
    manifests, texts = {}, {}
    def source(relative: str) -> str:
        if relative not in texts:
            texts[relative], manifests[relative] = read_source(root, relative)
        return texts[relative]
    for relative in ["openspec/AGENTS.md", "openspec/project.md"] + entry["sources"]:
        source(relative)
    tasks = source(entry["tasks"])
    assignment = None
    if entry.get("assignment_source"):
        assignment = json.loads(source(entry["assignment_source"]))
        if not assignment_id or assignment_id != assignment["assignment_id"]:
            raise GuardError("Current assignment ID required: " + assignment["assignment_id"] +
                             "; read latest instruction, not a historical checkpoint")
        if assignment["change"] != change or assignment["operation"] != operation:
            raise GuardError("Assignment operation " + assignment["operation"] +
                             " conflicts with requested " + operation +
                             "; follow current instruction, do not reopen historical work")
        source(assignment["scope_ref"])
    elif assignment_id:
        raise GuardError("No assignment source registered for this change")
    states = {}
    for identifier, binding in entry["operations"].items():
        text = source(binding["source"])
        for ref in binding.get("evidence", []) + binding.get("context_sources", []):
            source(ref)
        task_status = None
        if binding.get("task_prefix"):
            matches = re.findall(r"^- \[([ xX])\] " + re.escape(binding["task_prefix"]) + r".*$", tasks, re.MULTILINE)
            if len(matches) != 1:
                raise GuardError("Task binding missing or ambiguous: " + identifier)
            task_status = "completed" if matches[0].lower() == "x" else "pending"
        marker = binding.get("closed_marker")
        states[identifier] = {
            "status": "recorded-closed" if marker and marker in text else "not-signed-off",
            "source": binding["source"], "closed_marker": marker,
            "scope": binding["scope"], "evidence": binding.get("evidence", []),
            "context_sources": binding.get("context_sources", []),
            "task_prefix": binding.get("task_prefix"), "task_status": task_status,
        }
    if states[operation]["status"] == "recorded-closed" and phase == "before":
        if not reason.strip() or not decision_ref:
            raise GuardError("Recorded closed operation; require --reopen-reason and --decision-ref")
        if not decision_ref.startswith("openspec/changes/" + change + "/"):
            raise GuardError("Reopen decision must be a change artifact")
        decision = source(decision_ref)
        if reason not in decision or not re.search(r"(?<![A-Za-z0-9_.-])" + re.escape(operation) + r"(?![A-Za-z0-9_.-])", decision):
            raise GuardError("Decision must contain exact operation ID and reopening reason")
    elif reason or decision_ref:
        raise GuardError("Reopen arguments apply only to a recorded closed operation before work")
    tasks = source(entry["tasks"])
    if previous:
        if (previous.get("project"), previous.get("change"), previous.get("operation")) != (
                str(root), change, operation):
            raise GuardError("Previous checkpoint identity mismatch")
        old = {item["path"]: item["sha256"] for item in previous.get("sources", [])}
        if not old or old != {p: m["sha256"] for p, m in manifests.items()}:
            raise GuardError("Checkpoint stale: source set or bytes changed; reread and replan")
    for relative, manifest in manifests.items():
        _, current = read_source(root, relative)
        if current["sha256"] != manifest["sha256"]:
            raise GuardError("Source changed during checkpoint; retry: " + relative)
    boxes = re.findall(r"^- \[([ xX])\]", tasks, re.MULTILINE)
    headings = re.findall(r"^#{1,3} .+$", tasks, re.MULTILINE)
    return {
        "schema": "visualstruct-continuity/v1", "phase": phase,
        "purpose": "completion-report-only" if phase == "after" else "before-work-preconditions",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": str(root), "change": change, "operation": operation,
        "assignment": assignment,
        "global_tasks": {"completed": sum(b.lower() == "x" for b in boxes),
                         "total": len(boxes), "meaning": "top-level tasks, not time or operation coverage"},
        "latest_task_heading": headings[-1].strip() if headings else None,
        "operations": states, "sources": list(manifests.values()),
        "reopen": {"reason": reason, "decision_ref": decision_ref} if reason else None,
        "limits": [
            "Source declarations and evidence existence are not functional verification.",
            "Only registered blocks are classified; unknown blocks fail closed.",
            "No inference of approval, active process, next action or universal coverage.",
            "Hashes cover listed documents, not every product file or git commit.",
            "Concurrent edits after the final read remain possible; rerun before action.",
            "Unregistered new logs do not invalidate a checkpoint; registered edits require a fresh read.",
        ],
    }

def main() -> int:
    """Print fresh JSON or an actionable error; never write files."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True)
    parser.add_argument("--operation", required=True)
    parser.add_argument("--assignment-id", default="", help="ID from the current explicit instruction record")
    parser.add_argument("--phase", choices=["before", "after"], default="before")
    parser.add_argument("--reopen-reason", default="")
    parser.add_argument("--decision-ref", default="")
    parser.add_argument("--checkpoint", type=Path, help="Previously captured JSON; reject stale sources")
    parser.add_argument("--workflow-config", type=Path, help="Optional role protocol config; same harness, read-only")
    parser.add_argument("--task", help="Explicit role workflow task ID")
    parser.add_argument("--gate", choices=["before", "verify", "close", "after"], default="before")
    args = parser.parse_args()
    try:
        config = json.loads(CONFIG.read_text(encoding="utf-8-sig"))
        previous = json.loads(args.checkpoint.read_text(encoding="utf-8-sig")) if args.checkpoint else None
        result = checkpoint(ROOT, config, args.change, args.operation, Path.cwd(),
                            args.reopen_reason, args.decision_ref, previous, args.phase, args.assignment_id)
        if args.workflow_config:
            from role_workflow import evaluate
            if not args.task:
                raise GuardError("Workflow task required")
            workflow_config = json.loads(read_source(ROOT, str(args.workflow_config))[0])
            if workflow_config.get("change") != args.change or workflow_config.get("operation") != args.operation:
                raise GuardError("Workflow change/operation mismatch")
            # Continuity and role checkpoints are separate sections of one report.
            role_previous = previous.get("workflow") if previous else None
            result["workflow"] = evaluate(ROOT, workflow_config, args.task, args.gate, role_previous)
        elif args.task:
            raise GuardError("Workflow config required for task")
        print(json.dumps(result, ensure_ascii=True, indent=2))
        return 0
    except (GuardError, OSError, ValueError, KeyError) as exc:
        print("Continuity guard: " + str(exc), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
