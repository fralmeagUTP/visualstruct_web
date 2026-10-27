"""Only original triangle delete3 and Kruskal two consumer IDs."""
from copy import deepcopy
import hashlib,re
from _final_graph_oracle import assert_final_graph,_memory,_locals,_C_PHASES,_NON_C_PHASES
from _final_graph_oracle import _stored_value as _original_stored_value
SHAS={"remove_vertex":"4d8cfbf4231b1fcfcd95f1c2063c90cdc0a3aeb642700a98220450ab0e08abe1","run_kruskal":"9edc353fa4d52febb1217573bec48b1e5cc2d407a5fd76261c6d8739aa01b1c7"}
def _heap(m):
    d={n["id"]:n for n in m["heap_nodes"]};assert len(d)==len(m["heap_nodes"]);return d
def _reference(m,address):
    assert type(address) is str and address.startswith("&")
    f,s,v=address[1:].split(":")
    cells=[scope["variables"][v]["value"] for frame in m["frames"] if frame["id"]==f for scope in frame["scopes"] if scope["id"]==f+":"+s]
    assert len(cells)==1;return cells[0]
def _array_target(m,function,name):
    match=re.fullmatch(r"([A-Za-z_]\w*(?:(?:->|\.)[A-Za-z_]\w*)?)\[([A-Za-z_]\w*|[0-9]+)(?:\+([0-9]+))?(\+\+)?\]",name)
    assert match,"unsupported bounded array target"
    base,index,offset,increment=match.groups();env=_locals(m,function)
    i=int(index) if index.isdigit() else env[index]
    assert type(i) is int;i+=int(offset or 0);i-=int(bool(increment))
    if "->" in base:
        variable,field=base.split("->");address=_reference(m,env[variable])[field]
    elif "." in base:
        variable,field=base.split(".");address=env[variable][field]
    else:address=env[base]
    node=_heap(m)[address];assert node["borrowed"] is False and 0<=i<len(node["items"])
    return address,i,env
def _stored_value(before,after,event):
    if "[" not in event["name"]:return _original_stored_value(before,after,event)
    address,index,env=_array_target(after,event["function"],event["name"])
    return _heap(after)[address]["items"][index]
def assert_observed_graph_frame(step, trace, index):
    frame = step["pedagogy"]; invariant = frame["invariant"]
    assert frame["state_before"] == step["state_snapshot"] and frame["state_after"] == step["state_after"]
    if invariant["holds"] is True:
        assert_final_graph(frame["state_after"]); return
    assert invariant["holds"] is None, "Explicit invariant failure"
    assert invariant["symbol"] == "?" and invariant["evidence"]
    active = [m for m in ("numeric", "construction", "vertex", "bfs", "dfs") if trace.get(m + "_instruction_model") is True]
    assert len(active) == 1, "Missing or ambiguous observer"
    model = active[0]; event = frame["instruction_event"]; phase = event["phase"]
    assert phase in _C_PHASES | _NON_C_PHASES, "Invented instruction phase"
    assert step["debug"]["stage"] == phase, "Event detached from observed step"
    before, after = frame["instruction_state_before"], frame["instruction_state_after"]
    old, retired_old = _memory(before, model); new, retired_new = _memory(after, model)
    assert frame["memory_state"] == after
    debug_key = {"numeric": "graph_memory", "vertex": "vertex_memory", "bfs": "bfs_memory", "dfs": "dfs_memory"}.get(model)
    if debug_key: assert step["debug"][debug_key] == after, "Detached observer memory"
    lines = trace["source_code"].splitlines()
    assert type(step["line_index"]) is int and 0 <= step["line_index"] < len(lines)
    assert step["line_text"] == lines[step["line_index"]]
    if phase in _NON_C_PHASES:
        assert index == len(trace["steps"]) - 1
        assert event.get("C_executed") is False or (model in {"bfs", "dfs"} and phase == "caller")
        assert old == new and retired_old == retired_new and before["graph"] == after["graph"]
        return
    # Legacy BFS/DFS omit the flag; an explicit denial or invalid value is never a C event.
    assert event.get("C_executed") is True or (model in {"bfs", "dfs"} and "C_executed" not in event)
    assert type(event["function"]) is str and event["function"]
    if "statement" in event: assert event["statement"] == step["line_text"]
    if "line_index" in event: assert event["line_index"] == step["line_index"]
    if "pos" in event:
        pos = event["pos"]; assert type(pos) is int and 0 <= pos < len(trace["source_code"])
        assert trace["source_code"].count("\n", 0, pos) == step["line_index"]
    memories = (before,) if phase in {"return", "scope_exit"} else (after,)
    assert any(any(f["function"] == event["function"] for f in m["frames"]) for m in memories)
    if model not in {"bfs", "dfs"}:
        c_steps = [s for s in trace["steps"] if s["pedagogy"]["instruction_event"].get("C_executed") is True]
        ledger = trace["C_instruction_events"]; assert len(c_steps) == len(ledger)
        ordinal = sum(s["pedagogy"]["instruction_event"].get("C_executed") is True for s in trace["steps"][:index])
        record = ledger[ordinal]; assert {"function", "phase", "line_index"} <= record.keys()
        assert all(event.get(k) == v for k, v in record.items()), "Detached C ledger event"
    if phase in {"condition", "operand"}: assert before == after, "Condition mutated memory"
    if phase == "enter":
        ids = lambda memory: {f.get("id", f.get("frame_id")) for f in memory["frames"]}
        assert len(ids(after) - ids(before)) == 1
    if phase == "allocate":
        assert len(new - old) == 1 and not old - new and retired_new == retired_old
        if model != "vertex": assert after["allocations"] == before["allocations"] + 1
    if phase == "free":
        assert len(old - new) == 1 and not new - old and retired_new - retired_old == old - new
        if model != "vertex": assert after["frees"] == before["frees"] + 1
    if phase == "write" and model in {"numeric", "construction"}:
        if "++" in event["name"]:
            import re
            variable = re.fullmatch(r"[A-Za-z_]\w*\[([A-Za-z_]\w*)\+\+\]", event["name"])[1]
            assert index > 0
            previous = trace["steps"][index - 1]["pedagogy"]
            prior_event = previous["instruction_event"]
            assert prior_event["phase"] == "write" and prior_event["name"] == variable
            assert prior_event["function"] == event["function"] and prior_event["line_index"] == event["line_index"]
            old_index = _locals(previous["instruction_state_before"], event["function"])[variable]
            assert prior_event["value"] == old_index + 1 == _locals(before, event["function"])[variable]
        assert _stored_value(before, after, event) == event["value"], "Written value detached from C storage"

def project_graphdk(body,operation):
    assert operation in SHAS;trace=body["execution_trace"];source=trace["source_code"];assert hashlib.sha256(source.encode()).hexdigest()==SHAS[operation]
    lines=source.splitlines();rows=[];layout=[]
    for i,s in enumerate(trace["steps"]):
        p=s["pedagogy"];e=p["instruction_event"]
        assert type(s["line_index"]) is int and lines[s["line_index"]]==s["line_text"]
        assert p["source"]["line_index"]==s["line_index"] and p["source"]["line_text"]==s["line_text"]
        layout.append([s["line_index"],s["line_text"],e.get("function"),e["phase"]])
        if operation=="remove_vertex" or e["phase"]=="free" or (e["phase"]=="write" and "[" in e.get("name","")):
            rows.append(dict(index=i,line=s["line_text"],event=e,before=p["instruction_state_before"],after=p["instruction_state_after"]))
    return dict(operation=operation,source=source,layout=layout,rows=rows,final=body["visual_state"],result=body.get("result"),last_memory=trace["steps"][-1]["pedagogy"]["memory_state"])
def assert_graphdk_projection(p):
    operation=p["operation"];assert operation in SHAS
    assert hashlib.sha256(p["source"].encode()).hexdigest()==SHAS[operation]
    lines=p["source"].splitlines();assert len(p["layout"])==(47 if operation=="remove_vertex" else 1166)
    for index,line,function,phase in p["layout"]:assert type(index) is int and lines[index]==line
    assert_final_graph(p["final"])
    if operation=="remove_vertex":
        assert len(p["rows"])==47
        expected={**{"V"+str(i):{"id":"V"+str(i),"kind":"struct NodoV","fields":{"dato":i,"marcado":0,"sig":"NULL" if i==1 else "V"+str(i-1)}} for i in (1,2,3)},**{"E"+str(i):{"id":"E"+str(i),"kind":"struct NodoA","fields":{"origen":u,"destino":v,"costo":w,"sig":"NULL" if i==1 else "E"+str(i-1)}} for i,(u,v,w) in enumerate([(1,2,1),(2,1,1),(2,3,2),(3,2,2),(1,3,5),(3,1,5)],1)}}
        graph={"v":"V3","a":"E6"};retired=[];frees={5:"V3",14:"E6",20:"E5",26:"E4",32:"E3"};links={4:("v","V2"),13:("a","E5"),19:("a","E4"),25:("a","E3"),31:("a","E2")};conditions={2:True,3:True,10:True,12:True,16:True,18:True,22:True,24:True,28:True,30:True,34:True,36:False,39:True,41:False,44:False}
        for i,r in enumerate(p["rows"]):
            assert r["index"]==i;old=r["before"];new=r["after"];e=r["event"]
            assert _heap(old)==expected and old["graph"]==graph and old["retired_objects"]==retired
            assert p["layout"][i][1]==r["line"] and p["layout"][i][3]==e["phase"]
            if i in links:field,value=links[i];graph[field]=value;assert e["phase"]=="assignment"
            if i in frees:
                ident=frees[i];assert e["phase"]=="free";del expected[ident];retired.append(ident)
            if i in conditions:assert e["phase"]=="condition" and e["value"] is conditions[i]
            assert _heap(new)==expected and new["graph"]==graph and new["retired_objects"]==retired
        final=p["final"];assert {n["id"] for n in final["nodes"]}=={"1","2"}
        assert [(e["source"],e["target"],e["weight"]) for e in final["edges"]]==[("1","2",1)]
    else:
        frees=[];writes=[];tracked={"M1":["sin inicializar"]*3,"M2":["sin inicializar"]*3,"M3":["sin inicializar"]*6};borrowed=None
        for r in p["rows"]:
            old=r["before"];new=r["after"];e=r["event"];a=_heap(old);expected={k:deepcopy(node) for k,node in a.items()}
            current_borrowed={k:n for k,n in a.items() if n["borrowed"]}
            if borrowed is None:borrowed=deepcopy(current_borrowed);assert len(borrowed)==9
            assert current_borrowed==borrowed
            for identity,items in tracked.items():assert a[identity]["items"]==items,"unexplained array change between focal stores"
            assert p["layout"][r["index"]][1]==r["line"] and p["layout"][r["index"]][3]==e["phase"]
            if e["phase"]=="free":
                identity=e["value"];assert identity in a and a[identity]["borrowed"] is False
                del expected[identity];del tracked[identity];frees.append(identity)
                assert new["retired_objects"]==old["retired_objects"]+[{**a[identity],"alive":False,"historical_identity_only":True}]
            else:
                name=e["name"];address,index,env=_array_target(old,e["function"],name);items=a[address]["items"]
                if name=="conjuntos.padre[i]":value=env["i"]
                elif name=="vertices[i++]":value=a[env["v"]]["fields"]["dato"]
                elif name=="aristas[i++]":value=env["a"]
                elif name=="aristas[y]":value=items[index+1]
                elif name=="aristas[y+1]":value=env["tmp"]
                elif name=="c->padre[ry]":value=env["rx"]
                elif name=="c->padre[x]":
                    value=items[index];seen=set()
                    while items[value]!=value:
                        assert value not in seen;seen.add(value);value=items[value]
                else:raise AssertionError("unexpected focal target")
                assert e["value"]==value;expected[address]["items"][index]=value;tracked[address][index]=value
                writes.append(name)
            assert _heap(new)==expected,("unexplained focal array mutation/free",r["index"],e.get("name"),[(k,expected.get(k),_heap(new).get(k)) for k in expected.keys()|_heap(new).keys() if expected.get(k)!=_heap(new).get(k)])
        assert frees==["M3","M1","M2"]
        assert writes.count("conjuntos.padre[i]")==3 and writes.count("aristas[i++]")==6 and writes.count("vertices[i++]")==3
        result=p["result"];assert result["mst_edges"]==[[3,2,2],[2,1,1]] and result["total_weight"]==3 and result["connected"] is True and result["components_count"]==1
        live=_heap(p["last_memory"]);owned={k:n for k,n in live.items() if not n["borrowed"]}
        assert set(owned)=={"M4","M5"} and owned["M5"]["fields"]=={"origen":3,"destino":2,"costo":2,"sig":"M4"}
        assert owned["M4"]["fields"]=={"origen":2,"destino":1,"costo":1,"sig":"NULL"}
def assert_graphdk_consumer(body,operation):
    project=project_graphdk(body,operation)
    if operation=="run_kruskal":
        trace=body["execution_trace"]
        for i,s in enumerate(trace["steps"]):assert_observed_graph_frame(s,trace,i)
    assert_graphdk_projection(project)
