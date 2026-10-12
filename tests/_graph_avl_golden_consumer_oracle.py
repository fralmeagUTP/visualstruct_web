"""Only original graph1-2weight3 and AVL30,20,10 golden fixtures."""
from copy import deepcopy
import hashlib
from _tree_intermediate_consumer_oracle import _assert_tree_public_projection
SHAS={"graph":"8a8c55df893d3870d9aa01e0ea8cd8368d94b026a7fc55f957a37bea941a936b","tree":"36fb6488de4ccdaa289d336bc4cd0827204d11f9a8a6633e2bbf4bb9afd88073"}
ROTATION=["*r = B;","A->izq = C;","B->der = A;","A->padre = B;","B->padre = padre;","A->FE = A->FE + 1 - (B->FE < 0 ? B->FE : 0);","B->FE = B->FE + 1 + (A->FE > 0 ? A->FE : 0);"]
def nodes(m,tree=False):
    result={n["id"]:({k:v for k,v in n.items() if k!="status"} if tree else n) for n in m["heap_nodes"]}
    assert len(result)==len(m["heap_nodes"])
    return result
def project_golden(body,case):
    trace=body["execution_trace"];steps=trace["steps"];source=trace["source_code"];lines=source.splitlines();rows=[];layout=[];public_frames=[]
    assert hashlib.sha256(source.encode()).hexdigest()==SHAS[case]
    for i,s in enumerate(steps):
        assert type(s["line_index"]) is int and lines[s["line_index"]]==s["line_text"]
        p=s["pedagogy"];e=p["instruction_event"];line=s["line_text"].strip();phase=e["phase"]
        layout.append([s["line_index"],s["line_text"],phase])
        if case=="tree":
            public_frames.append(dict(index=i,before=s["state_snapshot"],after=s["state_after"],memory=p["memory_state"]))
            frames=s["state_after"].get("tree_frames",[]);function=frames[-1]["function"] if frames else ""
            if function=="avl_RSD" and phase=="after" and line in ROTATION:
                rows.append(dict(index=i,line=line,event=e,before=s["state_snapshot"],after=s["state_after"]))
        elif (e["function"]=="grafo_insertar_arco" and (phase=="allocate" or (phase=="write" and e["name"] in {"nuevo->sig","nuevo->origen","nuevo->destino","nuevo->costo","g.a"}))) or (e["function"]=="audit_graph_operation" and phase=="write" and e["name"]=="g"):
            rows.append(dict(index=i,line=line,event=e,before=p["instruction_state_before"],after=p["instruction_state_after"]))
    projection=dict(case=case,source=source,layout=layout,rows=rows,final=body["visual_state"],trace_final=trace["final_state"],last_memory=steps[-1]["pedagogy"]["memory_state"])
    if case=="tree":projection["public_frames"]=public_frames
    return projection
def assert_golden_projection(p):
    case=p["case"];assert case in SHAS
    assert hashlib.sha256(p["source"].encode()).hexdigest()==SHAS[case]
    assert len(p["layout"])==(131 if case=="graph" else 62)
    lines=p["source"].splitlines()
    for index,line,phase in p["layout"]:assert type(index) is int and lines[index]==line
    assert p["trace_final"]==p["final"]
    if case=="tree":
        assert "public_frames" in p, "incomplete historical projection cannot certify all steps"
        frames=p["public_frames"]
        assert [f["index"] for f in frames]==list(range(62)), "all instruction projections required"
        physical_before=frames[0]["before"]
        for frame in frames:
            _assert_tree_public_projection(frame["before"],physical_before,"avl")
            _assert_tree_public_projection(frame["memory"],frame["memory"],"avl")
            _assert_tree_public_projection(frame["after"],frame["memory"],"avl")
            physical_before=frame["memory"]
        _assert_tree_public_projection(p["final"],physical_before,"avl")
        assert [r["line"] for r in p["rows"]]==ROTATION
        prior_nodes=None;prior_head=None
        for r in p["rows"]:
            old=r["before"];new=r["after"];a=nodes(old,True);b=nodes(new,True);expected=deepcopy(a);head=old["head"]
            if prior_nodes is None:
                assert old["head"]=="N1" and a=={
                    "N1":{"id":"N1","value":30,"balance_factor":-2,"left":"N2","right":"NULL","parent":"NULL"},
                    "N2":{"id":"N2","value":20,"balance_factor":-1,"left":"N3","right":"NULL","parent":"N1"},
                    "N3":{"id":"N3","value":10,"balance_factor":0,"left":"NULL","right":"NULL","parent":"N2"}}
            else:assert a==prior_nodes and old["head"]==prior_head,"unexplained change between rotation stores"
            frame=new["tree_frames"][-1];assert frame["function"]=="avl_RSD" and frame["parameters"]=={"r":"&raiz","nodo":"N1"}
            env=frame["locals"];assert env=={"padre":"NULL","A":"N1","B":"N2","C":"NULL"}
            assert {k:v["value"] for k,v in a.items()}=={"N1":30,"N2":20,"N3":10}
            line=r["line"]
            if line==ROTATION[0]:head="N2"
            elif line==ROTATION[1]:expected["N1"]["left"]="NULL"
            elif line==ROTATION[2]:expected["N2"]["right"]="N1"
            elif line==ROTATION[3]:expected["N1"]["parent"]="N2"
            elif line==ROTATION[4]:expected["N2"]["parent"]="NULL"
            elif line==ROTATION[5]:expected["N1"]["balance_factor"]=a["N1"]["balance_factor"]+1-min(a["N2"]["balance_factor"],0)
            else:expected["N2"]["balance_factor"]=a["N2"]["balance_factor"]+1+max(a["N1"]["balance_factor"],0)
            _assert_tree_public_projection(old,old,"avl")
            _assert_tree_public_projection(new,new,"avl")
            assert b==expected and new["head"]==head
            prior_nodes=b;prior_head=head
            assert p["layout"][r["index"]][1].strip()==line and r["event"]["phase"]=="after"
        f=p["final"];assert f["size"]==3 and f["height"]==2 and f["validation"] is True
        root=f["root"];assert root["value"]==20 and root["left"]["value"]==10 and root["right"]["value"]==30
        assert f["traversals"]["inorden"]==[10,20,30]
        assert all(n["balance_factor"]==0 for n in (root,root["left"],root["right"]))
    else:
        expected_names=["malloc","nuevo->sig","nuevo->origen","nuevo->destino","nuevo->costo","g.a","g"]*2
        assert [r["event"]["name"] for r in p["rows"]]==expected_names
        prior_nodes=None;prior_graph=None
        for j,r in enumerate(p["rows"]):
            old=r["before"];new=r["after"];a=nodes(old);b=nodes(new);expected=deepcopy(a);e=r["event"];name=e["name"];phase=e["phase"];ident="M1" if j<7 else "M2";graph=deepcopy(old["graph"])
            if prior_nodes is None:
                assert old["graph"]=={"v":"V2","a":"NULL"}
                assert a=={
                    "V1":{"id":"V1","kind":"struct NodoV","borrowed":False,"fields":{"dato":1,"marcado":0,"sig":"NULL"},"alive":True},
                    "V2":{"id":"V2","kind":"struct NodoV","borrowed":False,"fields":{"dato":2,"marcado":0,"sig":"V1"},"alive":True}}
            else:assert a==prior_nodes and old["graph"]==prior_graph,"unexplained change between arc stores"
            assert old["frees"]==new["frees"]==0 and old["retired_objects"]==new["retired_objects"]==[]
            assert all(n["alive"] is True for n in list(a.values())+list(b.values()))
            if name=="malloc":
                assert phase=="allocate" and e["value"]=={"pointer":ident,"size":24,"zeroed":False}
                assert new["allocations"]==old["allocations"]+1
                expected[ident]={"id":ident,"kind":"struct NodoA","borrowed":False,"alive":True,"bytes":24,"fields":{k:"sin inicializar" for k in ("origen","destino","costo","sig")}}
            else:
                assert phase=="write" and old["allocations"]==new["allocations"]
                if name.startswith("nuevo->"):
                    field=name.split("->")[1];value={"sig":"NULL" if j<7 else "M1","origen":1 if j<7 else 2,"destino":2 if j<7 else 1,"costo":3}[field]
                    assert e["value"]==value;expected[ident]["fields"][field]=value
                elif name=="g.a":
                    assert e["value"]==ident
                    frame=next(f for f in new["frames"] if f["function"]=="grafo_insertar_arco")
                    env={**frame["parameters"],**{k:v["value"] for sc in frame["scopes"] for k,v in sc["variables"].items()}}
                    assert env["g"]["a"]==ident
                else:graph["a"]=ident;assert e["value"]==graph
            assert b==expected and new["graph"]==graph,"unexpected physical write/publication"
            prior_nodes=b;prior_graph=graph
            layout=p["layout"][r["index"]];assert layout[1].strip()==r["line"] and layout[2]==phase
        f=p["final"];assert f["directed"] is False and {n["id"] for n in f["nodes"]}=={"1","2"}
        assert [(e["source"],e["target"],e["weight"]) for e in f["edges"]]==[("1","2",3)]
        assert type(f["edges"][0]["weight"]) in (int,float) and f["edges"][0]["weight"]==3 and f["metadata"]["edges_count"]==1
        live=nodes(p["last_memory"]);assert len(live)==4 and p["last_memory"]["graph"]=={"v":"V2","a":"M2"}
def assert_golden_consumer(body,case):assert_golden_projection(project_golden(body,case))
