"""Independent oracle for the eleven small, explicitly scoped route cases.

This is not a C interpreter. Only reached physical writes in these fixtures are
supported; unknown writes fail rather than acquiring a missing-invariant waiver.
"""
from __future__ import annotations

from copy import deepcopy
import re
import ast
from typing import Any

CASES = {("avl", "insertar"), ("avl", "eliminar"),
         ("binary_heap", "insertar"), ("binary_heap", "extraer_raiz"),
         ("binary_heap", "limpiar"),
         *(("red_black", op) for op in ("insertar", "eliminar", "altura", "buscar", "inorden", "validar"))}
FIELDS = {"nro": "value", "izq": "left", "der": "right",
          "padre": "parent", "FE": "balance_factor", "rbt_color": "color"}


def _nodes(state: dict) -> dict:
    nodes = state["heap_nodes"]
    result = {n["id"]: {k: v for k, v in n.items() if k != "status"} for n in nodes}
    assert len(result) == len(nodes), "duplicate memory identity"
    return result


def _environment(state: dict) -> dict:
    frames = state.get("tree_frames", state.get("query_frames", []))
    assert frames, "write without C scope"
    return {**frames[-1]["parameters"], **frames[-1]["locals"]}


def _value(expression: str, state: dict) -> Any:
    expression = expression.strip()
    if expression in {"NULL", "ROJO", "NEGRO"}:
        return {"NULL": "NULL", "ROJO": "RED", "NEGRO": "BLACK"}[expression]
    if re.fullmatch(r"-?\d+", expression):
        return int(expression)
    parts = expression.split("->")
    value = state["head"] if parts[0] == "(*arbol)" else _environment(state)[parts[0]]
    for field in parts[1:]:
        assert value in _nodes(state), "read of non-live node"
        value = _nodes(state)[value][FIELDS[field]]
        assert value != "sin inicializar", "read of uninitialized field"
    return value


def _height(identity: str, nodes: dict, seen: set | None = None) -> int:
    if identity == "NULL":
        return 0
    seen = set() if seen is None else seen
    assert identity in nodes and identity not in seen
    return 1 + max(_height(nodes[identity]["left"], nodes, seen | {identity}),
                   _height(nodes[identity]["right"], nodes, seen | {identity}))


def _tree_write(before: dict, after: dict, text: str, phase: str) -> None:
    old, actual = _nodes(before), _nodes(after)
    expected = deepcopy(old)
    head = before["head"]
    added, removed = actual.keys() - old.keys(), old.keys() - actual.keys()
    if "malloc(" in text and phase in {"after", "allocate"}:
        assert len(added) == 1 and not removed, "one malloc reservation required"
        ident = next(iter(added))
        keys = {"id", "value", "left", "right", "parent"}
        keys.add("balance_factor" if "avl_insert_model" in before else "color")
        item = {k: "sin inicializar" for k in keys}
        item["id"] = ident
        if "color" in keys:
            item["initialized"] = 0
        expected[ident] = item
    elif phase == "free":
        assert text == "free(z);" and not added
        ident = _value("z", before)
        assert removed == {ident}
        del expected[ident]
    elif phase in {"after", "initialize", "link", "recolor"}:
        statement = re.sub(r"^if \((?:v|\*arbol)\)\s*", "", text)
        if "=" in statement and not any(op in statement for op in ("==", "!=", "<=", ">=")):
            parts = statement.rstrip(";").split("=")
            lhs = [x.strip() for x in parts[:-1]]
            rhs = parts[-1].strip()
            if "avl_altura(" in rhs and any("->" in target for target in lhs):
                assert rhs == "avl_altura(nodo->der) - avl_altura(nodo->izq)"
                value = _height(_value("nodo->der", before), old) - _height(_value("nodo->izq", before), old)
            elif any("->" in target or target.startswith("*") for target in lhs):
                value = _value(rhs, before)
            else:
                value = None  # A local write cannot change a reservation.
            for target in lhs:
                if target in {"*raiz", "*arbol", "*root"}:
                    head = value
                elif "->" in target:
                    alias, field = target.rsplit("->", 1)
                    ident = _value(alias, before)
                    assert ident in expected
                    expected[ident][FIELDS[field]] = value
                    if "initialized" in expected[ident]:
                        expected[ident]["initialized"] |= {"nro": 1, "izq": 2, "der": 4, "padre": 8, "rbt_color": 16}[field]
    assert actual == expected, (text, "unexplained node write/allocation/free")
    assert after["head"] == head, (text, "unexplained root publication")


def _heap_write(before: dict, after: dict, text: str, phase: str) -> None:
    objects = deepcopy(before["heap_allocations"])
    size, capacity, ref = before["size"], before["capacity"], before["heap_data_reference"]
    output = deepcopy(before.get("caller_output"))
    def live() -> dict:
        found = [o for o in objects if o["live"] and o["id"] == ref]
        assert len(found) == 1, "read/write requires live published storage"
        return found[0]
    def cell(index: int) -> dict:
        cells = live()["cells"]
        assert 0 <= index < len(cells)
        return cells[index]
    if phase == "free":
        assert text == "free(m->datos);"
        live().update(live=False, cells=[])
        ref = "indeterminado (" + ref + " historico)"
    elif phase == "allocation":
        assert "realloc(" in text and ref == "NULL", "focal clear reserves fresh buffer"
        n = _environment(before)["nueva_capacidad"]
        added = [o for o in after["heap_allocations"] if o["id"] not in {o["id"] for o in objects}]
        assert len(added) == 1 and n > 0
        objects.append({"id": added[0]["id"], "capacity": n, "live": True,
                        "cells": [{"index": i, "initialized": False, "value": None} for i in range(n)]})
    elif phase == "assignment":
        if text == "m->cantidad++;":
            size += 1
        elif text == "m->cantidad--;":
            size -= 1
        elif text == "m->cantidad = 0;":
            size = 0
        elif text == "m->capacidad = 0;":
            capacity = 0
        elif text == "m->capacidad = nueva_capacidad;":
            capacity = _environment(before)["nueva_capacidad"]
        elif text == "m->datos = NULL;":
            ref = "NULL"
        elif text == "m->datos = nuevos_datos;":
            ref = _environment(before)["nuevos_datos"]
        elif text == "*resultado = m->datos[0];":
            assert cell(0)["initialized"] is True
            output = {"initialized": True, "value": cell(0)["value"]}
        elif text == "m->datos[m->cantidad] = valor;":
            cell(size).update(initialized=True, value=_environment(before)["valor"])
        elif text == "m->datos[0] = m->datos[m->cantidad];":
            assert cell(size)["initialized"] is True
            cell(0).update(initialized=True, value=cell(size)["value"])
        elif text in {"*a = *b;", "*b = temp;"}:
            env = _environment(before)
            def pointed(name: str) -> int:
                match = re.fullmatch(r"&" + re.escape(ref) + r"\[(\d+)\]", env[name])
                assert match
                return int(match[1])
            if text == "*a = *b;":
                assert cell(pointed("b"))["initialized"] is True
                cell(pointed("a"))["value"] = cell(pointed("b"))["value"]
            else:
                cell(pointed("b"))["value"] = env["temp"]
    assert after["heap_allocations"] == objects, (text, "unexplained buffer change")
    assert (after["size"], after["capacity"], after["heap_data_reference"]) == (size, capacity, ref)
    assert after.get("caller_output") == output


def _predicate(rows: list[str], index: int, state: dict, phase: str, operand: str | None = None) -> bool:
    """Evaluate only reached fixture predicates from C and prior live operands."""
    text = " ".join(rows[index:])
    if re.match(r"\s*(?:}\s*else\s+)?(?:if|while)\s*\(", text):
        start = text.index("(")
        depth = 1
        end = start + 1
        while depth:
            depth += (text[end] == "(") - (text[end] == ")")
            end += 1
        expr = text[start+1:end-1]
    else:
        prefix = rows[index].split("?", 1)[0]
        assert "?" in rows[index]
        expr = prefix[prefix.rfind("(")+1:].rstrip(") ")
    if phase == "operand":
        parts = [part.strip() for part in expr.split("&&")]
        assert operand in parts, "operand absent from native condition"
        expr = parts[parts.index(operand)]
    tokens = re.findall(r"->|&&|\|\||==|!=|<=|>=|[A-Za-z_]\w*|\d+|[()+*/!<>\[\],-]", expr)
    output = []
    constants = {"NULL": "NULL", "ROJO": "r", "NEGRO": "n", "INT_MAX": 2147483647, "MONTICULO_MIN": 0}
    functions = {"comparar": "compare", "asegurar_capacidad": "reserve"}
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token == "*" and (i == 0 or tokens[i-1] in {"(", "&&", "||", "!"}):
            assert tokens[i+1] in {"arbol", "raiz", "root"}
            output.append("head()")
            i += 2
            continue
        if re.fullmatch(r"[A-Za-z_]\w*", token):
            if token in constants:
                output.append(repr(constants[token]))
            elif i+1 < len(tokens) and tokens[i+1] == "(":
                assert token in functions, "unsupported predicate call"
                output.append(functions[token])
            else:
                chain = token
                while i+2 < len(tokens) and tokens[i+1] == "->":
                    chain += "->" + tokens[i+2]
                    i += 2
                if chain == "m->datos" and i+1 < len(tokens) and tokens[i+1] == "[":
                    output.append("cell(")
                    i += 1
                else:
                    output.append("read(" + repr(chain) + ")")
        else:
            output.append({"&&": " and ", "||": " or ", "!": " not ", "]": ")"}.get(token, token))
        i += 1
    env = _environment(state)
    def read(name: str) -> Any:
        if name.startswith("m->"):
            return {"m->cantidad": state["size"], "m->capacidad": state["capacity"], "m->datos": state["heap_data_reference"], "m->tipo": 0}[name]
        value = _value(name, state)
        assert value != "sin inicializar"
        return {"RED": "r", "BLACK": "n"}.get(value, value) if isinstance(value, str) else value
    def cell(index: int) -> int:
        live = [o for o in state["heap_allocations"] if o["live"] and o["id"] == state["heap_data_reference"]]
        assert len(live) == 1 and 0 <= index < len(live[0]["cells"])
        c = live[0]["cells"][index]
        assert c["initialized"] is True
        return c["value"]
    def truth(value: Any) -> bool:
        return value != "NULL" if isinstance(value, str) else bool(value)
    def evaluate(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Call):
            assert isinstance(node.func, ast.Name) and not node.keywords
            args = [evaluate(a) for a in node.args]
            if node.func.id == "read":
                return read(*args)
            if node.func.id == "head":
                assert not args
                return state["head"]
            if node.func.id == "cell":
                return cell(*args)
            if node.func.id == "compare":
                assert args[0] == 0
                return args[1] < args[2]
            if node.func.id == "reserve":
                # These successful finite fixtures have a live published buffer
                # after reserve. Its size and contents are checked separately.
                assert args[0] == "M1" and args[1] > 0
                return state["capacity"] >= args[1] and state["heap_data_reference"] != "NULL"
            raise AssertionError("unknown predicate function")
        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.Not):
                return not truth(value)
            assert isinstance(node.op, ast.USub)
            return -value
        if isinstance(node, ast.BoolOp):
            for child in node.values:
                value = truth(evaluate(child))
                if isinstance(node.op, ast.And) and not value:
                    return False
                if isinstance(node.op, ast.Or) and value:
                    return True
            return isinstance(node.op, ast.And)
        if isinstance(node, ast.BinOp):
            a, b = evaluate(node.left), evaluate(node.right)
            if isinstance(node.op, ast.Add): return a+b
            if isinstance(node.op, ast.Sub): return a-b
            if isinstance(node.op, ast.Mult): return a*b
            assert isinstance(node.op, ast.Div) and b
            return int(a/b)
        assert isinstance(node, ast.Compare) and len(node.ops) == 1
        a, b = evaluate(node.left), evaluate(node.comparators[0])
        op = node.ops[0]
        if isinstance(op, ast.Eq): return a == b
        if isinstance(op, ast.NotEq): return a != b
        if isinstance(op, ast.Lt): return a < b
        if isinstance(op, ast.Gt): return a > b
        if isinstance(op, ast.LtE): return a <= b
        assert isinstance(op, ast.GtE)
        return a >= b
    return truth(evaluate(ast.parse("".join(output).strip(), mode="eval").body))


def _projection(state: dict, structure: str) -> None:
    """Recompute the visible partial projection without asserting TAD validity."""
    if structure == "binary_heap":
        live = [o for o in state["heap_allocations"] if o["live"] and o["id"] == state["heap_data_reference"]]
        limit = state.get("heap_written", state["size"])
        if state.get("heap_extract_model"):
            limit = state["size"]
        expected = [] if not live else [c["value"] for c in live[0]["cells"][:limit]]
        assert state["array"] == expected, "invented logical heap contents"
        assert state["empty"] is (state["size"] == 0)
        return
    nodes = _nodes(state)
    reached = set()
    def visible(ident: str) -> dict | None:
        if ident == "NULL" or ident in reached:
            return None
        assert ident in nodes, "projection dereferences retired node"
        reached.add(ident)
        node = nodes[ident]
        left, right = visible(node["left"]), visible(node["right"])
        out = {"value": node["value"], "left": left, "right": right}
        if structure == "red_black":
            out["color"] = node["color"]
        else:
            out["balance_factor"] = node["balance_factor"]
            out["height"] = 1 + max(left["height"] if left else 0, right["height"] if right else 0)
        return out
    assert state["root"] == visible(state["head"]), "invented projected tree"
    assert state["size"] == len(reached) and state["empty"] is (not reached)


def _stable_heap(state: dict) -> None:
    """Compute min-heap and array/tree/count agreement from final data."""
    array = state["array"]
    assert len(array) == state["size"] <= state["capacity"]
    assert all(type(v) is int for v in array)
    assert all(array[(i-1)//2] <= array[i] for i in range(1, len(array))), "invalid final min-heap"
    def tree(i: int) -> dict | None:
        return None if i >= len(array) else {"value": array[i], "left": tree(2*i+1), "right": tree(2*i+2)}
    assert state["root"] == tree(0), "heap tree/array mismatch"


def _scope_causality(before: dict, after: dict, text: str, phase: str) -> None:
    """Require frame lifetimes and local writes to belong to this statement."""
    a = before.get("tree_frames", before.get("query_frames", []))
    b = after.get("tree_frames", after.get("query_frames", []))
    old, new = {f["id"]: f for f in a}, {f["id"]: f for f in b}
    assert len(old) == len(a) and len(new) == len(b)
    if phase == "enter":
        assert len(b) == len(a) + 1 and b[:-1] == a
        assert re.search(r"\b" + re.escape(b[-1]["function"]) + r"\s*\(", text)
        assert not b[-1]["locals"], "future locals at function entry"
    elif phase == "return" and a:
        assert len(b) == len(a) - 1 and b == a[:-1]
        assert text == "}" or "return" in text or text.startswith("if ")
    else:
        assert old.keys() == new.keys(), "invented scope creation/removal"
        for ident in old:
            for kind in ("parameters", "locals"):
                left, right = old[ident][kind], new[ident][kind]
                for name in left.keys() | right.keys():
                    if left.get(name) == right.get(name):
                        continue
                    assert ident == a[-1]["id"], "write to suspended caller"
                    if phase == "free":
                        assert isinstance(left.get(name), str) and right.get(name) == left[name] + " [valor indeterminado; identidad historica]"
                    elif phase == "scope_exit":
                        assert text == "}" and name in {"s", "tmp"} and name not in right
                    else:
                        assert re.search(r"\b" + re.escape(name) + r"\s*(?:[+*/-]?=|,|;)", text), "local write absent from C statement"
                        assert phase in {"call", "resume", "after", "local", "assignment", "declaration", "allocate", "allocation"}
                        if phase in {"call", "declaration"}:
                            assert right[name] == "sin inicializar", "future call result"


def _stable_tree(root: dict | None, structure: str) -> tuple[list[int], int]:
    seen = set()
    def visit(node: dict | None, low: int | None, high: int | None) -> tuple[list[int], int, int]:
        if node is None:
            return [], 0, 1
        assert id(node) not in seen, "cycle or shared node"
        seen.add(id(node))
        v = node["value"]
        assert type(v) is int and (low is None or low < v) and (high is None or v < high), "strict BST order"
        left, lh, lb = visit(node["left"], low, v)
        right, rh, rb = visit(node["right"], v, high)
        height = 1 + max(lh, rh)
        if structure == "avl":
            assert node["height"] == height and node["balance_factor"] == rh - lh and abs(rh - lh) <= 1
        if structure == "red_black":
            assert node["color"] in {"RED", "BLACK"} and lb == rb, "RN color/black height"
            if node["color"] == "RED":
                assert all(c is None or c["color"] == "BLACK" for c in (node["left"], node["right"])), "red-red edge"
        return left + [v] + right, height, lb + int(node.get("color") == "BLACK")
    values, height, _ = visit(root, None, None)
    if structure == "red_black" and root is not None:
        assert root["color"] == "BLACK", "root must be black"
    return values, height


def _live_tree(state: dict, structure: str) -> dict | None:
    nodes = _nodes(state)
    reached = set()
    def visit(ident: str, parent: str) -> dict | None:
        if ident == "NULL":
            return None
        assert ident in nodes and ident not in reached, "cycle/shared/dangling identity"
        reached.add(ident)
        n = nodes[ident]
        assert n["parent"] == parent, "wrong parent identity"
        out = {"value": n["value"], "left": visit(n["left"], ident), "right": visit(n["right"], ident)}
        if structure == "red_black":
            out["color"] = n["color"]
        else:
            out["balance_factor"] = n["balance_factor"]
            out["height"] = 1 + max(_height(n["left"], nodes), _height(n["right"], nodes))
        return out
    root = visit(state["head"], "NULL")
    assert reached == nodes.keys(), "final detached live reservation"
    _stable_tree(root, structure)
    return root


def _memory_cards(cards: list[dict], live: dict, retired: dict) -> None:
    """Authenticate every card against live objects or causal retired versions."""
    ids = [card["id"] for card in cards]
    assert len(ids) == len(set(ids)), "duplicate memory card"
    shown_live = set()
    for card in cards:
        ident = card["id"]
        assert card["address"] == ident
        if card.get("freed", False):
            assert card["freed"] is True and card["allocated"] is False, "contradictory freed-card status"
            assert ident not in live and ident in retired, "invented freed memory card"
            versions = retired[ident]
        else:
            assert card.get("freed") is False and card["allocated"] is True
            assert ident in live, "invented live memory card"
            shown_live.add(ident)
            versions = [live[ident]]
        assert any(all(k in card and card[k] == v for k, v in version.items() if k != "status")
                   for version in versions), "invented memory contents"
    assert shown_live == live.keys(), "missing live memory card"


def _memory_events(records: list[dict], expected_ids: set, objects: dict) -> None:
    """Events require unique reservations and authentic available content."""
    ids = [obj["id"] for obj in records]
    assert len(ids) == len(set(ids)) and set(ids) == expected_ids, "duplicated/invented memory event"
    for obj in records:
        assert obj["address"] == obj["id"]
        assert all(obj[field] == value for field, value in objects[obj["id"]].items()
                   if field != "status" and field in obj), "invented memory event contents"


def _retire_objects(retired: dict, old: dict, new: dict) -> None:
    """Record contents at a proved free; reuse cannot rewrite that history."""
    for ident in old.keys() - new.keys():
        assert ident not in retired, "reservation freed twice"
        historical = deepcopy(old[ident])
        if "live" in historical:
            historical["live"] = False
        versions = [historical]
        if "cells" in historical:
            # The buffer renderer also represents terminated storage without
            # readable cells. Both forms originate at this same proven free.
            depleted = deepcopy(historical)
            depleted["cells"] = []
            versions.append(depleted)
        retired[ident] = versions


def assert_hierarchical_case(body: dict, structure: str, operation: str,
                             seed: list[int], payload: dict) -> None:
    """Check scoped C writes and independently stable final state/query results."""
    assert (structure, operation) in CASES, "no global unknown-invariant exemption"
    assert seed == ([] if operation == "insertar" else [8, 4, 12]), "only diagnosed fixtures supported"
    assert payload == ({"value": "8"} if operation in {"insertar", "eliminar", "buscar"} else {}), "only diagnosed payload supported"
    trace = body["execution_trace"]
    rows = trace["source_code"].replace("\r\n", "\n").split("\n")
    steps = trace["steps"]
    readonly = structure == "red_black" and operation in {"altura", "buscar", "inorden", "validar"}
    retired: dict = {}
    for index, step in enumerate(steps):
        ped = step["pedagogy"]
        assert step["step_index"] == index
        li = step["line_index"]
        assert type(li) is int and 0 <= li < len(rows) and rows[li] == step["line_text"]
        assert ped["source"] == {"line_index": li, "line_text": rows[li]}
        assert ped["structure"] == structure and ped["operation"] == operation
        assert ped["state_before"] == step["state_snapshot"] and ped["state_after"] == step["state_after"]
        if index:
            assert steps[index - 1]["state_after"] == step["state_snapshot"], "discontinuous frame"
        # This exact list of producers explicitly reports unknown. This field is
        # checked for fidelity, never used as evidence that a partial TAD is valid.
        assert ped["invariant"]["holds"] is None
        event = ped["instruction_event"]
        phase = event["phase"]
        assert phase in {"caller_enter", "caller", "enter", "call", "resume", "return", "condition", "operand", "after", "assignment", "declaration", "scope_exit", "break", "local", "initialize", "link", "recolor", "free", "allocate", "allocation", "printf"}, "invented instruction event"
        assert ped["case"] == phase
        expected_phase = (event["scope"] if structure == "binary_heap" else operation) + "-" + phase
        assert ped["phase"]["id"] == expected_phase
        text = rows[li].strip()
        before, after = step["state_snapshot"], ped["memory_state"]
        _scope_causality(before, after, text, phase)
        _projection(before, structure)
        _projection(after, structure)
        if index < len(steps) - 1:
            assert after == step["state_after"]
        if phase in {"condition", "operand"}:
            assert type(event["condition"]) is bool
            assert ped["condition"]["result"] == event["condition"] == step["condition_result"]
            assert event["condition"] is _predicate(rows, li, before, phase, event.get("expression")), ("wrong C predicate result", text, phase, event["condition"], _predicate(rows, li, before, phase, event.get("expression")))
            assert text.lstrip("} ").startswith(("if", "else if", "while")) or "?" in text or "&&" in text
        if phase in {"free", "allocation", "allocate"}:
            assert ("free(" if phase == "free" else "alloc(") in text
        if "heap_nodes" in before:
            _tree_write(before, after, text, phase)
            old, new = _nodes(before), _nodes(after)
        else:
            _heap_write(before, after, text, phase)
            old = {o["id"]: o for o in before["heap_allocations"] if o["live"]}
            new = {o["id"]: o for o in after["heap_allocations"] if o["live"]}
        memory = ped["memory"]
        assert not memory["dangling_references"]
        _memory_cards(memory["objects_before"], old, retired)
        added, removed = new.keys() - old.keys(), old.keys() - new.keys()
        assert not added.intersection(retired), "retired identity reused as live reservation"
        _retire_objects(retired, old, new)
        _memory_cards(memory["objects_after"], new, retired)
        for key, expected_ids, objects in (("allocated_objects", added, new), ("freed_objects", removed, old)):
            _memory_events(memory[key], expected_ids, objects)
        assert memory["event"] == ("allocation" if added else "free" if removed else "none")
        if readonly:
            assert old == new and before["head"] == after["head"], "readonly mutation"
    initial = steps[0]["state_snapshot"]
    if structure == "binary_heap":
        assert sorted(initial["array"]) == sorted(seed) and initial["size"] == len(seed)
    else:
        assert _stable_tree(initial["root"], structure)[0] == sorted(seed)
        assert _live_tree(initial, structure) == initial["root"]
    final = body["visual_state"]
    assert steps[-1]["state_after"] == final
    native = steps[-1]["pedagogy"]["memory_state"]
    expected = sorted(seed)
    if operation == "insertar":
        expected = sorted([*seed, int(payload["value"])])
    elif operation == "eliminar":
        expected.remove(int(payload["value"]))
    elif operation == "extraer_raiz":
        expected.remove(min(seed))
    elif operation == "limpiar":
        expected = []
    assert final["size"] == len(expected) and final["empty"] is (not expected)
    if structure == "binary_heap":
        array = final["array"]
        assert sorted(array) == expected and len(array) == final["size"]
        _stable_heap(final)
        assert native["array"] == array and native["size"] == final["size"] and native["capacity"] == final["capacity"]
        assert final["capacity"] >= final["size"]
        if operation == "extraer_raiz":
            assert body["result"] == min(seed) and native["caller_output"] == {"initialized": True, "value": min(seed)}
    else:
        values, height = _stable_tree(final["root"], structure)
        assert values == expected and final["height"] == height
        assert final["root"] == _live_tree(native, structure)
        assert final["traversals"]["inorden"] == expected
        # Validity is calculated above; metadata is checked only afterwards.
        assert final["validation"] is True
        if readonly:
            assert steps[0]["state_snapshot"]["root"] == final["root"]
            if operation == "inorden":
                assert body["result"] == expected
            elif operation == "altura":
                assert body["result"] == height
            elif operation == "validar":
                assert body["result"] is True and native["wrapper_result"] == 1 and native["validation"] is True
            elif operation == "buscar":
                assert body["result"] is (int(payload["value"]) in seed)
