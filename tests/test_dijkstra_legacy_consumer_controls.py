"""Compact pure adversarial controls from the two original Dijkstra HTTP captures."""
from pathlib import Path
import json
import pytest
from _dijkstra_legacy_consumer_oracle import assert_dijkstra_projection
P=Path(__file__).resolve().parents[1]/"openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-dijkstra-legacy-consumers-low/positive-projections.json"
def data(case):return json.loads(P.read_text(encoding="utf-8"))[case]
def row(p,line):return next(r for r in p["rows"] if r["line"]==line)
def variable(memory,name):
    return next(v for f in memory["frames"] if f["function"]=="grafo_dijkstra" for scope in f["scopes"] for k,v in scope["variables"].items() if k==name)
def node(memory,ident):return next(n for n in memory["heap_nodes"] if n["id"]==ident)
@pytest.mark.parametrize("case",("chain","weighted"))
def test_original_focal_projection(case):assert_dijkstra_projection(data(case))
@pytest.mark.parametrize("case",("chain","weighted"))
@pytest.mark.parametrize("defect",("wrong_auxiliary","wrong_parameter","duplicate_heap","wrong_freed_identity","missing_predecessor","early_predecessor","wrong_distance","wrong_minimum","inverted_guard","wrong_source","leaked_buffer","wrong_returned_arc","wrong_path","misplaced_line","cached_table"))
def test_rejects_dijkstra_causal_defect(case,defect):
    p=data(case)
    if defect=="wrong_auxiliary":row(p,"u = j;")["auxiliary"]["kind"]="priority_queue"
    elif defect=="wrong_parameter":row(p,"u = j;")["after"]["frames"][0]["parameters"]["inicio"]=999
    elif defect=="duplicate_heap":r=row(p,"u = j;");r["after"]["heap_nodes"].append(r["after"]["heap_nodes"][0].copy())
    elif defect=="wrong_freed_identity":row(p,"free(dist);")["event"]["value"]="M999"
    elif defect=="missing_predecessor":p["rows"].remove(row(p,"prev[v] = u;"))
    elif defect=="early_predecessor":
        r=row(p,"dist[v] = nueva_dist;");v=variable(r["before"],"v")["value"];u=variable(r["before"],"u")["value"];ident=variable(r["before"],"prev")["value"];node(r["after"],ident)["items"][v]=u
    elif defect=="wrong_distance":r=row(p,"dist[v] = nueva_dist;");v=variable(r["before"],"v")["value"];ident=variable(r["before"],"dist")["value"];node(r["after"],ident)["items"][v]=999
    elif defect=="wrong_minimum":variable(row(p,"min = dist[j];")["after"],"min")["value"]=999
    elif defect=="inverted_guard":r=row(p,"if (nueva_dist < dist[v]) {");r["event"]["value"]=1-r["event"]["value"]
    elif defect=="wrong_source":p["source"]+="\n/* fabricated */"
    elif defect=="leaked_buffer":p["last_memory"]["heap_nodes"].append(dict(id="M999",kind="int",alive=True,borrowed=False,items=[1]))
    elif defect=="wrong_returned_arc":n=next(n for n in p["last_memory"]["heap_nodes"] if n["id"]==p["last_memory"]["returned"]);n["fields"]["costo"]=999
    elif defect=="wrong_path":p["result"]["path"]=[1,3]
    elif defect=="misplaced_line":row(p,"u = j;")["index"]=0
    else:row(p,"dist[v] = nueva_dist;")["table"]["previous"]["3"]=2
    with pytest.raises(AssertionError):assert_dijkstra_projection(p)
