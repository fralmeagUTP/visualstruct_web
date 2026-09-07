"""Contract tests for hierarchical pedagogy phases 1-3."""
from __future__ import annotations
import json
from pathlib import Path

from app.domain.hierarchical.pedagogy import (
    HIERARCHICAL_FRAME_SCHEMA_VERSION, HIERARCHICAL_GUIDED_EXAMPLES,
    HIERARCHICAL_LEARNING_CATALOG, HIERARCHICAL_STRUCTURES,
    build_hierarchical_frame, hierarchical_frame_schema, validate_hierarchical_frame,
)

def _step(line: str, debug=None) -> dict:
    state={"kind":"binary_tree","root":{"value":10,"left":None,"right":None},"size":1,"validation":True}
    return {"line_index":0,"line_text":line,"state_snapshot":state,"state_after":state,"debug":debug or {}}

def test_catalog_schema_and_examples_cover_all_structures() -> None:
    assert set(HIERARCHICAL_LEARNING_CATALOG)==HIERARCHICAL_STRUCTURES
    assert set(HIERARCHICAL_GUIDED_EXAMPLES)==HIERARCHICAL_STRUCTURES
    assert hierarchical_frame_schema()["version"]==HIERARCHICAL_FRAME_SCHEMA_VERSION
    assert hierarchical_frame_schema()["levels"]==["basic","intermediate","advanced"]
    ids={item["id"] for examples in HIERARCHICAL_GUIDED_EXAMPLES.values() for item in examples}
    assert {"delete-leaf","delete-one","delete-two","ll","rr","lr","rl","red-uncle","black-uncle-simple","black-uncle-double","rise","descent","tie"}<=ids

def test_golden_hierarchical_concepts() -> None:
    fixtures=json.loads((Path(__file__).parent/"golden"/"hierarchical_pedagogical_frames_v1.json").read_text(encoding="utf-8"))["fixtures"]
    expected={"comparison":"compare","descent":"descend","return":"return","assignment":"assignment","allocation":"allocation","link":"link","rotation":"rotation","recolor":"recolor","swap":"swap","free":"free"}
    for name,line in fixtures.items():
        debug={"rotation_hint":{"type":"LL"}} if name=="rotation" else {}
        frame=build_hierarchical_frame(structure_id="avl",operation_name="insertar",payload={"value":10},step=_step(line,debug),source_lines=[line],success=True)
        validate_hierarchical_frame(frame,source_code=line)
        assert frame["concept"]==expected[name]

def test_real_traces_expose_canonical_three_level_frames(client) -> None:
    for structure_id in sorted(HIERARCHICAL_STRUCTURES):
        response=client.post(f"/hierarchical/{structure_id}/operate",json={"operation":"insertar","payload":{"value":10}})
        assert response.status_code==200
        trace=response.get_json()["execution_trace"]
        assert trace["pedagogy_schema_version"]==HIERARCHICAL_FRAME_SCHEMA_VERSION
        for step in trace["steps"]:
            frame=step["pedagogy"]; validate_hierarchical_frame(frame,source_code=trace["source_code"])
            assert frame["state_before"]==step["state_snapshot"]
            assert frame["state_after"]==step["state_after"]
            assert set(frame["narration"])=={"basic","intermediate","advanced"}

def test_hierarchical_page_exposes_learning_regions(client) -> None:
    html=client.get("/hierarchical/avl").get_data(as_text=True)
    for label in ("Preparar","Predecir","Ejecutar y visualizar","Comprender","Relacionar con C","Comparar","Reflexionar"):
        assert label in html
    for element_id in ("hier-learning-level","hier-guided-example","hier-load-example","hier-visual-region","hier-code-region","hier-function-list","hier-hide-comments","hier-restart-execution","hier-pedagogy-summary"):
        assert f'id="{element_id}"' in html

def test_active_frontend_no_longer_calls_visual_inference_helpers() -> None:
    source=(Path(__file__).parents[1]/"static/js/hierarchical.js").read_text(encoding="utf-8")
    assert source.count("rbDidacticDelta(")==1
    assert "traceRotationHint || rotationHint" not in source
    assert "buildHeapOperationFrames(\n        current.name" not in source
