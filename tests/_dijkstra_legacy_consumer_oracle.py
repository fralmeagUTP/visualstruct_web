"""Two original small Dijkstra consumers; scoped array scan and physical stores."""
from copy import deepcopy
import hashlib
SOURCE_SHA="2e3c8f9d6179b88256094fda7ec4fa3ec41342de59fe1e18d1696f1f38f512e4"
LINES={"dist[idx_inicio] = 0;","min = dist[j];","u = j;","visitado[u] = 1;","dist[v] = nueva_dist;","prev[v] = u;","if (nueva_dist < dist[v]) {","if (u == -1) break;","if (v != -1 && !visitado[v]) {","free(dist);","free(prev);","free(visitado);","free(vertices);"}
EXPECTED={"chain":dict(n=3,distance=5,directed=False,selected=[1,2,3],updates=[(1,2,2),(2,3,5)]),"weighted":dict(n=4,distance=3,directed=True,selected=[1,3,2,3],updates=[(1,2,2),(1,3,9),(2,3,3)])}

def _heap(memory):
    nodes=memory["heap_nodes"];assert len({n["id"] for n in nodes})==len(nodes),"duplicate live reservation"
    assert all(n["alive"] is True for n in nodes)
    return {n["id"]:n for n in nodes}

def _env(memory):
    frames=[f for f in memory["frames"] if f["function"]=="grafo_dijkstra"]
    assert len(frames)==1
    result={}
    for scope in frames[0]["scopes"]:
        for name,v in scope["variables"].items():result[name]=v["value"]
    return result

def _array(memory,env,name):
    ident=env[name];assert ident in _heap(memory),"read requires live array"
    node=_heap(memory)[ident];assert node["borrowed"] is False and node["element_type"]=="int"
    return node["items"]

def project_dijkstra_consumer(body,case):
    assert case in EXPECTED;trace=body["execution_trace"];steps=trace["steps"];source=trace["source_code"]
    assert hashlib.sha256(source.encode()).hexdigest()==SOURCE_SHA
    lines=source.replace("\r\n","\n").split("\n");retired={};borrowed=None;selected=[];layout=[]
    for i,s in enumerate(steps):
        p=s["pedagogy"];event=p["instruction_event"];old=p["instruction_state_before"];new=p["instruction_state_after"]
        assert type(s["line_index"]) is int and lines[s["line_index"]]==s["line_text"]
        if i:
            previous=steps[i-1]["pedagogy"]["instruction_state_after"]
            expected=dict(previous)
            if old["frames"]!=previous["frames"]:
                expected["frames"]=[f for f in previous["frames"] if f.get("status")!="returning"]
                assert len(expected["frames"])<len(previous["frames"]), "only completed returning scope may retire between events"
            if old["allocation_attempts"]!=previous["allocation_attempts"]:
                assert event["phase"]=="allocate"
                expected["allocation_attempts"]+=1
            assert old==expected, "unexplained snapshot boundary change"
        assert p["source"]["line_index"]==s["line_index"] and p["source"]["line_text"]==s["line_text"]
        a,b=_heap(old),_heap(new)
        if borrowed is None:borrowed={k:v for k,v in a.items() if v["borrowed"]}
        assert {k:v for k,v in a.items() if v["borrowed"]}=={k:v for k,v in b.items() if v["borrowed"]}==borrowed
        for identity in a.keys()-b.keys():
            assert event["phase"]=="free" and event["value"]==identity and a[identity]["borrowed"] is False
            retired[identity]={**a[identity],"alive":False,"historical_identity_only":True}
        cards=new["retired_objects"];assert len({x["id"] for x in cards})==len(cards)
        assert {x["id"]:x for x in cards}==retired,"retired cards require prior causal free"
        layout.append([s["line_index"],s["line_text"],event["function"],event["phase"]])
        if s["line_text"].strip() in LINES and event["function"]=="grafo_dijkstra" and event["phase"] in {"write","condition","free","break"}:
            selected.append(dict(index=i,line=s["line_text"].strip(),event=event,before=old,after=new,table=p["table"],auxiliary=p["auxiliary"]))
    return dict(case=case,source=source,layout=layout,rows=selected,last_memory=steps[-1]["pedagogy"]["instruction_state_after"],result=body["result"],directed=body["visual_state"]["directed"],nodes=body["visual_state"]["nodes"],payload=trace["payload"])

def assert_dijkstra_projection(project):
    case=project["case"];assert case in EXPECTED;want=EXPECTED[case];n=want["n"]
    assert hashlib.sha256(project["source"].encode()).hexdigest()==SOURCE_SHA
    assert project["directed"] is want["directed"] and {x["id"] for x in project["nodes"]}=={str(i) for i in range(1,n+1)}
    assert project["payload"]=={"start":"1","end":"3"}
    assert len(project["rows"])==(27 if case=="chain" else 34)
    assert [r["index"] for r in project["rows"]]==sorted({r["index"] for r in project["rows"]})
    source_lines=project["source"].replace("\r\n","\n").split("\n")
    for index,line,function,phase in project["layout"]:
        assert type(index) is int and source_lines[index]==line
    selects=[];updates=[];prev_updates=[];visited=[];freed=[];blocked=0;breaks=0
    for row in project["rows"]:
        line=row["line"];event=row["event"];before=row["before"];after=row["after"];phase=event["phase"]
        layout=project["layout"][row["index"]]
        assert layout[1].strip()==line and layout[2]==event["function"]=="grafo_dijkstra" and layout[3]==phase
        if line.startswith("free("):assert phase=="free"
        elif line.startswith("if ("):assert phase in ({"condition","break"} if line=="if (u == -1) break;" else {"condition"})
        else:assert phase=="write"
        env=_env(before);new_env=_env(after);root=next(f for f in after["frames"] if f["function"]=="grafo_dijkstra")
        assert root["parameters"]=={"g":{"v":"V"+str(n),"a":"E4"},"inicio":1,"llegada":3}
        assert root["parameter_types"]=={"g":"Grafo","inicio":"int","llegada":"int"}
        old,actual=_heap(before),_heap(after);expected=deepcopy(old)
        assert row["auxiliary"]["kind"]=="linear_candidates"
        if phase=="write":
            if line=="min = dist[j];":assert new_env["min"]==_array(before,env,"dist")[env["j"]]
            elif line=="u = j;":
                assert new_env["u"]==env["j"]
                vertex=_array(before,env,"vertices")[env["j"]];selects.append(vertex)
                assert row["auxiliary"]["selected"]==str(vertex)
            else:
                name,index,value=("dist",env["idx_inicio"],0) if line=="dist[idx_inicio] = 0;" else ("visitado",env["u"],1) if line=="visitado[u] = 1;" else ("dist",env["v"],env["nueva_dist"]) if line=="dist[v] = nueva_dist;" else ("prev",env["v"],env["u"])
                assert 0<=index<n;expected[env[name]]["items"][index]=value
                vertices=_array(before,env,"vertices")
                if line=="visitado[u] = 1;":visited.append(vertices[env["u"]])
                if line=="dist[v] = nueva_dist;":
                    assert env["nueva_dist"]==_array(before,env,"dist")[env["u"]]+env["costo"]
                    updates.append((vertices[env["u"]],vertices[env["v"]],value))
                    assert _array(after,new_env,"prev")==_array(before,env,"prev"),"distance write must not publish predecessor"
                if line=="prev[v] = u;":prev_updates.append((vertices[env["u"]],vertices[env["v"]]))
        elif phase=="condition":
            if line=="if (nueva_dist < dist[v]) {":value=env["nueva_dist"]<_array(before,env,"dist")[env["v"]]
            elif line=="if (u == -1) break;":value=env["u"]==-1
            else:value=env["v"]!=-1 and not _array(before,env,"visitado")[env["v"]];blocked+=int(not value)
            assert type(event["value"]) is int and event["value"]==int(value)
        elif phase=="break":assert line=="if (u == -1) break;" and env["u"]==-1;breaks+=1
        elif phase=="free":
            name=line[5:-2];identity=env[name];assert event["value"]==identity and identity in expected and not expected[identity]["borrowed"]
            del expected[identity];freed.append(name)
            assert after["retired_objects"]==before["retired_objects"]+[{**old[identity],"alive":False,"historical_identity_only":True}]
        else:raise AssertionError("unknown focal event")
        assert actual==expected,"unexplained focal memory write/free"
        # A live table is read from current physical arrays, not cached final values.
        if all(name in new_env and new_env[name] in actual for name in ("dist","prev","visitado","vertices")):
            vertices=_array(after,new_env,"vertices");dist=_array(after,new_env,"dist");prev=_array(after,new_env,"prev");marks=_array(after,new_env,"visitado")
            assert vertices==list(range(n,0,-1))
            assert row["table"]["distances"]=={str(v):("∞" if dist[i]==2147483647 else dist[i]) for i,v in enumerate(vertices)}
            assert row["table"]["previous"]=={str(v):(None if prev[i]==-1 else vertices[prev[i]]) for i,v in enumerate(vertices)}
            assert set(row["table"]["visited"])=={str(v) for i,v in enumerate(vertices) if marks[i]}
    assert selects==want["selected"] and updates==want["updates"]
    assert prev_updates==[(u,v) for u,v,d in updates] and visited==[1,2,3]
    assert freed==["dist","prev","visitado","vertices"] and blocked>=1 and breaks==(1 if case=="weighted" else 0)
    result=project["result"];assert result["path"]==[1,2,3] and result["distance_to_destination"]==want["distance"]
    memory=project["last_memory"];live=_heap(memory);assert memory["frames"]==[]
    owned={k:v for k,v in live.items() if not v["borrowed"]};assert len(owned)==2
    arcs=[];identity=memory["returned"];seen=set()
    while identity!="NULL":
        assert identity in owned and identity not in seen;seen.add(identity);node=owned[identity];assert node["kind"]=="struct NodoA"
        fields=node["fields"];arcs.append([fields["origen"],fields["destino"],fields["costo"]]);identity=fields["sig"]
    assert seen==owned.keys() and arcs==[[1,2,2],[2,3,(3 if case=="chain" else 1)]]
    return updates

def assert_dijkstra_legacy_consumer(body,case):
    assert body["success"] is True
    trace=body["execution_trace"];assert trace["operation_name"]=="run_dijkstra"
    assert all(s["pedagogy"]["auxiliary"]["kind"]=="linear_candidates" for s in trace["steps"])
    return assert_dijkstra_projection(project_dijkstra_consumer(body,case))
