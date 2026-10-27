from copy import deepcopy
from pathlib import Path
import json
import pytest
from _bellman_http_consumer_oracle import assert_bellman_projection
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-bellman-http-consumers-low"
from scripts.published_test_inputs import audit_input_path
FIXTURES=json.loads((audit_input_path(P/"original-three-query-projections.json")).read_text(encoding="utf-8"))
@pytest.mark.parametrize("case",list(FIXTURES))
def test_original_projection(case):assert_bellman_projection(FIXTURES[case])
@pytest.mark.parametrize("case",list(FIXTURES))
@pytest.mark.parametrize("fault",["status","success","source","sourceindex","condition","cleanuporder","freeidentity","resurrect","retired","ownedend","result","branch"])
def test_corrupt_original_projection_rejected(case,fault):
    p=deepcopy(FIXTURES[case]);rows=p["rows"]
    frees=[r for r in rows if r["event"]["phase"]=="free"]
    if fault=="status":p["status"]=200 if p["status"]==400 else 400
    elif fault=="success":p["success"]=not p["success"]
    elif fault=="source":p["source"]+="\n// fabricated"
    elif fault=="sourceindex":p["layout"][rows[0]["index"]][0]=0
    elif fault=="condition":
        row=next(r for r in rows if r["event"]["phase"]=="condition");row["event"]["value"]=1-row["event"]["value"]
    elif fault=="cleanuporder":
        a=rows.index(frees[0]);b=rows.index(frees[1]);rows[a],rows[b]=rows[b],rows[a]
    elif fault=="freeidentity":frees[0]["event"]["value"]="borrowed-object"
    elif fault=="resurrect":
        r=frees[0];ident=r["event"]["value"];r["after"]["heap_nodes"].append(next(n for n in r["before"]["heap_nodes"] if n["id"]==ident))
    elif fault=="retired":frees[0]["after"]["retired_objects"]=[]
    elif fault=="ownedend":p["last_memory"]["heap_nodes"][0]["borrowed"]=False
    elif fault=="result":p["result"]["has_negative_cycle"]=not p["result"]["has_negative_cycle"]
    else:
        phase="stdout" if case!="unreachable4" else "condition"
        if phase=="stdout":p["rows"]=[r for r in rows if r["event"]["phase"]!=phase]
        else:p["rows"]=[r for r in rows if r["event"].get("name")!="!alcanzable[idx_llegada]"]
    with pytest.raises(AssertionError):assert_bellman_projection(p)
