"""Independent graph shape and observed partial-frame checks for permanent QA."""
from __future__ import annotations
from math import isfinite


def assert_final_graph(state):
    assert state["structure"] == "graph"
    assert type(state["directed"]) is bool and type(state["weighted"]) is bool
    nodes, edges = state["nodes"], state["edges"]
    ids = [node["id"] for node in nodes]
    assert all(type(v) is str and str(int(v)) == v for v in ids)
    assert len(set(ids)) == len(ids)
    for node in nodes:
        assert node["label"] == node["value"] == node["id"]
        assert type(node["marked"]) is int and node["marked"] in (0, 1)
    keys = []
    for edge in edges:
        source, target, weight = edge["source"], edge["target"], edge["weight"]
        assert source in ids and target in ids
        assert type(weight) in (int, float) and isfinite(weight)
        keys.append((source, target) if state["directed"] else tuple(sorted((source, target))))
    assert len(set(keys)) == len(keys)
    assert state["weighted"] == any(edge["weight"] != 1 for edge in edges)
    metadata = state["metadata"]
    assert type(metadata["vertices_count"]) is int and metadata["vertices_count"] == len(nodes)
    assert type(metadata["edges_count"]) is int and metadata["edges_count"] == len(edges)
    assert type(metadata["is_empty"]) is bool and metadata["is_empty"] == (not nodes)


_C_PHASES = frozenset({"enter", "parameter", "scope_enter", "scope_exit", "declare", "write", "assignment", "statement", "condition", "operand", "call", "return", "allocate", "free", "break", "goto", "label", "stdout"})
_NON_C_PHASES = frozenset({"api_publication", "api_projection", "API_rejection", "caller_receipt", "caller"})


def _memory(memory, model):
    assert {"graph", "frames", "heap_nodes", "returned"} <= memory.keys()
    assert isinstance(memory["graph"], dict) and {"v", "a"} <= memory["graph"].keys()
    assert isinstance(memory["frames"], list) and isinstance(memory["heap_nodes"], list)
    retired = memory["freed_nodes" if model in {"bfs", "dfs"} else "retired_objects"]
    assert isinstance(retired, list)
    live = [n["id"] for n in memory["heap_nodes"]]; dead = [n["id"] for n in retired]
    assert len(set(live)) == len(live) and len(set(dead)) == len(dead) and set(live).isdisjoint(dead)
    ids = [f.get("id", f.get("frame_id")) for f in memory["frames"]]
    assert all(ids) and len(set(ids)) == len(ids)
    assert all(type(f["function"]) is str and f["function"] for f in memory["frames"])
    if model != "vertex":
        assert type(memory["allocations"]) is int and memory["allocations"] >= 0
        assert type(memory["frees"]) is int and memory["frees"] >= 0
        assert type(memory["console_stdout"]) is str
    return set(live), set(dead)


def _locals(memory, function):
    frames = [f for f in memory["frames"] if f["function"] == function]; assert frames
    values = dict(frames[-1]["parameters"])
    for scope in frames[-1]["scopes"]:
        values.update({k: c["value"] for k, c in scope["variables"].items()})
    return values


def _stored_value(before, after, event):
    import re
    name = event["name"]; values = _locals(after, event["function"])
    if re.fullmatch(r"[A-Za-z_]\w*", name): return values[name]
    if re.fullmatch(r"\*[A-Za-z_]\w*", name):
        address = values[name[1:]]
        assert type(address) is str and address.startswith("&")
        frame_id, scope_id, variable = address[1:].split(":")
        cells = [scope["variables"][variable] for frame in after["frames"] if frame["id"] == frame_id for scope in frame["scopes"] if scope["id"] == frame_id + ":" + scope_id]
        assert len(cells) == 1
        return cells[0]["value"]
    match = re.fullmatch(r"([A-Za-z_]\w*)\[([A-Za-z_]\w*|[0-9]+)(\+\+)?\]", name)
    if match:
        array, index, increment = match.groups()
        v = _locals(before if increment else after, event["function"])
        i = int(index) if index.isdigit() else v[index]
        if increment: i -= 1  # The observer emits the index increment before the array store.
        nodes = [n for n in after["heap_nodes"] if n["id"] == values[array]]
        assert len(nodes) == 1 and type(i) is int
        return nodes[0]["items"][i]
    match = re.fullmatch(r"([A-Za-z_]\w*)(->|\.)([A-Za-z_]\w*)", name); assert match, "Unverified write target"
    variable, operator, field = match.groups()
    if operator == ".": return values[variable][field]
    nodes = [n for n in after["heap_nodes"] if n["id"] == values[variable]]; assert len(nodes) == 1
    return nodes[0]["fields"][field]


def assert_observed_graph_frame(step, trace, index):
    frame = step["pedagogy"]; invariant = frame["invariant"]
    assert frame["state_before"] == step["state_snapshot"] and frame["state_after"] == step["state_after"]
    if invariant["holds"] is True:
        assert_final_graph(frame["state_after"]); return
    assert invariant["holds"] is None, "Explicit invariant failure"
    assert invariant["symbol"] == "?" and invariant["evidence"]
    active = [m for m in ("numeric", "construction", "vertex", "bfs", "dfs") if trace.get(m + "_instruction_model") is True]
    assert len(active) == 1, "Missing or ambiguous observer"
    model = active[0]; event = frame["instruction_event"]; phase = event["phase"]
    assert phase in _C_PHASES | _NON_C_PHASES, "Invented instruction phase"
    assert step["debug"]["stage"] == phase, "Event detached from observed step"
    before, after = frame["instruction_state_before"], frame["instruction_state_after"]
    old, retired_old = _memory(before, model); new, retired_new = _memory(after, model)
    assert frame["memory_state"] == after
    debug_key = {"numeric": "graph_memory", "vertex": "vertex_memory", "bfs": "bfs_memory", "dfs": "dfs_memory"}.get(model)
    if debug_key: assert step["debug"][debug_key] == after, "Detached observer memory"
    lines = trace["source_code"].splitlines()
    assert type(step["line_index"]) is int and 0 <= step["line_index"] < len(lines)
    assert step["line_text"] == lines[step["line_index"]]
    if phase in _NON_C_PHASES:
        assert index == len(trace["steps"]) - 1
        assert event.get("C_executed") is False or (model in {"bfs", "dfs"} and phase == "caller")
        assert old == new and retired_old == retired_new and before["graph"] == after["graph"]
        return
    # Legacy BFS/DFS omit the flag; an explicit denial or invalid value is never a C event.
    assert event.get("C_executed") is True or (model in {"bfs", "dfs"} and "C_executed" not in event)
    assert type(event["function"]) is str and event["function"]
    if "statement" in event: assert event["statement"] == step["line_text"]
    if "line_index" in event: assert event["line_index"] == step["line_index"]
    if "pos" in event:
        pos = event["pos"]; assert type(pos) is int and 0 <= pos < len(trace["source_code"])
        assert trace["source_code"].count("\n", 0, pos) == step["line_index"]
    memories = (before,) if phase in {"return", "scope_exit"} else (after,)
    assert any(any(f["function"] == event["function"] for f in m["frames"]) for m in memories)
    if model not in {"bfs", "dfs"}:
        c_steps = [s for s in trace["steps"] if s["pedagogy"]["instruction_event"].get("C_executed") is True]
        ledger = trace["C_instruction_events"]; assert len(c_steps) == len(ledger)
        ordinal = sum(s["pedagogy"]["instruction_event"].get("C_executed") is True for s in trace["steps"][:index])
        record = ledger[ordinal]; assert {"function", "phase", "line_index"} <= record.keys()
        assert all(event.get(k) == v for k, v in record.items()), "Detached C ledger event"
    if phase in {"condition", "operand"}: assert before == after, "Condition mutated memory"
    if phase == "enter":
        ids = lambda memory: {f.get("id", f.get("frame_id")) for f in memory["frames"]}
        assert len(ids(after) - ids(before)) == 1
    if phase == "allocate":
        assert len(new - old) == 1 and not old - new and retired_new == retired_old
        if model != "vertex": assert after["allocations"] == before["allocations"] + 1
    if phase == "free":
        assert len(old - new) == 1 and not new - old and retired_new - retired_old == old - new
        if model != "vertex": assert after["frees"] == before["frees"] + 1
    if phase == "write" and model in {"numeric", "construction"}:
        if "++" in event["name"]:
            import re
            variable = re.fullmatch(r"[A-Za-z_]\w*\[([A-Za-z_]\w*)\+\+\]", event["name"])[1]
            assert index > 0
            previous = trace["steps"][index - 1]["pedagogy"]
            prior_event = previous["instruction_event"]
            assert prior_event["phase"] == "write" and prior_event["name"] == variable
            assert prior_event["function"] == event["function"] and prior_event["line_index"] == event["line_index"]
            old_index = _locals(previous["instruction_state_before"], event["function"])[variable]
            assert prior_event["value"] == old_index + 1 == _locals(before, event["function"])[variable]
        assert _stored_value(before, after, event) == event["value"], "Written value detached from C storage"
