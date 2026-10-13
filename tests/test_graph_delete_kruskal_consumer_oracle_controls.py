from pathlib import Path
from copy import deepcopy
import json
import pytest
from _graph_delete_kruskal_consumer_oracle import assert_graphdk_projection
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-graph-delete-kruskal-consumers-low"
FIXTURES=json.loads((P/"original-two-graphdk-projections.json").read_text(encoding="utf-8"))
@pytest.mark.parametrize("operation",list(FIXTURES))
def test_original_projection(operation):assert_graphdk_projection(FIXTURES[operation])
def test_interned_immutable_arrays_are_distinct_physical_reservations():
    p=deepcopy(FIXTURES["run_kruskal"]);row=p["rows"][0]
    nodes={n["id"]:n for n in row["before"]["heap_nodes"]}
    assert nodes["M1"]["items"]==nodes["M2"]["items"]
    nodes["M2"]["items"]=nodes["M1"]["items"]
    assert_graphdk_projection(p)
@pytest.mark.parametrize("fault",["source","index","resurrect","earlyfree","coordinatedvertex","condition","head","duplicateRetired","finalnodes","finaledge"])
def test_delete_corruption_rejected(fault):
    p=deepcopy(FIXTURES["remove_vertex"]);rows=p["rows"]
    if fault=="source":p["source"]+="\n// fabricated"
    elif fault=="index":p["layout"][5][0]=0
    elif fault=="resurrect":rows[5]["after"]["heap_nodes"].append(next(n for n in rows[5]["before"]["heap_nodes"] if n["id"]=="V3"))
    elif fault=="earlyfree":rows[4]["after"]["heap_nodes"]=[n for n in rows[4]["after"]["heap_nodes"] if n["id"]!="V3"]
    elif fault=="coordinatedvertex":
        for m in (rows[6]["before"],rows[6]["after"]):next(n for n in m["heap_nodes"] if n["id"]=="V1")["fields"]["dato"]=99
    elif fault=="condition":rows[12]["event"]["value"]=False
    elif fault=="head":rows[4]["after"]["graph"]["v"]="V1"
    elif fault=="duplicateRetired":rows[14]["after"]["retired_objects"].append("V3")
    elif fault=="finalnodes":p["final"]["nodes"][0]["id"]="99"
    else:p["final"]["edges"][0]["weight"]=99
    with pytest.raises(AssertionError):assert_graphdk_projection(p)
@pytest.mark.parametrize("fault",["source","index","coordinatedstore","postfix","offset","stackreference","coordinatedarray","borrowed","freeidentity","retired","mstvalue","leak"])
def test_kruskal_corruption_rejected(fault):
    p=deepcopy(FIXTURES["run_kruskal"]);rows=p["rows"]
    def locals_for(row,function):
        frames=[f for f in row["before"]["frames"] if f["function"]==function]
        return frames[-1]["scopes"]
    def setlocal(row,function,name,value):
        for s in locals_for(row,function):
            if name in s["variables"]:s["variables"][name]["value"]=value;return
        raise AssertionError("control target missing")
    if fault=="source":p["source"]+="\n// fabricated"
    elif fault=="index":p["layout"][rows[0]["index"]][0]=0
    elif fault=="coordinatedstore":
        row=next(r for r in rows if r["event"].get("name")=="conjuntos.padre[i]");row["event"]["value"]=99
        next(n for n in row["after"]["heap_nodes"] if n["id"]=="M1")["items"][0]=99
    elif fault=="postfix":setlocal(rows[0],"inicializarVectorVertices","i",0)
    elif fault=="offset":
        row=next(r for r in rows if r["event"].get("name")=="aristas[y+1]");row["event"]["name"]="aristas[y+2]"
    elif fault=="stackreference":
        row=next(r for r in rows if r["event"].get("name")=="c->padre[ry]")
        next(f for f in row["before"]["frames"] if f["function"]=="grafo_unir_conjuntos")["parameters"]["c"]="&Fmissing:B834:conjuntos"
    elif fault=="coordinatedarray":
        row=next(r for r in rows if r["event"].get("name")=="aristas[y]")
        for m in (row["before"],row["after"]):next(n for n in m["heap_nodes"] if n["id"]=="M1")["items"][0]=99
    elif fault=="borrowed":
        for m in (rows[5]["before"],rows[5]["after"]):next(n for n in m["heap_nodes"] if n["id"]=="V1")["fields"]["dato"]=99
    elif fault=="freeidentity":next(r for r in rows if r["event"]["phase"]=="free")["event"]["value"]="V1"
    elif fault=="retired":next(r for r in rows if r["event"]["phase"]=="free")["after"]["retired_objects"]=[]
    elif fault=="mstvalue":next(n for n in p["last_memory"]["heap_nodes"] if n["id"]=="M4")["fields"]["costo"]=99
    else:p["last_memory"]["heap_nodes"].append({"id":"M99","borrowed":False})
    with pytest.raises(AssertionError):assert_graphdk_projection(p)
