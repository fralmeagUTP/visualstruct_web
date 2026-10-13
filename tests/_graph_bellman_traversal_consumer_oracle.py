"""Only instructed Bellman7/cycle3 and original weighted4 BFS/DFS consumers."""
from copy import deepcopy
import hashlib,random,re
SHAS={"run_bellman_ford":"a879bd47847aec3eee8006fa31e874f10a6b4279bf192dfcfa0d32a07a258461","run_bfs":"f2cbcf9014d5db332c4a72ae528cbb700e22cde520a298c372f6f8d6d29cd171","run_dfs":"9230a427009bb3f83e07b036d5adb42f257ed4686ad41f1fc82fa4fd1b505206"}
def heap(memory):
    result={n["id"]:n for n in memory["heap_nodes"]}
    assert len(result)==len(memory["heap_nodes"]);return result
def env(memory,function):
    frames=[f for f in memory["frames"] if f["function"]==function];assert frames
    f=frames[-1];values=dict(f["parameters"])
    if "locals" in f:values.update(f["locals"])
    for s in f.get("scopes",[]):values.update({k:v["value"] for k,v in s["variables"].items()})
    return values
def array(memory,values,name):
    node=heap(memory)[values[name]];assert node["borrowed"] is False
    assert node["element_type"]==("long long" if name=="dist" else "int")
    return node["items"]
def seed_calls():
    rng=random.Random(484589473);vertices=list(range(1,8));shuffled=vertices[:];rng.shuffle(shuffled);calls=[]
    for i in range(1,7):calls.append((shuffled[rng.randrange(0,i)],shuffled[i],rng.randint(1,20)))
    existing={tuple(sorted((a,b))) for a,b,c in calls};remaining=rng.randint(0,7);attempts=0;limit=max(30,remaining*20)
    while remaining>0 and attempts<limit:
        attempts+=1;a=rng.choice(vertices);b=rng.choice(vertices)
        if a==b or tuple(sorted((a,b))) in existing:continue
        calls.append((a,b,rng.randint(1,20)));existing.add(tuple(sorted((a,b))));remaining-=1
    return calls

def assert_bellman_projection(p):
    n=len(p["final"]["nodes"]);assert n in (3,7);negative=n==3
    assert p["success"] is (not negative) and p["final"]["directed"] is negative
    initial=p["rows"][0]["before"];borrowed={k:n for k,n in heap(initial).items() if n["borrowed"]}
    values=env(initial,"grafo_bellman_ford");g=values["g"];vertices=[];v=g["v"]
    while v!="NULL":vertices.append(borrowed[v]["fields"]["dato"]);v=borrowed[v]["fields"]["sig"]
    assert vertices==list(range(n,0,-1))
    arcs=[];a=g["a"]
    while a!="NULL":
        f=borrowed[a]["fields"];arcs.append((f["origen"],f["destino"],f["costo"]));a=f["sig"]
    calls=[(1,2,1),(2,3,-3),(3,1,1)] if negative else seed_calls()
    expected_arcs=list(reversed([arc for u,v,c in calls for arc in ([(u,v,c)] if negative else [(u,v,c),(v,u,c)])]))
    assert arcs==expected_arcs and len(arcs)==(3 if negative else 26)
    model_dist=[0]*n;reach=[0]*n;previous=[-1]*n;start=vertices.index(1);reach[start]=1;expected_updates=[]
    for iteration in range(n-1):
        for a,b,c in arcs:
            u=vertices.index(a);v=vertices.index(b)
            if reach[u] and (not reach[v] or model_dist[u]+c<model_dist[v]):
                model_dist[v]=model_dist[u]+c;reach[v]=1;previous[v]=u;expected_updates.append((a,b,model_dist[v]))
    updates=[];frees=[];diagnostics=[];loop=[];returns=[]
    for row in p["rows"]:
        old=row["before"];new=row["after"];e=row["event"];phase=e["phase"];name=e.get("name");values=env(old,"grafo_bellman_ford")
        a=heap(old);actual=heap(new);expected={k:deepcopy(node) for k,node in a.items()}
        assert {k:n for k,n in a.items() if n["borrowed"]}==borrowed
        if phase=="condition":
            if name=="i < n - 1":value=values["i"]<n-1;loop.append(bool(value))
            elif name=="u != -1 && v != -1 && alcanzable[u]":value=values["u"]!=-1 and values["v"]!=-1 and bool(array(old,values,"alcanzable")[values["u"]])
            elif name=="!alcanzable[v] || cand < dist[v]":value=not array(old,values,"alcanzable")[values["v"]] or values["cand"]<array(old,values,"dist")[values["v"]]
            elif name=="!alcanzable[idx_llegada]":value=not array(old,values,"alcanzable")[values["idx_llegada"]]
            elif name=="dist == NULL || alcanzable == NULL || prev == NULL || vertices == NULL":value=any(values[k]=="NULL" for k in ("dist","alcanzable","prev","vertices"))
            else:raise AssertionError("unexpected selected Bellman condition")
            assert type(e["value"]) is int and e["value"]==int(value)
        elif phase=="write":
            if name=="minimo_simple":assert e["value"]==(n-1)*-2147483648
            elif name=="cand":
                arc=a[values["a"]]["fields"];value=array(old,values,"dist")[values["u"]]+arc["costo"]
                assert e["value"]==value and env(new,"grafo_bellman_ford")["cand"]==value
            else:
                field="dist" if name.startswith("dist[") else "alcanzable" if name.startswith("alcanzable[") else "prev"
                index=values["idx_inicio"] if "idx_inicio" in name else values["v"]
                value=0 if name=="dist[idx_inicio]" else 1 if field=="alcanzable" else values["cand"] if field=="dist" else values["u"]
                assert type(value) is int and e["value"]==value
                expected[values[field]]["items"][index]=value
                if name=="dist[v]":
                    vertex_list=array(old,values,"vertices");updates.append((vertex_list[values["u"]],vertex_list[index],value))
        elif phase=="free":
            identity=e["value"];assert identity in a and a[identity]["borrowed"] is False
            del expected[identity];frees.append(identity)
            assert new["retired_objects"]==old["retired_objects"]+[{**a[identity],"alive":False,"historical_identity_only":True}]
        elif phase=="stdout":
            assert row["line"].strip()=='printf("Se detecto un ciclo negativo.\\n");'
            assert new["console_stdout"]==old["console_stdout"]+"Se detecto un ciclo negativo.\n";diagnostics.append(row["index"])
        elif phase=="return":returns.append((e["value"],actual))
        else:raise AssertionError("unexpected selected Bellman phase")
        assert actual==expected,"unexpected selected physical Bellman mutation"
    assert loop==[True]*(n-1)+[False] and frees==["M1","M2","M3","M4"] and len(returns)==1
    result=p["result"];assert result["has_negative_cycle"] is negative
    if negative:
        assert len(diagnostics)==1 and returns[0][0]=="NULL" and result["path"]==[] and result["reachable"] is False
        assert all(node["borrowed"] for node in returns[0][1].values())
    else:
        assert not diagnostics and updates==expected_updates
        distances={str(v):model_dist[i] if reach[i] else None for i,v in enumerate(vertices)}
        parents={str(v):None if previous[i]==-1 else vertices[previous[i]] for i,v in enumerate(vertices)}
        assert result["distances"]==distances and result["previous"]==parents and result["distance_to_destination"]==7
        assert result["path"]==[1,5,4] and result["path_edges"]==[[1,5],[5,4]] and result["reachable"] is True
        pointer,live=returns[0];path=[];seen=set()
        while pointer!="NULL":
            assert pointer in live and pointer not in seen;seen.add(pointer);node=live[pointer]
            assert node["borrowed"] is False;f=node["fields"];path.append((f["origen"],f["destino"],f["costo"]));pointer=f["sig"]
        assert path==[(1,5,2),(5,4,5)] and seen=={k for k,n in live.items() if not n["borrowed"]}

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
                if lhs=="k->marcado" and value==1 and a[identity]["mark"]==0:
                    vertex=a[identity]["value"];discovery.append(vertex)
                    parent=None if vertex==1 else old["active"] if bfs else old["recursive_frames"][-2]["parameters"]["actual"]
                    parents[str(vertex)]=parent
            elif line in {"q->delante = aux;","q->atras = aux;","q->delante = aux->sgte;","q->atras = NULL;"}:
                lhs,rhs=line.rstrip(";").split(" = ");queue[lhs.split("->")[1]]=expression(rhs,old,values)
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
            assert auxiliary["kind"]=="recursión C" and auxiliary["items"]==[f["parameters"]["actual"] for f in recursive]
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

def assert_graphbt_projection(p):
    operation=p["operation"];assert operation in SHAS
    assert hashlib.sha256(p["source"].encode()).hexdigest()==SHAS[operation]
    lines=p["source"].splitlines()
    for index,line,function,phase in p["layout"]:assert type(index) is int and 0<=index<len(lines) and lines[index]==line
    for row in p["rows"]:
        index=row["index"];assert p["layout"][index]==[row["line_index"],row["line"],row["event"].get("function"),row["event"]["phase"]]
    assert p["trace_final"]==p["final"]
    if operation=="run_bellman_ford":assert_bellman_projection(p)
    else:assert_traversal_projection(p)
def assert_graphbt_consumer(body):
    assert_graphbt_projection(project_graphbt(body,body["execution_trace"]["operation_name"]))
