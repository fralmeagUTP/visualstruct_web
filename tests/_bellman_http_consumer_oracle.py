"""Bounded original Bellman HTTP failure/unreachable consumers."""
from copy import deepcopy
import hashlib
SOURCE_SHA="a879bd47847aec3eee8006fa31e874f10a6b4279bf192dfcfa0d32a07a258461"
def _heap(m):
    nodes=m["heap_nodes"]
    assert len({x["id"] for x in nodes})==len(nodes)
    assert all(x["alive"] is True for x in nodes)
    return {x["id"]:x for x in nodes}
def _env(m):
    f=[f for f in m["frames"] if f["function"]=="grafo_bellman_ford"]
    assert len(f)==1
    return {name:v["value"] for s in f[0]["scopes"] for name,v in s["variables"].items()}
def project_bellman_http(body,case,status):
    trace=body["execution_trace"];source=trace["source_code"]
    assert hashlib.sha256(source.encode()).hexdigest()==SOURCE_SHA
    lines=source.replace("\r\n","\n").split("\n");rows=[];layout=[]
    for i,s in enumerate(trace["steps"]):
        p=s["pedagogy"];e=p["instruction_event"]
        assert type(s["line_index"]) is int and lines[s["line_index"]]==s["line_text"]
        assert p["source"]["line_index"]==s["line_index"] and p["source"]["line_text"]==s["line_text"]
        layout.append([s["line_index"],s["line_text"],e["function"],e["phase"]])
        line=s["line_text"].strip()
        if e["function"]=="grafo_bellman_ford" and (e["phase"] in {"free","stdout","return"} or (e["phase"]=="condition" and e.get("name") in {"!alcanzable[idx_llegada]","!alcanzable[v] || cand < dist[v]"})):
            rows.append(dict(index=i,line=line,event=e,before=p["instruction_state_before"],after=p["instruction_state_after"]))
    return dict(case=case,status=status,success=body["success"],result=body["result"],source=source,layout=layout,rows=rows,last_memory=trace["steps"][-1]["pedagogy"]["instruction_state_after"])
def assert_bellman_projection(p):
    assert p["case"] in {"cycle3","unreachable4","cycle23"};negative=p["case"]!="unreachable4"
    assert p["status"]==(400 if negative else 200) and p["success"] is (not negative)
    assert hashlib.sha256(p["source"].encode()).hexdigest()==SOURCE_SHA
    lines=p["source"].replace("\r\n","\n").split("\n")
    for index,line,function,phase in p["layout"]:assert type(index) is int and lines[index]==line
    freed=[];diagnostic=[];unreachable=[];decisive=[];returns=[]
    for r in p["rows"]:
        e=r["event"];phase=e["phase"];line=r["line"];old=r["before"];new=r["after"];a=_heap(old);b=_heap(new)
        layout=p["layout"][r["index"]];assert layout[1].strip()==line and layout[2]==e["function"]=="grafo_bellman_ford" and layout[3]==phase
        env=_env(old);expected=deepcopy(a)
        if phase=="condition":
            source=e["name"]
            def arr(name):
                node=a[env[name]];assert node["borrowed"] is False
                assert node["element_type"]==("long long" if name=="dist" else "int")
                return node["items"]
            if source=="!alcanzable[idx_llegada]":
                value=not arr("alcanzable")[env["idx_llegada"]];unreachable.append((r["index"],value))
            else:
                value=not arr("alcanzable")[env["v"]] or env["cand"]<arr("dist")[env["v"]]
                decisive.append((r["index"],value))
            assert type(e["value"]) is int and e["value"]==int(value)
        elif phase=="free":
            assert line.startswith("free(");name=line[5:-2];identity=env[name]
            assert e["value"]==identity and identity in a and a[identity]["borrowed"] is False
            del expected[identity];freed.append((r["index"],name))
            assert new["retired_objects"]==old["retired_objects"]+[{**a[identity],"alive":False,"historical_identity_only":True}]
        elif phase=="stdout":
            assert line=='printf("Se detecto un ciclo negativo.\\n");'
            assert new["console_stdout"]==old["console_stdout"]+"Se detecto un ciclo negativo.\n"
            diagnostic.append(r["index"])
        elif phase=="return":assert line=="return NULL;";returns.append(r["index"])
        else:raise AssertionError("unexpected focal phase")
        assert b==expected,"focal branch must not mutate graph or unrelated heap"
    assert [name for i,name in freed]==["dist","alcanzable","prev","vertices"] and len(returns)==1
    assert freed[-1][0]<returns[0]
    if negative:
        assert len(diagnostic)==1 and decisive[-1][1] is True
        assert decisive[-1][0]<diagnostic[0]<freed[0][0] and not unreachable
    else:assert not diagnostic and len(unreachable)==1 and unreachable[0][1] is True and unreachable[0][0]<freed[0][0]
    result=p["result"]
    assert result["has_negative_cycle"] is negative and result["reachable"] is False
    assert result["path"]==[] and result["path_edges"]==[] and result["distance_to_destination"] is None
    assert result["start"]==1 and result["end"]==(4 if not negative else 3)
    memory=p["last_memory"];assert memory["frames"]==[]
    assert all(node["borrowed"] is True for node in _heap(memory).values())
def assert_bellman_http(body,case,status):
    assert_bellman_projection(project_bellman_http(body,case,status))
