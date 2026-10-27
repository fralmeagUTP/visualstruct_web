"""Source-bound grafo_sucesores instructions and an explicit owning query observer.

The observer is shown for ownership; successful neighbors queries are not added
into the downloadable chronological main. Native execution is independent QA.
"""
from copy import deepcopy
import hashlib
import re
from .pedagogy import build_graph_frame, validate_graph_frame, graph_frame_schema, GRAPH_LEARNING_CATALOG
from .snapshot_pool import validate_graph_logical_trace

NULL = "NULL"
UNINIT = "sin inicializar"
SUPPORTED_BODY = "f105e4b3a497a8cc86e81750768859e5211e5099b81d660e78219d42e33af5e4"
CALLER_ROWS = [
    "static void consulta_vecinos(Grafo g, int x) {",
    "    ListaVertice resultado = grafo_sucesores(g, x);",
    "    while (resultado != NULL) {",
    "        ListaVertice siguiente = resultado->sig;",
    "        free(resultado);",
    "        resultado = siguiente;",
    "    }",
    "}",
]


def build_graph_neighbor_trace(*, payload, source_code, code_title, before_state,
                               after_state, success, message, allocation_failures=()):
    normalized = re.sub(r"\s+", "", re.sub(r"/\*.*?\*/|//[^\n]*", "", source_code, flags=re.S))
    if hashlib.sha256(normalized.encode()).hexdigest() != SUPPORTED_BODY:
        raise ValueError("Neighbors C body changed: revalidate its instruction model")
    raw_count = len(source_code.splitlines())
    caller_start = raw_count + 1
    source_code += "\n/* Caller observador de consulta: libera la lista propia; no pertenece al main del historial. */\n" + "\n".join(CALLER_ROWS)
    source_code += "\n/* Publicacion API de consulta; rechazo no invoca C y consulta exitosa no agrega historial. */"
    lines = source_code.splitlines()
    # One appended comment occupies raw_count; the actual observer starts next.
    def line(text):
        matches = [i for i, s in enumerate(lines[:raw_count]) if text in s and not s.lstrip().startswith(("*", "/"))]
        if len(matches) != 1:
            raise ValueError(("Neighbors source drift", text, matches))
        return matches[0]
    heap = {}; head = NULL
    for i, node in enumerate(before_state.get("nodes", []), 1):
        ident = "V" + str(i)
        heap[ident] = {"id":ident,"kind":"struct NodoV","borrowed":True,
                       "fields":{"dato":int(node["id"]),"sig":head,"marcado":node.get("marked",0)}}
        head = ident
    arcs = []
    for edge in before_state.get("edges", []):
        o, d, w = int(edge["source"]), int(edge["target"]), int(edge["weight"])
        arcs.append((o,d,w))
        if not before_state.get("directed") and o != d:
            arcs.append((d,o,w))
    ahead = NULL
    for i, (o,d,w) in enumerate(arcs, 1):
        ident = "E" + str(i)
        heap[ident] = {"id":ident,"kind":"struct NodoA","borrowed":True,
                       "fields":{"origen":o,"destino":d,"costo":w,"sig":ahead}}
        ahead = ident
    g = {"v":head,"a":ahead}
    frames = []; retired = []; returned = UNINIT; steps = []; events = []
    types = {"g":"Grafo","x":"int","k":"ListaArco","ver":"ListaVertice",
             "nuevo":"ListaVertice","resultado":"ListaVertice","siguiente":"ListaVertice"}
    def safe(value):
        if isinstance(value,str) and value in retired:
            return {"historical_identity":value,"usable":False,"value_status":"indeterminate_after_free"}
        if isinstance(value,dict):return {k:safe(v) for k,v in value.items()}
        return deepcopy(value)
    def memory():
        return {"heap_nodes":deepcopy(list(heap.values())),"retired_objects":list(retired),
                "graph":deepcopy(g),"returned":safe(returned),
                "frames":[{k:v for k,v in f.items() if k not in {"values","scopes"}} for f in frames]}
    def cells():
        out = {}
        for f in frames:
            for name,value in f["values"].items():
                scope = f["function"] + "/" + f.get("scopes",{}).get(name,f["frame_id"])
                out[(scope,name)] = safe(value)
        return out
    def emit(text, phase, action=None, *, value=None, operands=None, caller=False, c=True, offset=None):
        old = memory(); previous = cells()
        state_before = deepcopy(steps[-1]["state_after"] if steps else before_state)
        if action:action()
        new = memory(); current = cells()
        idx = caller_start + offset if offset is not None else line(text) if c else len(lines)-1
        fn = "consulta_vecinos" if caller else "grafo_sucesores"
        state_after = deepcopy(before_state if c else after_state)
        if c:
            state_after["last_result"] = None
            state_after["last_operation"] = None
        note = {"enter":"Parametros por valor; el grafo y sus nodos son prestados.",
                "condition":"Solo se ejecuta la rama cuyo predicado resulta verdadero.",
                "allocate":"Reserva nueva: ningun campo se lee antes de inicializarse.",
                "free":"El caller libera solamente un nodo de la lista retornada; el grafo permanece prestado.",
                "return":"La cabeza de la lista propia retorna al caller.",
                "api_publication":"Se publica la consulta despues de que el observer libera la lista C; no agrega historial.",
                "input_validation":"La API rechaza la consulta sin invocar C."}.get(phase,"Se ejecuta esta asignacion sin anticipar valores futuros.")
        step = dict(step_index=len(steps),line_index=idx,line_text=lines[idx],event_type="line",phase=phase,
                    delay_ms=170,state_snapshot=state_before,state_after=state_after,console=[],debug={"stage":phase,"note":note})
        frame = build_graph_frame(operation_name="neighbors",payload=payload,step=step,source_lines=lines,success=success)
        frame["variables"] = [dict(name=name,type=types[name],scope=scope,
            previous=previous.get((scope,name),"fuera de ambito"),value=current.get((scope,name),"fuera de ambito"),
            changed=previous.get((scope,name))!=current.get((scope,name)),meaning="Valor del ambito; aliases retirados no se leen.")
            for scope,name in dict.fromkeys([*previous,*current])]
        frame["call_stack"] = deepcopy(new["frames"])
        frame["condition"] = dict(source=lines[idx].strip(),substituted=str(operands or {})+" => "+str(value),
            result=value,evaluated_operands=deepcopy(operands),consequence="Rama real registrada.") if phase=="condition" else None
        oldheap = {n["id"]:n for n in old["heap_nodes"]}
        frame["memory"].update(objects_before=old["heap_nodes"],objects_after=new["heap_nodes"],
            allocated=[n for n in new["heap_nodes"] if n["id"] not in oldheap],
            freed=[n for n in old["heap_nodes"] if n["id"] not in heap],dangling_references=[])
        event = dict(function=fn if c else None,phase=phase,line_index=idx,C_executed=c,
                     value=value,operands=deepcopy(operands),origin="caller" if caller else "callee")
        if c:events.append(deepcopy(event))
        frame.update(query_operation=True,concept=phase,memory_state=new,instruction_state_before=old,
            instruction_state_after=new,instruction_event=event,highlight_semantics="just-executed",
            narration={level:note for level in ["basic","intermediate","advanced"]})
        frame["source"]["function"] = fn if c else None
        frame["phase"].update(label=phase,goal=note)
        frame["invariant"].update(name="grafo prestado intacto",holds=True,symbol="V",evidence="Solo la lista propia de resultados se reserva y libera.")
        if not steps:
            initial = deepcopy(frame)
            initial.update(variables=[],call_stack=[],condition=None,concept="initial",memory_state=old,
                state_before=deepcopy(before_state),state_after=deepcopy(before_state),instruction_event={"C_executed":False,"phase":"initial"})
            initial["phase"] = {"id":"neighbors-initial","label":"initial","goal":"Antes de invocar C; sin frames activos."}
            initial["source"]["function"] = None
            frame["initial_frame"] = initial
        validate_graph_frame(frame,source_code=source_code)
        step["pedagogy"] = frame;steps.append(step)
    if success:
        x = int(payload["vertex"])
        emit("","enter",lambda:frames.append(dict(function="consulta_vecinos",frame_id="F0",scope_status="activo",values={"g":g,"x":x},scopes={})),caller=True,offset=0)
        def call():
            frames[0]["values"]["resultado"] = UNINIT
            frames[0]["scope_status"] = "pausado (llamada)"
        emit("","call",call,caller=True,offset=1)
        emit("ListaVertice grafo_sucesores","enter",lambda:frames.append(dict(function="grafo_sucesores",frame_id="F1",scope_status="activo",values={"g":g,"x":x},scopes={})))
        local = frames[-1]["values"]
        emit("ListaArco k = g.a;","assignment",lambda:local.update(k=g["a"]))
        emit("ListaVertice ver = NULL, nuevo;","assignment",lambda:local.update(ver=NULL,nuevo=UNINIT))
        attempt = 0
        while True:
            ptr = local["k"]
            emit("while (k != NULL)","condition",value=ptr!=NULL,operands={"k":ptr})
            if ptr == NULL:break
            fields = heap[ptr]["fields"]
            emit("if (k->origen == x)","condition",value=fields["origen"]==x,operands={"k->origen":fields["origen"],"x":x})
            if fields["origen"] == x:
                attempt += 1;ident = "R"+str(attempt);failed = attempt in allocation_failures
                def reserve():
                    local["nuevo"] = NULL if failed else ident
                    if not failed:heap[ident] = dict(id=ident,kind="struct NodoV",borrowed=False,fields={"dato":UNINIT,"sig":UNINIT,"marcado":UNINIT})
                emit("nuevo = (ListaVertice)malloc","allocate",reserve)
                emit("if (nuevo != NULL)","condition",value=not failed,operands={"nuevo":local["nuevo"]})
                if not failed:
                    for field, val in [("sig",local["ver"]),("dato",fields["destino"]),("marcado",0)]:
                        emit("nuevo->"+field+" =","assignment",lambda field=field,val=val:heap[ident]["fields"].update({field:val}))
                    emit("ver = nuevo;","assignment",lambda:local.update(ver=ident))
            emit("k = k->sig;","assignment",lambda:local.update(k=fields["sig"]))
        def finish():
            nonlocal returned
            returned = local["ver"];frames[-1]["scope_status"] = "terminado (retorno)"
        emit("return ver;","return",finish,value=local["ver"])
        def receipt():
            frames.pop();frames[0]["scope_status"] = "activo";frames[0]["values"]["resultado"] = returned
        emit("","caller_receipt",receipt,caller=True,offset=1)
        caller = frames[0]["values"];iteration = 0
        while True:
            ptr = caller["resultado"]
            emit("","condition",value=ptr!=NULL,operands={"resultado":ptr},caller=True,offset=2)
            if ptr == NULL:break
            iteration += 1
            def save_next():
                caller["siguiente"] = heap[ptr]["fields"]["sig"]
                frames[0]["scopes"]["siguiente"] = "F0/body"+str(iteration)
            emit("","assignment",save_next,caller=True,offset=3)
            def free_result():
                retired.append(ptr);del heap[ptr]
            emit("","free",free_result,caller=True,offset=4)
            emit("","assignment",lambda:caller.update(resultado=caller["siguiente"]),caller=True,offset=5)
            def leave_body():
                caller.pop("siguiente");frames[0]["scopes"].pop("siguiente")
            emit("","scope_exit",leave_body,caller=True,offset=6)
        emit("","scope_exit",lambda:frames.clear(),caller=True,offset=7)
        emit("","api_publication",c=False)
    else:
        emit("","input_validation",c=False)
    trace = dict(structure_id="graph",operation_name="neighbors",payload=deepcopy(payload),success=success,
        mutates=False,message=message,code_title=code_title,source_code=source_code,steps=steps,
        final_state=deepcopy(after_state),pedagogy_schema_version=1,pedagogy_schema=graph_frame_schema(),
        learning_profile=deepcopy(GRAPH_LEARNING_CATALOG["construction"]),neighbor_instruction_model=True,
        execution_started=bool(success),highlight_semantics="just-executed",C_instruction_events=events,
        instruction_scope="Actual grafo_sucesores plus explicit owning observer; API publication/rejection non-C. Observer excluded from chronological downloaded main.")
    validate_graph_logical_trace(trace)
    return trace
