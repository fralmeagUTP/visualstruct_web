"""Pure controls of the original weighted4 BFS/DFS captures; no service calls."""
from pathlib import Path
from copy import deepcopy
import json,pytest
from _bfs_dfs_auxiliary_consumer_oracle import assert_saved_traversal
ROOT=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-bellman-traversal-consumers-low"
from scripts.published_test_inputs import audit_input_path
@pytest.fixture(scope="module",params=["run_bfs","run_dfs"])
def saved(request):return json.loads((audit_input_path(ROOT/("graphbt-compact-before-traversal-"+request.param+"-service-1.json"))).read_text(encoding="utf-8"))
def test_original_capture_positive(saved):assert_saved_traversal(saved)
@pytest.mark.parametrize("mutation",["auxiliary_kind","auxiliary_items","tree","discovery","output","physical_store","free","allocation","result","source"])
def test_causal_mutations_rejected(saved,mutation):
    p=deepcopy(saved)
    if mutation=="auxiliary_kind":p["rows"][-1]["auxiliary"]["kind"]="recursive_stack"
    elif mutation=="auxiliary_items":p["rows"][-1]["auxiliary"]["items"].append("999")
    elif mutation=="tree":p["rows"][-1]["traversal"]["tree_edges"].append(["1","4"])
    elif mutation=="discovery":p["rows"][-1]["traversal"]["discovery_order"].append("1")
    elif mutation=="output":p["rows"][-1]["traversal"]["output_order"]=["1","3","2"]
    elif mutation=="physical_store":
        row=next(r for r in p["rows"] if r["line"].strip()=="tmp->dato = actual;")
        node=next(n for n in row["after"]["heap_nodes"] if n["kind"]=="result");node["value"]=999
    elif mutation=="free":next(r for r in p["rows"] if r["event"]["phase"]=="free")["after"]["freed_nodes"]=[]
    elif mutation=="allocation":next(r for r in p["rows"] if r["event"]["phase"]=="allocate")["after"]["allocations"]+=1
    elif mutation=="result":p["result"]=[1,3,2]
    elif mutation=="source":p["source"]+="\n"
    with pytest.raises(AssertionError):assert_saved_traversal(p)
@pytest.mark.parametrize("mutation",["recursive_parameter","recursive_return","dead_head_storage"])
def test_dfs_causal_stack_mutations_rejected(mutation):
    p=json.loads((audit_input_path(ROOT/"graphbt-compact-before-traversal-run_dfs-service-1.json")).read_text(encoding="utf-8"))
    if mutation=="recursive_parameter":
        r=next(r for r in p["rows"] if r["event"]["phase"]=="enter" and r["event"]["function"]=="grafo_dfs_recursivo");r["after"]["recursive_frames"][-1]["parameters"]["actual"]=999
    elif mutation=="recursive_return":
        r=next(r for r in p["rows"] if r["event"]["phase"]=="return" and r["event"]["function"]=="grafo_dfs_recursivo");r["after"]["recursive_frames"]=[*r["before"]["recursive_frames"]]
    else:p["rows"][-1]["memory"]["head_storage"]["live"]=True
    with pytest.raises(AssertionError):assert_saved_traversal(p)
