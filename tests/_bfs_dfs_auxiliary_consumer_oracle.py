"""Focal original weighted4 BFS/DFS physical C auxiliary/tree oracle."""
from copy import deepcopy
import hashlib,re
SHAS={"run_bfs":"f2cbcf9014d5db332c4a72ae528cbb700e22cde520a298c372f6f8d6d29cd171","run_dfs":"9230a427009bb3f83e07b036d5adb42f257ed4686ad41f1fc82fa4fd1b505206"}
def heap(memory):
    result={n["id"]:n for n in memory["heap_nodes"]}
    assert len(result)==len(memory["heap_nodes"]);return result
def env(memory,function):
    frames=[f for f in memory["frames"] if f["function"]==function];assert frames
    f=frames[-1];values=dict(f["parameters"])
    if "locals" in f:values.update(f["locals"])
    for s in f.get("scopes",[]):values.update({k:v["value"] for k,v in s["variables"].items()})
    return values
def chain(memory,head):
    nodes=heap(memory);result=[];seen=set()
    while head!="NULL":
        assert head in nodes and head not in seen;seen.add(head);node=nodes[head];result.append(node);head=node["next"]
    return result
FIELDS={"dato":"value","nro":"value","marcado":"mark","sig":"next","sgte":"next","destino":"target"}
STORES={"aux->nro = valor;","aux->sgte = NULL;","q->atras->sgte = aux;","ultimo->sig = tmp;","tmp->dato = actual;","tmp->marcado = 0;","tmp->sig = NULL;","k->marcado = 1;","k->marcado = 0;","nuevo->dato = k->destino;","nuevo->marcado = 0;","nuevo->sig = ver;","nuevo->sig = NULL;","ultimo->sig = nuevo;"}
def expression(text,memory,values):
    if text=="NULL":return "NULL"
    if re.fullmatch(r"-?[0-9]+",text):return int(text)
    if text=="q->atras":return memory["queue"]["atras"]
    if "->" in text:
        root,field=text.split("->");return heap(memory)[values[root]][FIELDS[field]]
    return values[text]
def assert_traversal_projection(p):
    bfs=p["operation"]=="run_bfs";assert len(p["layout"])==(412 if bfs else 359) and len(p["rows"])==len(p["layout"])
    tracked=heap(p["rows"][0]["before"]);freed=[];discovery=[];parents={};entered=[];returned=[]
    assert {n["value"] for n in tracked.values() if n["kind"]=="vertex"}=={1,2,3,4}
    for row in p["rows"]:
        old=row["before"];new=row["after"];e=row["event"];phase=e["phase"];function=e["function"];line=row["line"].split("//",1)[0].strip()
        if line.startswith("else "):line=line[5:]
        a=heap(old);actual=heap(new);assert a==tracked;expected={k:deepcopy(n) for k,n in a.items()};queue=dict(old["queue"])
        if phase=="allocate":
            added=actual.keys()-a.keys();assert len(added)==1;identity=next(iter(added))
            kind="queue" if function=="cola_encolar" else "result" if function in {"grafo_bfs","grafo_dfs_recursivo"} else "successor"
            variable="aux" if kind=="queue" else "tmp" if kind=="result" else "nuevo"
            assert env(new,function)[variable]==identity
            node={"id":identity,"kind":kind,"value":"sin inicializar","next":"sin inicializar"}
            if kind!="queue":node["mark"]="sin inicializar"
            expected[identity]=node
        elif phase=="free":
            values=env(old,function);identity=values["aux" if function=="cola_desencolar" else "temp"]
            assert identity in a and a[identity]["kind"] in {"queue","successor"};del expected[identity];freed.append({**a[identity],"usable":False})
        elif phase=="statement":
            values=env(old,function)
            if line in STORES:
                lhs,rhs=line.rstrip(";").split(" = ");value=expression(rhs,old,values)
                if lhs=="q->atras->sgte":identity=old["queue"]["atras"];field="next"
                else:root,cfield=lhs.split("->");identity=values[root];field=FIELDS[cfield]
                expected[identity][field]=value
            elif line in {"q->delante = aux;","q->atras = aux;","q->delante = aux->sgte;","q->atras = NULL;"}:
                lhs,rhs=line.rstrip(";").split(" = ");queue[lhs.split("->")[1]]=expression(rhs,old,values)
            elif line in {"g = grafo_marcar_vertice(g, inicio);","g = grafo_marcar_vertice(g, suces->dato);","g = grafo_marcar_vertice(g, actual);"}:
                vertex=values["inicio"] if "inicio);" in line else expression("suces->dato",old,values) if "suces->dato);" in line else values["actual"]
                marked=[n for n in a.values() if n["kind"]=="vertex" and n["value"]==vertex];assert len(marked)==1 and marked[0]["mark"]==1 and vertex not in discovery
                discovery.append(vertex)
                parent=None if vertex==1 else old["active"] if bfs else old["recursive_frames"][-2]["parameters"]["actual"]
                parents[str(vertex)]=parent

        assert actual==expected,"unexpected physical traversal mutation";tracked=actual
        assert new["queue"]==queue and new["freed_nodes"]==freed
        assert new["allocations"]==old["allocations"]+int(phase=="allocate") and new["frees"]==old["frees"]+int(phase=="free")
        assert new["discovery"]==discovery and new["parents"]==parents
        marks={n["value"]:n["mark"] for n in actual.values() if n["kind"]=="vertex"}
        assert {n["vertex"]:n["mark"] for n in new["graph_marks"]}==marks
        assert new["queue_nodes"]==chain(new,new["queue"]["delante"])
        frame_function="grafo_bfs" if bfs else "grafo_dfs";frames=[f for f in new["frames"] if f["function"]==frame_function]
        root=frames[0]["locals"].get("recorrido","NULL") if frames else new["returned"]
        if root=="sin inicializar":root="NULL"
        assert new["result_nodes"]==chain(new,root)
        auxiliary=row["auxiliary"];traversal=row["traversal"]
        if bfs:
            assert auxiliary["kind"]=="queue" and auxiliary["items"]==[str(n["value"]) for n in new["queue_nodes"] if n["value"]!="sin inicializar"]
        else:
            recursive=[f for f in new["frames"] if f["function"]=="grafo_dfs_recursivo"]
            assert new["recursive_frames"]==recursive
            assert auxiliary["kind"]=="recursi\u00f3n C" and auxiliary["items"]==[f["parameters"]["actual"] for f in recursive]
            if function=="grafo_dfs_recursivo" and phase=="enter":
                oldframes=old["recursive_frames"];assert len(recursive)==len(oldframes)+1 and recursive[:-1]==oldframes;entered.append(recursive[-1]["parameters"]["actual"])
            if function=="grafo_dfs_recursivo" and phase=="return":
                assert recursive==old["recursive_frames"][:-1];returned.append(old["recursive_frames"][-1]["parameters"]["actual"])
        assert traversal["discovery_order"]==list(map(str,discovery))
        assert traversal["output_order"]==[str(n["value"]) for n in new["result_nodes"]]
        assert traversal["tree_edges"]==[[str(parent),child] for child,parent in parents.items() if parent is not None]
        assert row["console"]==[] and new["console_stdout"]==""
    final=p["rows"][-1]["memory"]
    assert final["frames"]==[] and p["result"]==[1,2,3] and discovery==[1,2,3]
    assert (final["allocations"],final["frees"])==((12,9) if bfs else (9,6))
    assert {n["kind"] for n in final["heap_nodes"] if n["id"].startswith("N")}=={"result"}
    assert [n["value"] for n in final["result_nodes"]]==[1,2,3]
    assert parents==({"1":None,"2":1,"3":1} if bfs else {"1":None,"2":1,"3":2})
    if not bfs:assert entered==[1,2,3] and returned==[3,2,1] and final["head_storage"]["live"] is False

def project_traversal(body,operation):
 trace=body["execution_trace"];layout=[];rows=[]
 for i,step in enumerate(trace["steps"]):
  p=step["pedagogy"];event=p["instruction_event"];line=step["line_text"]
  layout.append([step["line_index"],line,event.get("function"),event["phase"]])
  selected=operation!="run_bellman_ford" or (event.get("function")=="grafo_bellman_ford" and (event["phase"] in {"free","stdout","return"} or (event["phase"]=="write" and event.get("name") in {"dist[idx_inicio]","alcanzable[idx_inicio]","dist[v]","alcanzable[v]","prev[v]","cand","minimo_simple"}) or (event["phase"]=="condition" and ("alcanzable" in line or "n - 1" in line))))
  if selected:rows.append({"index":i,"line_index":step["line_index"],"line":line,"event":event,"auxiliary":p.get("auxiliary"),"traversal":p.get("traversal"),"table":p.get("table"),"before":p.get("instruction_state_before"),"after":p.get("instruction_state_after"),"memory":p.get("memory_state"),"console":step.get("console")})
 return {"operation":operation,"source":trace["source_code"],"layout":layout,"rows":rows,"success":body["success"],"result":body.get("result"),"history":body["history"],"final":body["visual_state"],"trace_final":trace["final_state"]}

def assert_saved_traversal(p):
    assert p["operation"] in SHAS and p["success"] is True
    assert hashlib.sha256(p["source"].encode()).hexdigest()==SHAS[p["operation"]]
    lines=p["source"].splitlines()
    for index,line,function,phase in p["layout"]:assert type(index) is int and 0<=index<len(lines) and lines[index]==line
    for row in p["rows"]:assert p["layout"][row["index"]]==[row["line_index"],row["line"],row["event"].get("function"),row["event"]["phase"]]
    assert p["trace_final"]==p["final"]
    assert_traversal_projection(p)
def assert_traversal_consumer(body,operation):assert_saved_traversal(project_traversal(body,operation))
