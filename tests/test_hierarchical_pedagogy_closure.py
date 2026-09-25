"""Closure acceptance tests for hierarchical pedagogy phases 7-9."""
from pathlib import Path

import pytest

from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.domain.hierarchical.pedagogy import HIERARCHICAL_GUIDED_EXAMPLES, validate_hierarchical_frame


@pytest.mark.parametrize("kind", ["abb-avl", "avl-red-black", "abb-heap"])
def test_comparisons_use_isolated_copies_and_preserve_input(kind):
    values=[10,20,30,40,50]
    result=HierarchicalStructureService.compare_structures(kind,values)
    assert values==[10,20,30,40,50]
    assert result["isolated"] is True
    assert result["left"]["final_state"] is not result["right"]["final_state"]
    assert result["left"]["validation"] and result["right"]["validation"]
    assert result["left"]["size"]==result["right"]["size"]==5


def test_ordered_input_exposes_abb_degeneration_and_avl_balance():
    result=HierarchicalStructureService.compare_structures("abb-avl",[10,20,30,40,50])
    assert result["left"]["height"] > result["right"]["height"]
    assert "rotaciones" in result["conclusion"]


def test_traversal_comparison_has_synchronized_recursive_rules():
    result=HierarchicalStructureService.compare_structures("traversals",[10,5,15])
    assert [item["name"] for item in result["traversals"]]==["inorden","preorden","postorden"]
    assert result["traversals"][0]["values"]==[5,10,15]
    assert all("→" in item["stack_rule"] for item in result["traversals"])


def test_compare_route_validates_inputs(client):
    ok=client.post("/hierarchical/compare",json={"kind":"abb-heap","values":[8,3,10,1]})
    assert ok.status_code==200 and ok.get_json()["isolated"] is True
    assert client.post("/hierarchical/compare",json={"kind":"abb-avl","values":[1,1]}).status_code==400
    assert client.post("/hierarchical/compare",json={"kind":"unknown","values":[1]}).status_code==400


def test_help_accessibility_comparison_and_exports_are_published(client):
    page=client.get("/hierarchical/avl").get_data(as_text=True)
    for element_id in ("hier-compare-kind","hier-compare-values","hier-compare-run","hier-compare-progress","hier-export-image","hier-export-summary","hier-accessible-announcer"):
        assert f'id="{element_id}"' in page
    help_page=client.get("/help/hierarchical/avl").get_data(as_text=True)
    for text in ("Objetivo:","Estrategia:","Invariante:","Memoria C:","Complejidad:","Glosario jerárquico","Black-height","Teclado y accesibilidad"):
        assert text in help_page
    root=Path(__file__).parents[1]
    assert (root/"docs/qa/hierarchical-teacher-guide.md").is_file()
    source=(root/"static/js/hierarchical.js").read_text(encoding="utf-8")
    for marker in ("prefers-reduced-motion: reduce","exportVisualStateAsJpg","hierarchical-learning-summary/v1","ArrowLeft","ArrowRight"):
        assert marker in source


@pytest.mark.parametrize("structure_id", ["abb","avl","red_black","binary_heap"])
def test_fast_and_trace_final_states_are_equivalent(structure_id):
    result=HierarchicalStructureService.execute_operation(structure_id,"insertar",{"value":10},[])
    trace=result["execution_trace"]
    assert trace["final_state"]==result["visual_state"]
    assert trace["steps"][-1]["state_after"]==result["visual_state"]
    assert trace["steps"][-1]["pedagogy"]["invariant"]["holds"]


@pytest.mark.parametrize("structure_id", ["abb","avl","red_black","binary_heap"])
def test_all_guided_cases_publish_valid_frames_at_all_levels(structure_id):
    for example in HIERARCHICAL_GUIDED_EXAMPLES[structure_id]:
        history=[]
        for value in example["seed"]:
            seeded=HierarchicalStructureService.execute_operation(structure_id,"insertar",{"value":value},history)
            assert seeded["success"]
            history=seeded["history"]
        result=HierarchicalStructureService.execute_operation(structure_id,example["operation"],example["payload"],history)
        trace=result["execution_trace"]
        assert trace["steps"], example["id"]
        for step in trace["steps"]:
            frame=step["pedagogy"]
            validate_hierarchical_frame(frame,source_code=trace["source_code"])
            assert set(frame["narration"])=={"basic","intermediate","advanced"}
            assert frame["state_before"]==step["state_snapshot"]
            assert frame["state_after"]==step["state_after"]


@pytest.mark.parametrize("values", [[7,3,9,1,5,8,10],[1,2,3,4,5,6,7],[7,6,5,4,3,2,1]])
def test_structural_properties_hold_for_representative_orders(values):
    for kind in ("abb-avl","avl-red-black","abb-heap"):
        result=HierarchicalStructureService.compare_structures(kind,values)
        assert all(step["validation"] for step in result["left"]["timeline"])
        assert all(step["validation"] for step in result["right"]["timeline"])
