"""Finite native C branch oracle for the two vertex traces, never the preview."""
from copy import deepcopy
from pathlib import Path
import json, os, shutil, subprocess
import pytest
from app.services.c_code_service import CCodeService
from app.domain.graph.vertex_instruction import build_graph_vertex_trace

CASES = [
    ("insert_vertex", [], 7, False),
    ("insert_vertex", [1, 2, 3], 4, False),
    ("insert_vertex", [1, 2, 3], 3, False),
    ("insert_vertex", [1, 2, 3], 2, False),
    ("insert_vertex", [1, 2, 3], 1, False),
    ("insert_vertex", [], -2147483648, False),
    ("insert_vertex", [1], 2147483647, False),
    ("insert_vertex", [], 7, True),
    ("insert_vertex", [1, 2], 7, True),
    ("remove_vertex", [], 7, False),
    ("remove_vertex", [7], 7, False),
    ("remove_vertex", [1, 2, 3], 3, False),
    ("remove_vertex", [1, 2, 3], 2, False),
    ("remove_vertex", [1, 2, 3], 1, False),
    ("remove_vertex", [1, 2, 3], 9, False),
]

def state(values):
    return dict(structure="graph", directed=True, weighted=False,
                nodes=[dict(id=str(v),label=str(v),value=str(v),marked=0) for v in values],edges=[],
                metadata=dict(vertices_count=len(values),edges_count=0,is_empty=not values),last_result=None)


def instrument(source, operation):
    lines = source.splitlines()
    def index(text):
        return next(i for i,s in enumerate(lines) if text in s and not s.lstrip().startswith(("*","/")))
    def ev(text,phase,value="-1"):
        return f'ev({index(text)},"{phase}",{value},g);'
    name = "grafo_insertar_vertice" if operation=="insert_vertex" else "grafo_eliminar_vertice"
    # The body is the exact published C source with observer calls added.
    opening=source.index("{",source.index("Grafo "+name))
    source=source[:opening+1]+ev(name,"enter")+source[opening+1:]
    if operation=="insert_vertex":
        assignments=["ListaVertice actual = g.v;","actual = actual->sig;","nuevo->sig = g.v;","nuevo->dato = x;","nuevo->marcado = 0;","g.v = nuevo;"]
        conditions=[("actual != NULL","while (actual != NULL)"),("actual->dato == x","if (actual->dato == x)"),("nuevo == NULL","if (nuevo == NULL)")]
        for expression,text in conditions:
            source=source.replace("("+expression+")",f'(cond({index(text)},({expression}),g))',1)
        source=source.replace("return g;",'{'+ev("if (actual->dato == x)","return")+'return g;}',1)
        pos=source.index("if (cond",source.index("ListaVertice nuevo"))
        tail=source[pos:].replace("return g;",'{'+ev("if (nuevo == NULL)","return")+'return g;}',1)
        source=source[:pos]+tail
        statement="ListaVertice nuevo = (ListaVertice)malloc(sizeof(struct NodoV));"
        assert statement in source
        source=source.replace(statement,statement+ev("ListaVertice nuevo =","allocate"))
    else:
        assignments=["ListaVertice k=g.v, p;","g.v = g.v->sig;","k=k->sig;","p=k->sig;","k->sig=p->sig;"]
        conditions=[("g.v!=NULL","if (g.v!=NULL)"),("g.v->dato == x","if (g.v->dato == x)"),
                    ("(k->sig != NULL) && (k->sig->dato != x)","while ((k->sig != NULL)"),("k->sig!=NULL","if (k->sig!=NULL)")]
        for expression,text in conditions:
            evaluated=expression
            if text.startswith("while"):
                evaluated='operand("next_nonnull",k->sig != NULL) && operand("next_not_x",k->sig->dato != x)'
            source=source.replace("("+expression+")",f'(cond({index(text)},({evaluated}),g))',1)
        for text in ["free(k);","free(p);"]:
            source=source.replace(text,text+ev(text,"free"))
    for statement in assignments:
        assert statement in source
        source=source.replace(statement,("{"+statement+ev(statement,"assignment")+"}") if statement=="k=k->sig;" else statement+ev(statement,"assignment"))
    pos=source.rfind("return g;")
    source=source[:pos]+ev("    return g;" if operation=="insert_vertex" else "     return g;","return")+source[pos:]
    return source

@pytest.mark.parametrize("operation,vertices,x,fail",CASES)
def test_native_vertex_events_and_live_graph(tmp_path,operation,vertices,x,fail):
    gcc=shutil.which("gcc") or "C:/msys64/mingw64/bin/gcc.exe"
    assert Path(gcc).exists(), "The authorized finite native oracle requires installed GCC"
    out=Path(os.environ.get("GRAPH_VERTEX_QA_OUT",str(tmp_path)))/("native-"+operation+"-"+str(x)+"-"+str(len(vertices))+"-"+str(int(fail)))
    out.mkdir(parents=True,exist_ok=True)
    source=CCodeService.get_structure_data("graph")["operations"][operation]
    raw=Path("docs/tads_C/tad_grafo.c").read_text(encoding="utf-8-sig")
    assert source[source.index("Grafo grafo_"):].strip() in raw
    (out/"canonical-function.c.txt").write_text(source,encoding="utf-8")
    expected=list(vertices)
    if operation=="insert_vertex" and not fail and x not in expected:expected.append(x)
    if operation=="remove_vertex" and x in expected:expected.remove(x)
    before=state(vertices)
    if operation=="remove_vertex" and len(vertices)==3:
        before["edges"]=[dict(source="1",target="2",weight=5)]
        before["metadata"]["edges_count"]=1
    trace=build_graph_vertex_trace(operation_name=operation,payload={"vertex":x},source_code=source,code_title="C",
        before_state=before,after_state=state(expected),success=True,message="oracle",allocation_failure=fail)
    header=Path("docs/tads_C/tad_grafo.h").resolve()
    harness='#include "'+header.as_posix()+'"\n#include <stdio.h>\n#include <stdlib.h>\n'
    harness+=r"""
static int fail_alloc;
static void *observed_malloc(size_t n){return fail_alloc?NULL:malloc(n);}
static void ev(int line,const char *phase,int value,Grafo g){
 printf("%d|%s|%d|",line,phase,value);
 for(ListaVertice v=g.v;v!=NULL;v=v->sig)printf("%d,",v->dato);
 printf("|");
 for(ListaArco a=g.a;a!=NULL;a=a->sig)printf("%d,%d,%d;",a->origen,a->destino,a->costo);
 printf("\n");
}
int operand(const char *name,int value){fprintf(stderr,"OP|%s|%d\n",name,!!value);return value;}
static int cond(int line,int value,Grafo g){ev(line,"condition",!!value,g);return value;}
#define malloc observed_malloc
"""
    harness+=instrument(source,operation)+'\n#undef malloc\nint main(void){(void)observed_malloc;Grafo g={NULL,NULL};\n'
    for v in vertices:
        harness+=f'{{ListaVertice n=malloc(sizeof *n);if(!n)return 2;n->dato={v};n->marcado=0;n->sig=g.v;g.v=n;}}\n'
    if before["edges"]:
        harness+='ListaArco a=malloc(sizeof *a);if(!a)return 3;a->origen=1;a->destino=2;a->costo=5;a->sig=NULL;g.a=a;\n'
    fn="grafo_insertar_vertice" if operation=="insert_vertex" else "grafo_eliminar_vertice"
    harness+=f'fail_alloc={int(fail)};g={fn}(g,{x});\n'
    harness+='while(g.v){ListaVertice next=g.v->sig;free(g.v);g.v=next;}while(g.a){ListaArco next=g.a->sig;free(g.a);g.a=next;}return 0;}\n'
    (out/"observer.c").write_text(harness,encoding="utf-8")
    compiled=subprocess.run([gcc,"-std=c17","-Wall","-Wextra","-Werror",str(out/"observer.c"),"-o",str(out/"observer.exe")],capture_output=True,text=True)
    (out/"compile.log").write_text(compiled.stdout+compiled.stderr,encoding="utf-8");assert compiled.returncode==0,compiled.stderr
    native=subprocess.run([str(out/"observer.exe")],capture_output=True,text=True)
    (out/"native.log").write_text(native.stdout+native.stderr,encoding="utf-8");assert native.returncode==0
    rows=[]
    for row in native.stdout.splitlines():
        line,phase,value,graph,arcs=row.split("|")
        rows.append(dict(line_index=int(line),phase=phase,value=int(value),vertices=[int(v) for v in graph.split(",") if v],arcs=[[int(v) for v in arc.split(",")] for arc in arcs.split(";") if arc]))
    csteps=[s for s in trace["steps"] if s["pedagogy"]["instruction_event"]["C_executed"]]
    actual=[dict(line_index=s["line_index"],phase=s["phase"],value=int(s["pedagogy"]["condition"]["result"]) if s["phase"]=="condition" else -1,
                 vertices=[int(n["id"]) for n in reversed(s["state_after"]["nodes"])],
                 arcs=[[n["fields"][k] for k in ["origen","destino","costo"]] for n in s["pedagogy"]["memory_state"]["heap_nodes"] if n["kind"]=="struct NodoA"]) for s in csteps]
    assert rows==actual
    native_operands=[]
    for row in native.stderr.splitlines():
        tag,name,value=row.split("|");assert tag=="OP"
        native_operands.append(dict(name=name,value=bool(int(value))))
    model_operands=[]
    for step in csteps:
        if step["phase"]=="condition" and "while ((k->sig" in step["line_text"]:
            op=step["pedagogy"]["condition"]["evaluated_operands"]
            model_operands.append(dict(name="next_nonnull",value=op["k->sig"]!="NULL"))
            if "k->sig->dato" in op:model_operands.append(dict(name="next_not_x",value=op["k->sig->dato"]!=x))
    assert native_operands==model_operands

    for s in csteps:
        frame=s["pedagogy"]
        if s["phase"]=="free":assert any(v["value"].get("usable") is False for v in frame["variables"] if isinstance(v["value"],dict))
        if s["phase"]=="condition" and "while ((k->sig" in s["line_text"] and frame["condition"]["evaluated_operands"]["k->sig"]=="NULL":
            assert "k->sig->dato" not in frame["condition"]["evaluated_operands"]
    assert trace["steps"][-1]["state_after"]["nodes"]==state(expected)["nodes"]
    (out/"report.json").write_text(json.dumps(dict(operation=operation,vertices=vertices,x=x,malloc_failure=fail,
        native_events=rows,model_events=actual,native_operands=native_operands,model_operands=model_operands,exact_equal=True),indent=2),encoding="utf-8")
