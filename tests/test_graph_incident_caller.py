"""Downloaded Graph caller must translate API incident-arc removal after C return."""
from pathlib import Path
import json, os, shutil, subprocess
from app import create_app
from app.config import Config
from app.domain.graph.incident_caller import incident_caller_lines, incident_vertex_literal
import pytest
from _graph_trace_contract import decode_graph_http_trace


def private_client(path):
    class PrivateConfig(Config):
        APP_ENV="testing"
        TESTING=True
        SECRET_KEY="graph-incident-private-qa"
        SESSION_CACHE_DIR=str(path/"cache")
    return create_app(PrivateConfig).test_client()


def download_main_fixture(client,folder,history):
    folder.mkdir(parents=True,exist_ok=True)
    responses=[]
    for operation,payload in history:
        r=client.post("/graph/graph/operate",json={"operation":operation,"payload":payload})
        assert r.status_code==200 and r.json["success"]
        responses.append(r.json)
    r=client.get("/help/source/graph/main");assert r.status_code==200
    assert r.data==responses[-1]["main_c"].encode("utf-8")
    (folder/"downloaded-main.c").write_bytes(r.data)
    for structure,name in [("graph","tad_grafo"),("queue","tad_cola")]:
        for kind,ext in [("source","c"),("header","h")]:
            d=client.get("/help/source/"+structure+"/"+kind);assert d.status_code==200
            assert d.data==Path("docs/tads_C",name+"."+ext).read_bytes()
            (folder/(name+"."+ext)).write_bytes(d.data)
    (folder/"API.json").write_text(json.dumps(responses,ensure_ascii=False,indent=2),encoding="utf-8")
    logical_response=dict(responses[-1])
    logical_response["execution_trace"]=decode_graph_http_trace(logical_response["execution_trace"])
    return r.data.decode("utf-8"),logical_response


def native_final_probe(folder,main):
    pos=main.rfind("    while (g.a != NULL)");assert pos>=0
    observer=r"""    printf("PROBE vertices=%d arcs=%d\n",grafo_orden(g),grafo_tamano(g));
"""
    source=folder/"observed-main.c";source.write_text(main[:pos]+observer+main[pos:],encoding="utf-8",newline="\n")
    gcc=shutil.which("gcc") or "C:/msys64/mingw64/bin/gcc.exe"
    r=subprocess.run([gcc,"-std=c17","-Wall","-Wextra","-Werror","-I",str(folder),str(source),str(folder/"tad_grafo.c"),str(folder/"tad_cola.c"),"-o",str(folder/"observed-main.exe")],capture_output=True,text=True)
    (folder/"compile.log").write_text(r.stdout+r.stderr,encoding="utf-8");assert r.returncode==0,r.stderr
    r=subprocess.run([str(folder/"observed-main.exe")],capture_output=True,text=True)
    (folder/"native.log").write_text(r.stdout+r.stderr,encoding="utf-8");assert r.returncode==0
    return r.stdout


def test_downloaded_main_selfloop_remove_vertex_matches_API_before_final_cleanup(tmp_path):
    folder=Path(os.environ.get("GRAPH_INCIDENT_QA_OUT",str(tmp_path)))/"selfloop-baseline"
    client=private_client(tmp_path)
    main,data=download_main_fixture(client,folder,[
        ("insert_vertex",{"vertex":1}),
        ("insert_edge",{"origin":1,"target":1,"weight":5}),
        ("remove_vertex",{"vertex":1}),
    ])
    assert data["visual_state"]["nodes"]==data["visual_state"]["edges"]==[]
    actual=native_final_probe(folder,main)
    (folder/"report.json").write_text(json.dumps(dict(expected="PROBE vertices=0 arcs=0\n",actual=actual,API_vertices=0,API_arcs=0),indent=2),encoding="utf-8")
    assert actual=="PROBE vertices=0 arcs=0\n"


CALLER_FIXTURES = [
    ("directed-mixed",True,[1,2,3,4],[(2,1,3),(1,3,4),(1,1,5),(3,4,6)],1),
    ("undirected-mixed",False,[1,2,3,4],[(2,1,3),(1,3,4),(1,1,5),(3,4,6)],1),
    ("empty-arcs",True,[1,2],[],1),
    ("int-min-selfloop",True,[-2147483648,2],[(-2147483648,-2147483648,-2147483648)],-2147483648),
    ("all-incidents",True,[1,2,3],[(1,2,3),(3,1,4),(1,1,5)],1),
]


def observe_caller_and_ownership(folder,main,vertex):
    rows=incident_caller_lines(vertex)
    observed=list(rows)
    emit=lambda i,phase:'ev('+str(i)+',"'+phase+'",-1,g);'
    observed[0]+=emit(0,"scope_enter")
    observed[1]+=emit(1,"assignment")
    observed[2]=observed[2].replace("*enlace != NULL",'cond(2,*enlace != NULL,g)')
    observed[3]+=emit(3,"assignment")
    literal=incident_vertex_literal(vertex)
    expression=f"actual->origen == {literal} || actual->destino == {literal}"
    evaluated=f'operand("origin",actual->origen == {literal}) || operand("target",actual->destino == {literal})'
    observed[4]=observed[4].replace(expression,'cond(4,('+evaluated+'),g)')
    observed[5]+=emit(5,"assignment")
    observed[6]+=emit(6,"free")
    observed[8]+=emit(8,"assignment")
    # Observer before the lexical close never reads the retiring body local.
    observed[10]='        '+emit(10,"scope_exit")+observed[10]
    observed[11]+=emit(11,"scope_exit")
    fragment="\n".join(rows);assert main.count(fragment)==1
    code=main.replace(fragment,"\n".join(observed))
    call=f"    g = grafo_eliminar_vertice(g, {incident_vertex_literal(vertex)});";assert code.count(call)==1
    code=code.replace(call,call+emit(-1,"caller_receipt"))
    prefix=r"""
#include "tad_grafo.h"
#include <stdio.h>
static void ev(int offset,const char *phase,int value,Grafo g){
 printf("EV|%d|%s|%d|",offset,phase,value);
 for(ListaVertice v=g.v;v!=NULL;v=v->sig)printf("%d,",v->dato);
 printf("|");
 for(ListaArco a=g.a;a!=NULL;a=a->sig)printf("%d,%d,%d;",a->origen,a->destino,a->costo);
 printf("\n");
}
static int operand(const char *name,int value){fprintf(stderr,"OP|%s|%d\n",name,!!value);return value;}
static int cond(int offset,int value,Grafo g){ev(offset,"condition",!!value,g);return value;}
"""
    code=prefix+code
    assert code.count("    return 0;")==1
    code=code.replace("    return 0;","    audit_finish();\n    return 0;")
    (folder/"caller-observer.c").write_text(code,encoding="utf-8",newline="\n")
    hooks=r"""
#ifndef AUDIT_HOOKS_H
#define AUDIT_HOOKS_H
#include <stdlib.h>
#include <stdint.h>
void *audit_malloc(size_t);
void audit_free(void *);
void audit_finish(void);
#define malloc audit_malloc
#define free audit_free
#endif
"""
    (folder/"audit-hooks.h").write_text(hooks,encoding="utf-8")
    runtime=r"""
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
static struct {uintptr_t address;int live;int frees;} objects[4096];
static int allocated,freed,duplicates;
void *audit_malloc(size_t size){
 void *p=malloc(size);if(p!=NULL){if(allocated==4096)exit(90);objects[allocated].address=(uintptr_t)p;objects[allocated].live=1;allocated++;}return p;
}
void audit_free(void *p){
 if(p==NULL)return;
 uintptr_t address=(uintptr_t)p;int found=-1;
 for(int i=allocated-1;i>=0;i--)if(objects[i].address==address && objects[i].live){found=i;break;}
 if(found<0){duplicates++;fprintf(stderr,"duplicate free blocked\n");exit(91);}
 objects[found].live=0;objects[found].frees++;freed++;free(p);
}
void audit_finish(void){
 int live=0,bad=0;for(int i=0;i<allocated;i++){live+=objects[i].live;bad+=objects[i].frees!=1;}
 printf("OWN|%d|%d|%d|%d|%d\n",allocated,freed,live,duplicates,bad);
 if(live || duplicates || bad)exit(92);
}
"""
    (folder/"audit-runtime.c").write_text(runtime,encoding="utf-8")
    gcc=shutil.which("gcc") or "C:/msys64/mingw64/bin/gcc.exe";logs=[];objects=[]
    for source in ["caller-observer.c","tad_grafo.c","tad_cola.c","audit-runtime.c"]:
        obj=folder/(source+".o");command=[gcc,"-std=c17","-Wall","-Wextra","-Werror","-I",str(folder)]
        if source!="audit-runtime.c":command += ["-include",str(folder/"audit-hooks.h")]
        r=subprocess.run(command+["-c",str(folder/source),"-o",str(obj)],capture_output=True,text=True)
        logs.append(r.stdout+r.stderr);assert r.returncode==0,r.stderr;objects.append(str(obj))
    exe=folder/"caller-observer.exe";r=subprocess.run([gcc,*objects,"-o",str(exe)],capture_output=True,text=True);logs.append(r.stdout+r.stderr)
    (folder/"ownership-compile.log").write_text("".join(logs),encoding="utf-8");assert r.returncode==0,r.stderr
    r=subprocess.run([str(exe)],capture_output=True,text=True)
    (folder/"ownership-native.log").write_text(r.stdout+r.stderr,encoding="utf-8");assert r.returncode==0,r.stdout+r.stderr
    events=[];ownership=None;operands=[]
    for line in r.stdout.splitlines():
        fields=line.split("|")
        if fields[0]=="OWN":ownership=dict(zip(["allocations","frees","live","duplicate_frees","wrong_free_count"],map(int,fields[1:])));continue
        assert fields[0]=="EV"
        _,offset,phase,value,vertices,arcs=fields
        events.append(dict(offset=int(offset),phase=phase,value=int(value),vertices=[int(v) for v in vertices.split(",") if v],arcs=[[int(v) for v in arc.split(",")] for arc in arcs.split(";") if arc]))
    for line in r.stderr.splitlines():
        tag,name,value=line.split("|");assert tag=="OP";operands.append(dict(name=name,value=bool(int(value))))
    return events,ownership,operands


@pytest.mark.parametrize("case,directed,vertices,arcs,remove",CALLER_FIXTURES,ids=[case[0] for case in CALLER_FIXTURES])
def test_native_caller_source_events_shortcircuit_and_unique_ownership(tmp_path,case,directed,vertices,arcs,remove):
    folder=Path(os.environ.get("GRAPH_INCIDENT_QA_OUT",str(tmp_path)))/case;client=private_client(tmp_path)
    history=[("create_graph",{"directed":directed})]+[("insert_vertex",{"vertex":v}) for v in vertices]
    history += [("insert_edge",{"origin":o,"target":d,"weight":w}) for o,d,w in arcs]
    history += [("remove_vertex",{"vertex":remove})]
    main,data=download_main_fixture(client,folder,history)
    trace=data["execution_trace"];assert trace["incident_caller_model"]
    fragment="\n".join(incident_caller_lines(remove));assert fragment in main and fragment in trace["source_code"]
    native,ownership,native_operands=observe_caller_and_ownership(folder,main,remove)
    steps=[s for s in trace["steps"] if s["pedagogy"]["instruction_event"]["C_executed"] and s["pedagogy"]["instruction_event"]["origin"]=="caller"]
    call_index=steps[0]["line_index"];actual=[];model_operands=[]
    for s in steps:
        memory=s["pedagogy"]["memory_state"];nodes={n["id"]:n for n in memory["heap_nodes"]}
        def chain(head,fields):
            output=[]
            while head!="NULL":
                n=nodes[head]["fields"];output.append([n[k] for k in fields]);head=n["sig"]
            return output
        condition=s["pedagogy"]["condition"]
        actual.append(dict(offset=s["line_index"]-call_index-1,phase=s["phase"],value=int(condition["result"]) if condition else -1,
            vertices=[v[0] for v in chain(memory["graph"]["v"],["dato"])],arcs=chain(memory["graph"]["a"],["origen","destino","costo"])))
        if s["phase"]=="condition" and "actual->origen" in s["line_text"]:
            operands=condition["evaluated_operands"]
            model_operands.append(dict(name="origin",value=operands["actual->origen"]==remove))
            if "actual->destino" in operands:model_operands.append(dict(name="target",value=operands["actual->destino"]==remove))
        if s["phase"]=="free":
            pointer=next(v for v in s["pedagogy"]["variables"] if v["name"]=="actual" and v["scope"].startswith("main"))["value"]
            assert pointer["usable"] is False and pointer["historical_identity"] in memory["retired_objects"]
        if s["phase"]=="scope_exit":
            assert "actual" not in {v["name"] for v in s["pedagogy"]["variables"] if v["value"]!="fuera de ambito"}
    for step in steps:
        recorded=step["pedagogy"]["memory_state"]["returned"]
        if isinstance(recorded,dict) and isinstance(recorded.get("a"),dict):
            assert recorded["a"]["usable"] is False and recorded["a"]["historical_identity"] in step["pedagogy"]["memory_state"]["retired_objects"]
    assert native==actual
    assert native_operands==model_operands
    raw_arcs=sum(1 if directed or o==d else 2 for o,d,w in arcs)
    assert ownership==dict(allocations=len(vertices)+raw_arcs,frees=len(vertices)+raw_arcs,live=0,duplicate_frees=0,wrong_free_count=0)
    assert actual[0]["arcs"]==native[0]["arcs"] # receipt is before any caller cleanup
    expected=[edge for edge in actual[0]["arcs"] if edge[0]!=remove and edge[1]!=remove]
    assert actual[-1]["arcs"]==expected
    assert sum(s["phase"]=="free" for s in steps)==sum(o==remove or d==remove for o,d,w in actual[0]["arcs"])
    (folder/"caller-report.json").write_text(json.dumps(dict(case=case,native_events=native,model_events=actual,native_operands=native_operands,model_operands=model_operands,ownership=ownership,exact_equal=True,helper_return_preserves_arcs=True,caller_removes_only_incidents=True),indent=2),encoding="utf-8")



def test_repeated_vertex_removal_caller_has_no_double_free(tmp_path):
    folder=Path(os.environ.get("GRAPH_INCIDENT_QA_OUT",str(tmp_path)))/"repeated-removals";client=private_client(tmp_path)
    history=[("create_graph",{"directed":False})]+[("insert_vertex",{"vertex":v}) for v in [1,2,3,4]]
    history += [("insert_edge",{"origin":o,"target":d,"weight":w}) for o,d,w in [(1,2,3),(2,3,4),(3,4,6),(1,1,5)]]
    history += [("remove_vertex",{"vertex":1}),("remove_vertex",{"vertex":2})]
    main,data=download_main_fixture(client,folder,history)
    events,ownership,operands=observe_caller_and_ownership(folder,main,2)
    assert events[0]["vertices"]==[4,3] # second callee returned, still with its incident arcs
    assert events[-1]["arcs"]==[[4,3,6],[3,4,6]]
    assert ownership==dict(allocations=11,frees=11,live=0,duplicate_frees=0,wrong_free_count=0)
    assert [int(n["id"]) for n in data["visual_state"]["nodes"]]==[3,4]
    assert data["visual_state"]["edges"]==[dict(source="3",target="4",weight=6.0)]
    (folder/"caller-report.json").write_text(json.dumps(dict(case="repeated-removals",native_events=events,ownership=ownership,native_operands=operands,exact_unique_free=True),indent=2),encoding="utf-8")



def test_unknown_caller_fragment_rejected_instead_of_fabricated_cleanup(monkeypatch):
    from app.domain.graph import vertex_instruction
    from app.services.c_code_service import CCodeService
    original=vertex_instruction.incident_caller_lines
    def changed(vertex):
        rows=original(vertex);rows[5]="            *enlace = NULL;";return rows
    monkeypatch.setattr(vertex_instruction,"incident_caller_lines",changed)
    with pytest.raises(ValueError,match="Incident caller C fragment changed"):
        vertex_instruction.build_graph_vertex_trace(operation_name="remove_vertex",payload={"vertex":1},
            source_code=CCodeService.get_structure_data("graph")["operations"]["remove_vertex"],code_title="C",
            before_state={},after_state={},success=True,message="guard",translate_incident_arcs=True)



def test_caller_partial_visual_weight_and_return_alias_follow_live_arcs(tmp_path):
    client=private_client(tmp_path)
    for operation,payload in [("insert_vertex",{"vertex":1}),("insert_edge",{"origin":1,"target":1,"weight":5})]:
        assert client.post("/graph/graph/operate",json={"operation":operation,"payload":payload}).json["success"]
    data=client.post("/graph/graph/operate",json={"operation":"remove_vertex","payload":{"vertex":1}}).json
    assert data["success"]
    steps=decode_graph_http_trace(data["execution_trace"])["steps"]
    freed=next(s for s in steps if s["phase"]=="free" and s["pedagogy"]["instruction_event"]["origin"]=="caller")
    unlink=next(s for s in steps if s["line_text"].strip()=="*enlace = actual->sig;")
    assert unlink["state_snapshot"]["weighted"] is True
    assert unlink["state_after"]["weighted"] is False and unlink["state_after"]["edges"]==[]
    assert any(n["kind"]=="struct NodoA" for n in unlink["pedagogy"]["memory_state"]["heap_nodes"]) # detached but still alive until free
    assert freed["state_snapshot"]["weighted"] is False
    assert freed["state_after"]["weighted"] is False and freed["state_after"]["edges"]==[]
    assert freed["state_after"]["last_result"] is None
    recorded=freed["pedagogy"]["memory_state"]["returned"]["a"]
    assert recorded["usable"] is False and recorded["historical_identity"] in freed["pedagogy"]["memory_state"]["retired_objects"]
    assert steps[-1]["state_after"]==data["visual_state"]
    for left,right in zip(steps,steps[1:]):
        assert left["pedagogy"]["instruction_state_after"]==right["pedagogy"]["instruction_state_before"]
    caller_receipt=next(s for s in steps if s["phase"]=="caller_receipt")
    assert caller_receipt["pedagogy"]["instruction_state_before"]["frames"][0]["scope_status"]=="terminado (retorno)"
    assert caller_receipt["pedagogy"]["instruction_state_after"]["frames"][0]["function"]=="main"
