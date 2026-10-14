"""Pure mutation controls of frozen original Bellman7 capture; no app calls."""
from pathlib import Path
from copy import deepcopy
import json,pytest
from _bellman_reachability_consumer_oracle import assert_saved_bellman
CAP=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-bellman-traversal-consumers-low/graphbt-compact-before-bellman-run_bellman_ford-service-1.json"
from scripts.published_test_inputs import audit_input_path
@pytest.fixture(scope="module")
def saved():return json.loads(audit_input_path(CAP).read_text(encoding="utf-8"))
def test_original_capture_positive(saved):assert_saved_bellman(saved)
@pytest.mark.parametrize("mutation",["guard_value","guard_name","reachability","distance_write","path","source","free","success"])
def test_causal_mutations_rejected(saved,mutation):
    p=deepcopy(saved)
    guards=[r for r in p["rows"] if r["event"].get("name")=="u != -1 && v != -1 && alcanzable[u]"]
    r=next(r for r in guards if r["event"]["value"]==1)
    if mutation=="guard_value":r["event"]["value"]=0
    elif mutation=="guard_name":r["event"]["name"]="u != -1 && v != -1 && dist[u] != INT_MAX"
    elif mutation=="reachability":
        from _bellman_reachability_consumer_oracle import env,heap
        v=env(r["before"],"grafo_bellman_ford");heap(r["before"])[v["alcanzable"]]["items"][v["u"]]=0
    elif mutation=="distance_write":next(r for r in p["rows"] if r["event"].get("name")=="dist[v]")["event"]["value"]+=1
    elif mutation=="path":p["result"]["path"]=[1,4]
    elif mutation=="source":p["source"]+="\n"
    elif mutation=="free":next(r for r in p["rows"] if r["event"]["phase"]=="free")["event"]["value"]="V1"
    elif mutation=="success":p["success"]=False
    with pytest.raises(AssertionError):assert_saved_bellman(p)

def test_service_integer_keys_positive(saved):
    p=deepcopy(saved)
    for field in ("distances","previous"):p["result"][field]={int(k):v for k,v in p["result"][field].items()}
    assert_saved_bellman(p)
