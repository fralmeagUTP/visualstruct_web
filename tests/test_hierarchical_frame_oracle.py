"""Pure negative controls for the scoped independent hierarchical oracle."""
from __future__ import annotations

from copy import deepcopy
import pytest
from _hierarchical_frame_oracle import assert_hierarchical_case, _stable_tree, _live_tree, _tree_write, _heap_write, _stable_heap, _predicate, _memory_cards, _retire_objects, _memory_events


def _fixture() -> dict:
    """Hand-built healthy RN state and wrapper boundary; no producer imports."""
    def leaf(value: int) -> dict:
        return {"value": value, "color": "RED", "left": None, "right": None}
    root = {"value": 8, "color": "BLACK", "left": leaf(4), "right": leaf(12)}
    final = {"root": root, "height": 2, "size": 3, "empty": False,
             "validation": True, "traversals": {"inorden": [4, 8, 12]}}
    nodes = [{"id": "N1", "value": 8, "color": "BLACK", "left": "N2", "right": "N3", "parent": "NULL", "status": "linked"},
             {"id": "N2", "value": 4, "color": "RED", "left": "NULL", "right": "NULL", "parent": "N1", "status": "linked"},
             {"id": "N3", "value": 12, "color": "RED", "left": "NULL", "right": "NULL", "parent": "N1", "status": "linked"}]
    before = {**deepcopy(final), "head": "N1", "heap_nodes": nodes, "tree_frames": [], "wrapper_result": None}
    entered = deepcopy(before)
    entered["tree_frames"] = [{"id": "F1", "function": "ejecutar_validar", "parameters": {"raiz": "N1"}, "locals": {}}]
    returned = deepcopy(before)
    returned["wrapper_result"] = 1
    source = "int ejecutar_validar(RBT raiz) {\n    return rbt_validar(raiz);\n}\n"
    rows = source.splitlines()
    def step(index: int, old: dict, native: dict, phase: str) -> dict:
        after = deepcopy(final if phase == "return" else native)
        objects = [{**n, "address": n["id"], "allocated": True, "freed": False} for n in nodes]
        ped = {"structure": "red_black", "operation": "validar", "source": {"line_index": index, "line_text": rows[index]},
               "state_before": deepcopy(old), "state_after": after, "memory_state": deepcopy(native),
               "invariant": {"holds": None}, "case": phase, "phase": {"id": "validar-" + phase},
               "instruction_event": {"phase": phase, "condition": None},
               "memory": {"event": "none", "objects_before": deepcopy(objects), "objects_after": deepcopy(objects), "allocated_objects": [], "freed_objects": [], "dangling_references": []}}
        return {"step_index": index, "line_index": index, "line_text": rows[index], "state_snapshot": deepcopy(old), "state_after": after, "pedagogy": ped}
    return {"result": True, "visual_state": deepcopy(final), "execution_trace": {"source_code": source, "steps": [step(0, before, entered, "enter"), step(1, entered, returned, "return")]}}


def _check(body: dict) -> None:
    assert_hierarchical_case(body, "red_black", "validar", [8, 4, 12], {})


def test_independent_healthy_boundary_fixture() -> None:
    _check(_fixture())


@pytest.mark.parametrize("corruption", ["unknown_event", "fabricated_allocation", "fabricated_free", "memory_value", "duplicate_memory", "dangling", "unmapped_source", "false_invariant", "true_certificate", "discontinuity", "future_local", "bad_parent", "wrong_return", "bad_final_root", "bad_final_height", "wrong_input"])
def test_scoped_oracle_rejects_corruption(corruption: str) -> None:
    body = _fixture()
    steps = body["execution_trace"]["steps"]
    first, last = steps
    p = first["pedagogy"]
    if corruption == "unknown_event":
        p["instruction_event"]["phase"] = p["case"] = "invented"
        p["phase"]["id"] = "validar-invented"
    elif corruption == "fabricated_allocation":
        p["memory"]["allocated_objects"] = [{"id": "N999"}]
    elif corruption == "fabricated_free":
        p["memory"]["freed_objects"] = [{"id": "N1"}]
    elif corruption == "memory_value":
        p["memory"]["objects_after"][0]["value"] = 999
    elif corruption == "duplicate_memory":
        p["memory"]["objects_after"].append(deepcopy(p["memory"]["objects_after"][0]))
    elif corruption == "dangling":
        p["memory"]["dangling_references"] = ["N1"]
    elif corruption == "unmapped_source":
        first["line_index"] = None
    elif corruption in {"false_invariant", "true_certificate"}:
        p["invariant"]["holds"] = corruption == "true_certificate"
    elif corruption == "discontinuity":
        last["state_snapshot"]["wrapper_result"] = 999
        last["pedagogy"]["state_before"] = deepcopy(last["state_snapshot"])
    elif corruption == "future_local":
        p["memory_state"]["tree_frames"][0]["locals"]["future"] = 7
    elif corruption == "bad_parent":
        last["pedagogy"]["memory_state"]["heap_nodes"][1]["parent"] = "NULL"
    elif corruption == "wrong_return":
        body["result"] = False
    elif corruption == "bad_final_root":
        body["visual_state"]["root"]["color"] = "RED"
    elif corruption == "bad_final_height":
        body["visual_state"]["height"] = 3
    elif corruption == "wrong_input":
        first["state_snapshot"]["root"]["left"]["value"] = 3
        p["state_before"] = deepcopy(first["state_snapshot"])
    with pytest.raises((AssertionError, KeyError, TypeError)):
        _check(body)


def test_unknown_invariant_has_no_other_structure_exemption() -> None:
    with pytest.raises(AssertionError):
        assert_hierarchical_case(_fixture(), "abb", "validar", [8, 4, 12], {})


@pytest.mark.parametrize("corruption", ["order", "black_height", "red_red", "root_red", "color"])
def test_independent_rn_final_rules_reject_corruption(corruption: str) -> None:
    root = _fixture()["visual_state"]["root"]
    if corruption == "order":
        root["left"]["value"] = 9
    elif corruption == "black_height":
        root["left"]["color"] = "BLACK"
    elif corruption == "red_red":
        root["left"]["left"] = {"value": 2, "color": "RED", "left": None, "right": None}
    elif corruption == "root_red":
        root["color"] = "RED"
    else:
        root["right"]["color"] = "BLUE"
    with pytest.raises(AssertionError):
        _stable_tree(root, "red_black")


@pytest.mark.parametrize("corruption", ["height", "FE", "imbalance"])
def test_independent_avl_final_rules_reject_corruption(corruption: str) -> None:
    node = {"value": 8, "left": None, "right": None, "height": 1, "balance_factor": 0}
    if corruption == "height":
        node["height"] = 9
    elif corruption == "FE":
        node["balance_factor"] = 1
    else:
        node["left"] = {"value": 4, "left": {"value": 2, "left": None, "right": None, "height": 1, "balance_factor": 0}, "right": None, "height": 2, "balance_factor": -1}
        node.update(height=3, balance_factor=-2)
    with pytest.raises(AssertionError):
        _stable_tree(node, "avl")


def test_native_graph_rejects_cycle_or_shared_identity() -> None:
    native = _fixture()["execution_trace"]["steps"][-1]["pedagogy"]["memory_state"]
    native["heap_nodes"][1]["left"] = "N1"
    with pytest.raises(AssertionError):
        _live_tree(native, "red_black")


def test_tree_write_rejects_wrong_rhs_even_when_only_correct_field_changes() -> None:
    before = _fixture()["execution_trace"]["steps"][0]["state_snapshot"]
    before["tree_frames"] = [{"id": "F1", "parameters": {"n": "N2"}, "locals": {}}]
    after = deepcopy(before)
    after["heap_nodes"][1]["color"] = "BLUE"
    with pytest.raises(AssertionError):
        _tree_write(before, after, "n->rbt_color = NEGRO;", "recolor")


def test_heap_write_rejects_invented_store_value() -> None:
    before = {"size": 0, "capacity": 1, "heap_data_reference": "A1", "query_frames": [{"parameters": {"valor": 8}, "locals": {}}], "heap_allocations": [{"id": "A1", "capacity": 1, "live": True, "cells": [{"index": 0, "initialized": False, "value": None}]}]}
    after = deepcopy(before)
    after["heap_allocations"][0]["cells"][0].update(initialized=True, value=999)
    with pytest.raises(AssertionError):
        _heap_write(before, after, "m->datos[m->cantidad] = valor;", "assignment")


@pytest.mark.parametrize("corruption", ["parent", "capacity", "tree"])
def test_independent_final_heap_rejects_corruption(corruption: str) -> None:
    state = {"array": [4, 8, 12], "size": 3, "capacity": 3,
             "root": {"value": 4, "left": {"value": 8, "left": None, "right": None}, "right": {"value": 12, "left": None, "right": None}}}
    _stable_heap(state)
    if corruption == "parent":
        state["array"] = [8, 4, 12]
        state["root"]["value"] = 8
        state["root"]["left"]["value"] = 4
    elif corruption == "capacity":
        state["capacity"] = 2
    else:
        state["root"]["right"]["value"] = 99
    with pytest.raises(AssertionError):
        _stable_heap(state)


def test_coherent_fabricated_intermediate_projection_is_rejected() -> None:
    body = _fixture()
    step = body["execution_trace"]["steps"][0]
    step["state_after"]["root"]["left"]["value"] = 99
    step["pedagogy"]["state_after"] = deepcopy(step["state_after"])
    step["pedagogy"]["memory_state"] = deepcopy(step["state_after"])
    following = body["execution_trace"]["steps"][1]
    following["state_snapshot"] = deepcopy(step["state_after"])
    following["pedagogy"]["state_before"] = deepcopy(following["state_snapshot"])
    with pytest.raises(AssertionError, match="invented projected tree"):
        _check(body)



def _condition_fixture() -> dict:
    body = _fixture()
    trace = body["execution_trace"]
    trace["source_code"] = "int ejecutar_validar(RBT raiz) {\n    if (raiz == NULL) return 1;\n    return rbt_validar(raiz);\n}\n"
    first, last = trace["steps"]
    native = deepcopy(first["pedagogy"]["memory_state"])
    middle = deepcopy(first)
    middle.update(step_index=1, line_index=1, line_text="    if (raiz == NULL) return 1;", state_snapshot=deepcopy(native), state_after=deepcopy(native), condition_result=False)
    p = middle["pedagogy"]
    p.update(state_before=deepcopy(native), state_after=deepcopy(native), memory_state=deepcopy(native),
             case="condition", phase={"id": "validar-condition"}, condition={"result": False},
             source={"line_index": 1, "line_text": middle["line_text"]},
             instruction_event={"phase": "condition", "condition": False})
    last.update(step_index=2, line_index=2)
    last["pedagogy"]["source"]["line_index"] = 2
    trace["steps"] = [first, middle, last]
    return body


def test_independent_predicate_agrees_with_prior_live_pointer() -> None:
    _check(_condition_fixture())


def test_coherent_but_false_recorded_predicate_is_rejected() -> None:
    body = _condition_fixture()
    middle = body["execution_trace"]["steps"][1]
    middle["condition_result"] = True
    middle["pedagogy"]["condition"]["result"] = True
    middle["pedagogy"]["instruction_event"]["condition"] = True
    with pytest.raises(AssertionError, match="wrong C predicate result"):
        _check(body)


def test_native_short_circuit_skips_unreachable_dereference() -> None:
    state = _fixture()["execution_trace"]["steps"][0]["state_snapshot"]
    state["tree_frames"] = [{"parameters": {"n": "NULL"}, "locals": {}}]
    assert _predicate(["if (n != NULL && n->izq != NULL) {"], 0, state, "condition") is False


def test_operand_must_appear_in_native_condition() -> None:
    state = _fixture()["execution_trace"]["steps"][0]["state_snapshot"]
    state["tree_frames"] = [{"parameters": {"n": "NULL"}, "locals": {}}]
    with pytest.raises(AssertionError, match="operand absent"):
        _predicate(["if (n != NULL && n->izq != NULL) {"], 0, state, "operand", "invented")


@pytest.mark.parametrize("list_name", ["objects_before", "objects_after"])
def test_invented_freed_card_is_rejected(list_name: str) -> None:
    body = _fixture()
    body["execution_trace"]["steps"][0]["pedagogy"]["memory"][list_name].append(
        {"id": "N_INVENTADO", "address": "N_INVENTADO", "value": 999,
         "freed": True, "allocated": True})
    with pytest.raises(AssertionError):
        _check(body)


@pytest.mark.parametrize("presentation", ["preserved", "depleted"])
def test_proved_free_keeps_legitimate_historical_card(presentation: str) -> None:
    old = {"A1": {"id": "A1", "capacity": 1, "live": True,
                  "cells": [{"index": 0, "initialized": True, "value": 8}]}}
    history = {}
    _retire_objects(history, old, {})
    version = history["A1"][0 if presentation == "preserved" else 1]
    card = {**deepcopy(version), "address": "A1", "freed": True, "allocated": False}
    _memory_cards([card], {}, history)
    # The same authenticated historical card may persist into the next frame.
    _memory_cards([deepcopy(card)], {}, history)


@pytest.mark.parametrize("corruption", ["unknown_identity", "contents", "duplicate", "allocated"])
def test_historical_card_provenance_content_and_status(corruption: str) -> None:
    old = {"N1": {"id": "N1", "value": 8, "left": "NULL", "right": "NULL", "parent": "NULL", "color": "BLACK"}}
    history = {}
    _retire_objects(history, old, {})
    card = {**old["N1"], "address": "N1", "freed": True, "allocated": False}
    cards = [card]
    if corruption == "unknown_identity":
        card.update(id="N999", address="N999")
    elif corruption == "contents":
        card["value"] = 999
    elif corruption == "duplicate":
        cards.append(deepcopy(card))
    else:
        card["allocated"] = True
    with pytest.raises(AssertionError):
        _memory_cards(cards, {}, history)


@pytest.mark.parametrize("event_list", ["allocated_objects", "freed_objects"])
def test_duplicate_reservation_in_memory_event_is_rejected(event_list: str) -> None:
    record = {"id": "N1", "address": "N1", "value": 8}
    memory = {event_list: [record, deepcopy(record)]}
    with pytest.raises(AssertionError, match="duplicated/invented memory event"):
        _memory_events(memory[event_list], {"N1"}, {"N1": {"id": "N1", "value": 8}})
