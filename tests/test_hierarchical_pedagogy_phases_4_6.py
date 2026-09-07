"""Acceptance tests for hierarchical pedagogy phases 4 through 6."""
from pathlib import Path

from app.domain.hierarchical.pedagogy import build_hierarchical_frame, validate_hierarchical_frame


def _frame(structure: str, before: dict, after: dict, line: str, debug: dict | None = None):
    step={"line_index":0,"line_text":line,"state_snapshot":before,"state_after":after,"debug":debug or {},"condition_result":True}
    return build_hierarchical_frame(structure_id=structure,operation_name="insertar",payload={"value":5},step=step,source_lines=[line],success=True)


def test_c_memory_stack_and_reversible_states_are_canonical():
    before={"root":None,"size":0,"validation":True}
    after={"root":{"value":5,"left":None,"right":None},"size":1,"validation":True}
    frame=_frame("abb",before,after,"nodo = malloc(sizeof(struct Nodo));",{"path_keys":["5"],"path_index":0})
    validate_hierarchical_frame(frame,source_code="nodo = malloc(sizeof(struct Nodo));")
    assert frame["state_before"]==before and frame["state_after"]==after
    assert frame["memory"]["allocated_objects"][0]["address"]=="0xNODE-5"
    assert frame["memory"]["dangling_references"]==[]
    assert frame["call_stack"][0]["local_root_address"]=="0xNODE-5"
    assert all({"type","meaning","previous","value","changed"} <= set(item) for item in frame["variables"])


def test_each_structure_publishes_specific_invariant_evidence():
    tree={"root":{"value":5,"left":None,"right":None,"height":1,"balance_factor":0,"color":"negro"},"size":1,"validation":True}
    for structure in ("abb","avl","red_black"):
        frame=_frame(structure,tree,tree,"return nodo;",{"path_keys":["5"],"path_index":0})
        assert frame["invariant"]["evidence_by_node_or_path"]
        assert frame["structural_focus"]["red_black_roles"]["node"]=="5"
    heap={"array":[1,3,2],"size":3,"validation":True}
    frame=_frame("binary_heap",heap,heap,"if (A[i] < A[padre])",{"active_index":1,"parent_index":0,"child_indices":[]})
    assert "no es un ABB" in frame["invariant"]["explanation"]
    assert frame["array"]["index_relations"]["left"]=="2 * i + 1"


def test_double_rotation_has_two_explicit_simple_steps():
    state={"root":{"value":20,"left":None,"right":None},"size":1,"validation":True}
    frame=_frame("avl",state,state,"nodo->izq = rotar_izquierda(nodo->izq);",{"rotation_hint":{"type":"LR"}})
    assert frame["adjustment"]["simple_step"]=="rotación izquierda"
    assert len(frame["adjustment"]["sequence"])==2


def test_page_and_frontend_expose_complete_learning_controls(client):
    html=client.get("/hierarchical/avl").get_data(as_text=True)
    ids=("hier-prepare","hier-sim-play","hier-sim-pause","hier-sim-home","hier-sim-prev","hier-sim-step","hier-sim-end","hier-sim-repeat","hier-progress","hier-prediction","hier-hint","hier-skip-prediction","hier-practice-mode","hier-reset-progress","hier-variables-view","hier-memory-view","hier-relations-view")
    assert all(f'id="{element_id}"' in html for element_id in ids)
    source=(Path(__file__).parents[1]/"static/js/hierarchical.js").read_text(encoding="utf-8")
    assert "tracePlayer?.pause()" in source
    assert "tracePlayer?.seek(-1)" in source
    assert "sessionStorage.setItem(conceptualProgressKey" in source
    assert "practiceCover.hidden" in source
