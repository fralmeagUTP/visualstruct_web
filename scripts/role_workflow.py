"""Deterministic role gates for the existing continuity harness; no execution/writes."""
from __future__ import annotations
import json
from copy import deepcopy
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from check_session_continuity import GuardError, read_source

ROLES = {"specifications", "code", "quality", "visual", "documentation"}

def evaluate(root: Path, config: dict[str, Any], task_id: str, gate: str,
             previous: dict[str, Any] | None = None) -> dict[str, Any]:
    """Read current artifacts, then enforce a sequential workflow contract."""
    # Freeze caller-owned mutable input for this evaluation and its returned snapshot.
    config = deepcopy(config)
    root = root.resolve()
    def require(ok, message):
        if not ok:
            raise GuardError(message)
    require(gate in {"before", "verify", "close", "after"}, "Unknown workflow gate")
    require(config.get("schema") == "continuity-role-workflow/v1", "Unsupported workflow schema")
    require(Path(config["project_root"]).resolve() == root, "Wrong workflow project")
    require(set(config["roles"]) == ROLES, "Five role contracts required")
    manifests = {}
    def read(ref):
        text, manifest = read_source(root, ref)
        manifests[ref] = manifest
        return text
    def path(ref):
        require(isinstance(ref, str) and bool(ref.strip()), "Empty path")
        p = (root / ref).resolve()
        require(not Path(ref).is_absolute() and p.is_relative_to(root) and p != root,
                "Escaping or root write path: " + ref)
        return p
    def overlap(a, b):
        return a == b or a.is_relative_to(b) or b.is_relative_to(a)
    tasks = config["tasks"]
    require(task_id in tasks, "Unknown workflow task")
    required = {"objective", "role", "owner", "requirements", "base", "allowed_paths",
                "dependencies", "deliverables", "documentation", "evidence", "checks",
                "next_step", "state", "approval", "decisions", "reasoning"}
    for identifier, task in tasks.items():
        require(required <= set(task), "Incomplete task: " + identifier)
        require(task["state"] in {"pending", "active", "closed"}, "Invalid task state")
        require(task["role"] in ROLES and config["roles"][task["role"]]["enabled"], "Disabled/unknown role")
        contract = config["roles"][task["role"]]
        require(set(contract.get("required_checks", [])) <= set(task["checks"]), "Role checks missing")
        require(bool(task["objective"]) and bool(task["owner"]) and bool(task["next_step"]), "Missing objective/owner/next step")
        require(task["requirements"] and task["base"] and task["allowed_paths"] and task["deliverables"], "Empty task scope/base/deliverables")
        for ref in task["allowed_paths"]:
            p = path(ref)
            for protected in config.get("protected_paths", []):
                require(not overlap(p, path(protected)), "Protected write path: " + ref)
        for ref in task["deliverables"] + task["documentation"]:
            require(any(path(ref).is_relative_to(path(a)) for a in task["allowed_paths"]), "Deliverable outside owned paths")
        for dep in task["dependencies"]:
            require(dep in tasks and dep != identifier, "Invalid dependency")
    def visit(identifier, trail):
        require(identifier not in trail, "Dependency cycle")
        for dep in tasks[identifier]["dependencies"]:
            visit(dep, trail + [identifier])
    for identifier in tasks:
        visit(identifier, [])
    active = [(i, t) for i, t in tasks.items() if t["state"] == "active"]
    for n, (i, t) in enumerate(active):
        for j, other in active[n+1:]:
            require(not any(overlap(path(a), path(b)) for a in t["allowed_paths"] for b in other["allowed_paths"]),
                    "Overlapping ownership: " + i + " / " + j)
    require(len(active) <= 1, "Sequential pilot: multiple active writers")
    task = tasks[task_id]
    if gate != "after":
        require(task["state"] != "closed", "Closed work; new approved reopening task required")
        require(not active or active[0][0] == task_id, "Another writer holds the pilot")
    def closed_scope(t):
        """A fresh task ID cannot bypass closed scope; bind reviewed transitions."""
        bindings = t.get("closed_scope_decisions", {})
        require(isinstance(bindings, dict), "Closed-scope decisions must be a mapping")
        for predecessor, ref in bindings.items():
            require(predecessor in tasks and predecessor != task_id and
                    tasks[predecessor]["state"] == "closed", "Invalid closed predecessor")
            require(ref in t["decisions"], "Closed-scope decision must be a task decision")
        for predecessor, old in tasks.items():
            if predecessor == task_id or old["state"] != "closed":
                continue
            if not any(overlap(path(a), path(b)) for a in t["allowed_paths"] for b in old["allowed_paths"]):
                continue
            require(predecessor in bindings, "Closed scope overlaps: " + predecessor +
                    "; explicit reopening/successor decision required")
            ref = bindings[predecessor]
            require(ref in t["decisions"], "Closed-scope decision must be a task decision")
            decision = json.loads(read(ref))
            require(decision.get("status") == "resolved" and decision.get("approved") is True and
                    decision.get("predecessor") == predecessor and decision.get("task") == task_id and
                    decision.get("owner") == t["owner"] and
                    decision.get("allowed_paths") == t["allowed_paths"] and
                    isinstance(decision.get("reason"), str) and bool(decision["reason"].strip()),
                    "Invalid reopening/successor decision binding")
            require(decision.get("kind") in {"reopening", "successor"}, "Transition kind required")
            if decision["kind"] == "successor":
                require(isinstance(decision.get("new_scope"), str) and bool(decision["new_scope"].strip()) and
                        (t["objective"] != old["objective"] or t["requirements"] != old["requirements"]),
                        "Successor requires explicit new scope, not repeated closed work")
    def context(t):
        approval = json.loads(read(t["approval"]))
        require(approval.get("approved") is True and approval.get("owner") == t["owner"] and
                approval.get("allowed_paths") == t["allowed_paths"], "Scope approval missing/mismatched")
        for ref in t["decisions"]:
            decision = json.loads(read(ref))
            require(decision.get("status") == "resolved", "Pending decision")
        reasoning = t["reasoning"]
        require(reasoning.get("default") == "LOW", "LOW default required")
        if reasoning.get("current", "LOW") != "LOW":
            require(all(reasoning.get(x) for x in ["block", "reason", "scope", "return_to_low"]), "Unbounded reasoning escalation")
        for ref in t["requirements"] + t["base"]:
            read(ref)
    def verify(t, closing=False):
        inputs = sorted(set(t["requirements"] + t["base"] + t["deliverables"] + t["documentation"]))
        for ref in inputs:
            read(ref)
        expected = {ref: manifests[ref]["sha256"] for ref in inputs}
        records = [json.loads(read(ref)) for ref in t["evidence"]]
        def valid(e):
            require(e.get("executed") is True and e.get("result") == "passed" and type(e.get("exit_code")) is int and e["exit_code"] == 0,
                    "Required verification failed or not executed")
            require(e.get("inputs") == expected, "Evidence invalidated: input hashes changed")
            stamp = e.get("observed_at_utc")
            require(isinstance(stamp, str) and bool(re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|\+00:00)", stamp)),
                    "Evidence timestamp must be an ISO-8601 UTC datetime")
            try:
                observed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            except ValueError as exc:
                raise GuardError("Invalid UTC evidence timestamp") from exc
            require(observed.utcoffset() == timezone.utc.utcoffset(observed), "Evidence timestamp must be UTC")
        require(bool(t["checks"]), "Required checks missing")
        for check in t["checks"]:
            matches = [e for e in records if e.get("check") == check]
            require(len(matches) == 1, "Required check missing/ambiguous: " + check)
            valid(matches[0])
        if closing:
            require(bool(t["documentation"]), "Documentation deliverables required")
            qa = [e for e in records if e.get("kind") == "independent-qa"]
            require(len(qa) == 1, "Independent QA record required")
            valid(qa[0])
            require(qa[0].get("author") == t["owner"] and bool(qa[0].get("reviewer")) and
                    qa[0]["reviewer"] != t["owner"], "QA reviewer must differ from author")
            require(qa[0].get("role") == "quality" and config["roles"]["quality"]["enabled"], "QA role required")
    # Dependencies must still have valid closure evidence, not merely a closed flag.
    seen = set()
    def dependencies(t):
        for dep in t["dependencies"]:
            if dep in seen:
                continue
            seen.add(dep)
            require(tasks[dep]["state"] == "closed", "Dependency not closed: " + dep)
            context(tasks[dep]); dependencies(tasks[dep]); verify(tasks[dep], closing=True)
    context(task)
    if gate != "after" and task["state"] != "closed":
        closed_scope(task)
    dependencies(task)
    if gate in {"verify", "close"}:
        verify(task, closing=gate == "close")
    # Read existing owned files too, so before/after checkpoints catch changed work.
    for ref in task["deliverables"] + task["documentation"] + task["evidence"]:
        if path(ref).is_file():
            read(ref)
    current = {ref: m["sha256"] for ref, m in manifests.items()}
    if previous is not None:
        require(previous.get("project") == str(root) and previous.get("task") == task_id,
                "Checkpoint identity mismatch")
        require(previous.get("config") == config and previous.get("hashes") == current,
                "Stale checkpoint: config/source changed; reread and replan")
    for ref, manifest in manifests.items():
        require(read_source(root, ref)[1]["sha256"] == manifest["sha256"], "Concurrent source modification")
    return {"schema": "continuity-role-checkpoint/v1", "project": str(root), "task": task_id,
            "gate": gate, "purpose": "report-only" if gate == "after" else "declarative-preconditions",
            "observed_at_utc": datetime.now(timezone.utc).isoformat(), "config": config,
            "recovered_task": deepcopy(task), "hashes": current,
            "limits": ["No filesystem enforcement or agent launch.",
                       "Approval/reviewer identities are declarations, not authenticated independence.",
                       "No tests executed by validator; evidence must come from actual verification.",
                       "Unregistered files and edits after read are outside this snapshot."]}
