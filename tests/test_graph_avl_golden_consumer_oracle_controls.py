from copy import deepcopy
from pathlib import Path
import json
import pytest
from _graph_avl_golden_consumer_oracle import assert_golden_projection, project_golden
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-avl-golden-consumers-low"
from scripts.published_test_inputs import audit_input_path
HISTORICAL_FIXTURES=json.loads((audit_input_path(P/"original-two-golden-projections.json")).read_text(encoding="utf-8"))
SAVED_BODIES=json.loads((audit_input_path(P/"graph-avl-golden-final-traces.json")).read_text(encoding="utf-8"))
FIXTURES={"graph":HISTORICAL_FIXTURES["graph"],"tree":project_golden(SAVED_BODIES["tests/test_execution_trace_golden.py::test_tree_trace_golden"][-1],"tree")}
@pytest.mark.parametrize("case",list(FIXTURES))
def test_original_golden_projection(case):assert_golden_projection(FIXTURES[case])
@pytest.mark.parametrize("case",list(FIXTURES))
@pytest.mark.parametrize("fault",["source","layoutindex","rowdrop","roworder","coordinatedfinal"])
def test_common_corruption_rejected(case,fault):
    p=deepcopy(FIXTURES[case])
    if fault=="source":p["source"]+="\n// fabricated"
    elif fault=="layoutindex":p["layout"][p["rows"][0]["index"]][0]=0
    elif fault=="rowdrop":p["rows"].pop(0)
    elif fault=="roworder":p["rows"][0],p["rows"][1]=p["rows"][1],p["rows"][0]
    else:
        if case=="tree":p["final"]["size"]=2
        else:p["final"]["metadata"]["edges_count"]=2
        p["trace_final"]=deepcopy(p["final"])
    with pytest.raises(AssertionError):assert_golden_projection(p)
@pytest.mark.parametrize("fault",["malloc","prematureinit","cost","earlypublication","vertex","reverse","leak"])
def test_graph_physical_corruption_rejected(fault):
    p=deepcopy(FIXTURES["graph"]);rows=p["rows"]
    def node(row,ident):return next(n for n in row["after"]["heap_nodes"] if n["id"]==ident)
    if fault=="malloc":rows[0]["event"]["value"]["pointer"]="M99"
    elif fault=="prematureinit":node(rows[0],"M1")["fields"]["costo"]=3
    elif fault=="cost":node(rows[4],"M1")["fields"]["costo"]=99;rows[4]["event"]["value"]=99
    elif fault=="earlypublication":rows[1]["after"]["graph"]["a"]="M1"
    elif fault=="vertex":node(rows[2],"V1")["fields"]["dato"]=99
    elif fault=="reverse":rows[9]["event"]["value"]=1;node(rows[9],"M2")["fields"]["origen"]=1
    else:p["last_memory"]["heap_nodes"].append({"id":"M99","alive":True})
    with pytest.raises(AssertionError):assert_golden_projection(p)
@pytest.mark.parametrize("fault",["factor","head","parent","joinedwrite","reservation","alias","coordinatedfactor"])
def test_avl_physical_corruption_rejected(fault):
    p=deepcopy(FIXTURES["tree"]);rows=p["rows"]
    def node(row,ident):return next(n for n in row["after"]["heap_nodes"] if n["id"]==ident)
    if fault=="factor":node(rows[5],"N1")["balance_factor"]=-1
    elif fault=="head":rows[0]["after"]["head"]="N1"
    elif fault=="parent":node(rows[3],"N1")["parent"]="NULL"
    elif fault=="joinedwrite":node(rows[0],"N1")["left"]="NULL"
    elif fault=="reservation":rows[2]["after"]["heap_nodes"].append({"id":"N99","value":99})
    elif fault=="alias":rows[2]["after"]["tree_frames"][-1]["locals"]["B"]="N1"
    else:p["final"]["root"]["balance_factor"]=1;p["trace_final"]=deepcopy(p["final"])
    with pytest.raises(AssertionError):assert_golden_projection(p)

@pytest.mark.parametrize("case",["graph","tree"])
def test_coordinated_boundary_corruption_rejected(case):
    p=deepcopy(FIXTURES[case]);row=p["rows"][3]
    for state in (row["before"],row["after"]):
        node=next(n for n in state["heap_nodes"] if n["id"]==("V1" if case=="graph" else "N3"))
        if case=="graph":node["fields"]["dato"]=99
        else:node["parent"]="NULL"
    with pytest.raises(AssertionError):assert_golden_projection(p)


@pytest.mark.parametrize("position",[1,FIXTURES["tree"]["rows"][0]["index"]])
@pytest.mark.parametrize("defect",["value","topology","factor","size","height","memory_projection"])
def test_avl_public_projection_corruption_with_next_snapshot_synchronized(position,defect):
    p=deepcopy(FIXTURES["tree"]);frames=p["public_frames"];frame=frames[position];public=frame["after"]
    if defect in {"value","memory_projection"}:
        public["root"]["value"]=999
        if defect=="memory_projection":frame["memory"]["root"]["value"]=999
    elif defect=="topology":public["root"]["left"]=None
    elif defect=="factor":public["root"]["balance_factor"]=999
    else:public[defect]=999
    frames[position+1]["before"]=deepcopy(public)
    with pytest.raises(AssertionError):assert_golden_projection(p)

def test_historical_seven_store_projection_does_not_certify_complete_public_trace():
    with pytest.raises(AssertionError):assert_golden_projection(HISTORICAL_FIXTURES["tree"])
