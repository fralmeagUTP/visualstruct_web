"""Causal traces for the two graph vertex functions; symbolic memory, no C execution.

The C list head order is reverse API insertion order. Raw C removal preserves
arcs; the existing API projection removes incident arcs and is labelled separately.
"""
from copy import deepcopy
import hashlib
import re
from .pedagogy import build_graph_frame, validate_graph_frame, graph_frame_schema, GRAPH_LEARNING_CATALOG
from .snapshot_pool import validate_graph_logical_trace, SnapshotPool, GraphLogicalTrace
from .incident_caller import incident_caller_lines, incident_vertex_literal

SUPPORTED_CALLER_LINES_SHA256 = '387d358cf7b4fa3e7c2d4c4e26077d815c7102203cf7ab5d330b83cfb31996c6'
NULL = "NULL"
UNINIT = "sin inicializar"
SUPPORTED_BODIES = {'insert_vertex': '20661fb4e1c1e2be9e1f36625657e57328895b693f0b390daf22f5ee82458b6f', 'remove_vertex': '11a03321e6be3d950c270d9c8b5e314b136373957dea6682cfc97e204eed6d0f'}


def build_graph_vertex_trace(*, operation_name, payload, source_code, code_title,
                             before_state, after_state, success, message,
                             allocation_failure=False, translate_incident_arcs=False):
    body = re.sub(r"\s+", "", re.sub(r"/\*.*?\*/|//[^\n]*", "", source_code, flags=re.S))
    if hashlib.sha256(body.encode()).hexdigest() != SUPPORTED_BODIES.get(operation_name):
        raise ValueError("Vertex trace C body changed: revalidate the bounded model before use")
    fn = "grafo_" + ("insertar_vertice" if operation_name == "insert_vertex" else "eliminar_vertice")
    raw_line_count = len(source_code.splitlines())
    caller_start = None
    caller_call = None
    caller_rows = []
    if translate_incident_arcs and success:
        if operation_name != "remove_vertex":
            raise ValueError("Incident caller is only a remove_vertex translation")
        caller_rows = incident_caller_lines(int(payload["vertex"]))
        literal = incident_vertex_literal(int(payload["vertex"]))
        supported = "\n".join(re.sub(r"\s+", "", row.replace(literal,"VERTEX")) for row in caller_rows)
        if hashlib.sha256(supported.encode()).hexdigest() != SUPPORTED_CALLER_LINES_SHA256:
            raise ValueError("Incident caller C fragment changed: revalidate its instruction model")
        caller_call = raw_line_count + 1
        caller_start = raw_line_count + 2
        source_code += "\n/* Fragmento del caller main.c, despues del retorno de la funcion C. */\n"
        source_code += f"    g = grafo_eliminar_vertice(g, {incident_vertex_literal(int(payload['vertex']))});\n" + "\n".join(caller_rows)
    comment = "/* Proyeccion API: recibe el retorno; eliminar vertice retira arcos incidentes en Python, no en esta funcion C. */"
    if translate_incident_arcs and success:
        comment = "/* Publicacion API: recibe el grafo del caller equivalente; grafo_eliminar_vertice conserva arcos, el caller retira incidentes. */"
    reject = "/* Validacion API: no se invoca la funcion C. */"
    source_code += "\n" + (comment if success else reject)
    lines = source_code.splitlines()
    def line(text):
        matches = [i for i, value in enumerate(lines[:raw_line_count]) if text in value and not value.lstrip().startswith(("*", "/"))]
        if len(matches) != 1:
            raise ValueError(("Vertex trace source drift", text, matches))
        return matches[0]
    vertices = [deepcopy(n) for n in before_state.get("nodes", [])]
    heap = {}
    head = NULL
    for i, node in enumerate(vertices):
        ident = "V" + str(i + 1)
        heap[ident] = dict(id=ident, kind="struct NodoV", fields={"dato":int(node["id"]), "marcado":node.get("marked", 0), "sig":head})
        head = ident
    arcs = []
    for edge in before_state.get("edges", []):
        o, d, w = int(edge["source"]), int(edge["target"]), int(edge["weight"])
        arcs.append((o,d,w))
        if not before_state.get("directed") and o != d:
            arcs.append((d,o,w))
    ahead = NULL
    for i, (o,d,w) in enumerate(arcs):
        ident = "E" + str(i + 1)
        heap[ident] = dict(id=ident, kind="struct NodoA", fields={"origen":o,"destino":d,"costo":w,"sig":ahead})
        ahead = ident
    g = {"v":head, "a":ahead}
    locals_ = {}
    types = {"g":"Grafo", "x":"int", "actual":"ListaVertice", "nuevo":"ListaVertice", "k":"ListaVertice", "p":"ListaVertice", "enlace":"ListaArco *"}
    retired = []
    active = False
    frame_fn = fn
    frame_id = "F1"
    frame_status = "activo"
    scope_names = {}
    returned = UNINIT
    steps = []; pool = SnapshotPool(preserve_tuples=True)
    events = []
    template_nodes = {int(n["id"]): n for n in [*vertices, *after_state.get("nodes", [])]}
    def safe(value):
        if isinstance(value, str) and value in retired:
            return {"historical_identity":value, "usable":False, "value_status":"indeterminate_after_free"}
        if isinstance(value, dict):
            return {k:safe(v) for k,v in value.items()}
        return deepcopy(value)
    heap_cache = {};visual_cache = {}
    def heap_key():
        return tuple((key,tuple(node["fields"].items())) for key,node in heap.items())
    def memory():
        key=heap_key()
        if key not in heap_cache:heap_cache[key]=deepcopy(list(heap.values()))
        return {"heap_nodes":heap_cache[key], "retired_objects":list(retired),
                "graph":deepcopy(g), "returned":safe(returned),
                "frames":[{"function":frame_fn, "frame_id":frame_id, "scope_status":frame_status}] if active else []}
    def visual():
        values = []; pointer = g["v"]
        while pointer != NULL:
            fields = heap[pointer]["fields"]
            values.append(fields["dato"]); pointer = fields["sig"]
        state = deepcopy(before_state)
        state["nodes"] = [deepcopy(template_nodes[v]) for v in reversed(values)]
        if frame_fn == "main":
            pairs = set()
            arc = g["a"]
            while arc != NULL:
                fields = heap[arc]["fields"]
                pairs.add((fields["origen"],fields["destino"],fields["costo"]))
                arc = fields["sig"]
            state["edges"] = [deepcopy(edge) for edge in before_state.get("edges",[]) if
                (int(edge["source"]),int(edge["target"]),int(edge["weight"])) in pairs or
                (not state.get("directed") and (int(edge["target"]),int(edge["source"]),int(edge["weight"])) in pairs)]
            state["metadata"]["edges_count"] = len(state["edges"])
            state["weighted"] = any(float(edge["weight"]) != 1.0 for edge in state["edges"])
        state["metadata"].update(vertices_count=len(values), is_empty=not values)
        state["last_result"] = None
        state["last_operation"] = None
        return state
    def emit(text, phase, action=None, value=None, operands=None, c=True, source_index=None):
        nonlocal returned, frame_status
        old = memory(); previous = safe(locals_)
        old_fn, old_scopes = frame_fn, dict(scope_names)
        state_before = steps[-1]["state_after"] if steps else before_state
        if action:
            action()
        if phase == "return":
            returned = deepcopy(g)
            frame_status = "terminado (retorno)"
        new = memory()
        idx = source_index if source_index is not None else line(text) if c else len(lines)-1
        visual_key=(heap_key(),g["v"],g["a"],frame_fn=="main")
        if c and visual_key not in visual_cache:visual_cache[visual_key]=pool.intern(visual())
        state_after = visual_cache[visual_key] if c else deepcopy(after_state)
        note = {"enter":"Entrada: Grafo por valor y nodos propios compartidos con el caller.",
                "condition":"Se evalua esta condicion y solo se toma su rama real.",
                "allocate":"Reserva nueva: los campos siguen sin inicializar.",
                "free":"Finaliza la vida del nodo; sus aliases son identidades historicas no utilizables.",
                "return":"Se devuelve la cabeza actual por valor.",
                "api_projection":"La API recibe el resultado del caller equivalente; la funcion C de vertice conserva arcos y el caller los retira." if translate_incident_arcs else "La API recibe el resultado. La retirada de arcos incidentes pertenece a Python, no a esta funcion C.",
                "input_validation":"La API rechaza la solicitud sin invocar C."}.get(phase, "Se ejecuta esta instruccion C; no se anticipa una escritura futura.")
        if frame_fn == "main" and phase == "free":
            note = "El caller libera este arco ya desenlazado; la funcion de vertice no lo libero. Alias retirado no utilizable."
        step = dict(step_index=len(steps), line_index=idx, line_text=lines[idx], event_type="line", phase=phase,
                    delay_ms=170, state_snapshot=state_before, state_after=state_after, console=[],
                    debug={"stage":phase, "note":note, "vertex_memory":new})
        frame = build_graph_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success)
        current = safe(locals_)
        frame["variables"] = []
        old_cells = {(old_scopes.get(k,old_fn),k):v for k,v in previous.items()}
        new_cells = {(scope_names.get(k,frame_fn),k):v for k,v in current.items()}
        for scope,k in dict.fromkeys([*old_cells,*new_cells]):
            before_value=old_cells.get((scope,k),"fuera de ambito")
            after_value=new_cells.get((scope,k),"fuera de ambito")
            frame["variables"].append(dict(name=k,type="ListaArco" if k=="actual" and scope.startswith("main") else types[k],previous=before_value,value=after_value,
                changed=before_value!=after_value,scope=scope,meaning="Valor de este ambito; aliases retirados no son punteros legibles."))
        frame["call_stack"] = deepcopy(new["frames"])
        frame["condition"] = dict(source=lines[idx].strip(),substituted=str(operands or {})+" => "+str(value),result=value,
                                   evaluated_operands=deepcopy(operands),consequence="Rama ejecutada registrada.") if phase=="condition" else None
        oldheap = {n["id"]:n for n in old["heap_nodes"]}
        frame["memory"].update(objects_before=old["heap_nodes"],objects_after=new["heap_nodes"],
                                allocated=[n for n in new["heap_nodes"] if n["id"] not in oldheap],
                                freed=[n for n in old["heap_nodes"] if n["id"] not in heap])
        event = dict(function=frame_fn if c else None,phase=phase,line_index=idx,C_executed=c,value=value,operands=deepcopy(operands),origin="caller" if frame_fn=="main" else "callee")
        if c: events.append(deepcopy(event))
        frame.update(vertex_operation=True,concept=phase,memory_state=new,instruction_state_before=old,instruction_state_after=new,
                     instruction_event=event,highlight_semantics="just-executed",
                     narration={level:note for level in ["basic","intermediate","advanced"]})
        frame["phase"].update(label=phase,goal=note)
        frame["invariant"].update(holds=None,symbol="?",evidence="Estado parcial; no se afirma el resultado futuro ni integridad de arcos del C crudo.")
        if not steps:
            initial = deepcopy(frame)
            initial.update(variables=[],call_stack=[],condition=None,concept="initial",memory_state=old,
                           state_before=deepcopy(before_state),state_after=deepcopy(before_state),instruction_event={"C_executed":False,"phase":"initial"})
            frame["initial_frame"] = initial
        validate_graph_frame(frame,source_code=source_code)
        step["pedagogy"] = frame
        steps.append(pool.intern(step))
    if success:
        def enter():
            nonlocal active
            active = True
            locals_.update(g=g, x=int(payload["vertex"]))
        emit(fn,"enter",enter)
        x = locals_["x"]
        if operation_name == "insert_vertex":
            emit("ListaVertice actual = g.v;","assignment",lambda:locals_.update(actual=g["v"]))
            duplicate = False
            while True:
                ptr = locals_["actual"]
                emit("while (actual != NULL)","condition",value=ptr!=NULL,operands={"actual":ptr})
                if ptr == NULL: break
                dato = heap[ptr]["fields"]["dato"]
                emit("if (actual->dato == x)","condition",value=dato==x,operands={"actual->dato":dato,"x":x})
                if dato == x:
                    duplicate = True
                    emit("if (actual->dato == x)","return",value=deepcopy(g)); break
                emit("actual = actual->sig;","assignment",lambda:locals_.update(actual=heap[ptr]["fields"]["sig"]))
            if not duplicate:
                ident = "V"+str(len(vertices)+1)
                def reserve():
                    locals_["nuevo"] = NULL if allocation_failure else ident
                    if not allocation_failure: heap[ident] = dict(id=ident,kind="struct NodoV",fields={"sig":UNINIT,"dato":UNINIT,"marcado":UNINIT})
                emit("ListaVertice nuevo =","allocate",reserve)
                emit("if (nuevo == NULL)","condition",value=allocation_failure,operands={"nuevo":locals_["nuevo"]})
                if allocation_failure:
                    emit("if (nuevo == NULL)","return",value=deepcopy(g))
                else:
                    for field, value_ in [("sig",g["v"]),("dato",x),("marcado",0)]:
                        emit("nuevo->"+field+" =","assignment",lambda field=field,value_=value_:heap[ident]["fields"].update({field:value_}))
                    emit("g.v = nuevo;","assignment",lambda:g.update(v=ident))
                    emit("    return g;","return",value=deepcopy(g))
        else:
            emit("ListaVertice k=g.v, p;","assignment",lambda:locals_.update(k=g["v"],p=UNINIT))
            emit("if (g.v!=NULL)","condition",value=g["v"]!=NULL,operands={"g.v":g["v"]})
            if g["v"] != NULL:
                ptr = g["v"]; dato = heap[ptr]["fields"]["dato"]
                emit("if (g.v->dato == x)","condition",value=dato==x,operands={"g.v->dato":dato,"x":x})
                if dato == x:
                    emit("g.v = g.v->sig;","assignment",lambda:g.update(v=heap[ptr]["fields"]["sig"]))
                    def free_head(): retired.append(ptr); del heap[ptr]
                    emit("free(k);","free",free_head)
                else:
                    while True:
                        ptr = locals_["k"]; following = heap[ptr]["fields"]["sig"]
                        operands = {"k->sig":following}
                        if following != NULL: operands.update({"k->sig->dato":heap[following]["fields"]["dato"],"x":x})
                        condition = following!=NULL and heap[following]["fields"]["dato"]!=x
                        emit("while ((k->sig != NULL)","condition",value=condition,operands=operands)
                        if not condition: break
                        emit("k=k->sig;","assignment",lambda:locals_.update(k=following))
                    emit("if (k->sig!=NULL)","condition",value=following!=NULL,operands={"k->sig":following})
                    if following != NULL:
                        emit("p=k->sig;","assignment",lambda:locals_.update(p=following))
                        emit("k->sig=p->sig;","assignment",lambda:heap[ptr]["fields"].update(sig=heap[following]["fields"]["sig"]))
                        def free_following(): retired.append(following); del heap[following]
                        emit("free(p);","free",free_following)
            emit("     return g;","return",value=deepcopy(g))
        returned = deepcopy(g)
        if translate_incident_arcs:
            def receive_caller():
                nonlocal frame_fn, frame_id, frame_status
                locals_.clear(); scope_names.clear()
                frame_fn="main";frame_id="Fcaller";frame_status="activo"
                locals_["g"]=g;scope_names["g"]="main"
            emit("", "caller_receipt", receive_caller, value=deepcopy(g), source_index=caller_call)
            def caller_event(offset,phase,action=None,value=None,operands=None):
                emit("",phase,action,value,operands,source_index=caller_start+offset)
            caller_event(0,"scope_enter")
            caller_event(1,"assignment",lambda:(locals_.update(enlace="&g.a"),scope_names.update(enlace="main/block")))
            def read_link():
                ref=locals_["enlace"]
                if ref=="&g.a":return g["a"]
                owner=ref[1:-4]
                if owner not in heap:raise ValueError("Caller enlace targets a retired object")
                return heap[owner]["fields"]["sig"]
            def write_link(value_):
                ref=locals_["enlace"]
                if ref=="&g.a":g["a"]=value_
                else:heap[ref[1:-4]]["fields"]["sig"]=value_
            iteration=0
            while True:
                pointer=read_link()
                caller_event(2,"condition",value=pointer!=NULL,operands={"*enlace":pointer})
                if pointer==NULL:break
                iteration+=1
                def declare_actual():
                    locals_["actual"]=pointer;scope_names["actual"]=f"main/block/body{iteration}"
                caller_event(3,"assignment",declare_actual)
                fields=heap[pointer]["fields"]
                operands={"actual->origen":fields["origen"],"literal":int(payload["vertex"])}
                if fields["origen"]!=int(payload["vertex"]):operands["actual->destino"]=fields["destino"]
                incident=fields["origen"]==int(payload["vertex"]) or fields["destino"]==int(payload["vertex"])
                caller_event(4,"condition",value=incident,operands=operands)
                if incident:
                    caller_event(5,"assignment",lambda:write_link(fields["sig"]))
                    def free_arc():
                        retired.append(pointer);del heap[pointer]
                    caller_event(6,"free",free_arc)
                else:
                    caller_event(8,"assignment",lambda:locals_.update(enlace="&"+pointer+".sig"))
                def end_body():
                    locals_.pop("actual");scope_names.pop("actual")
                caller_event(10,"scope_exit",end_body)
            caller_event(11,"scope_exit",lambda:(locals_.pop("enlace"),scope_names.pop("enlace")))
        def receipt():
            nonlocal active
            if not translate_incident_arcs:
                active = False
                locals_.clear()
        emit("", "api_projection", receipt, c=False)
    else:
        emit("", "input_validation", c=False)
    trace = GraphLogicalTrace(snapshot_pool=pool,structure_id="graph",operation_name=operation_name,payload=deepcopy(payload),success=success,
                mutates=operation_name in {"insert_vertex","remove_vertex"},message=message,code_title=code_title,
                source_code=source_code,steps=steps,final_state=deepcopy(after_state),pedagogy_schema_version=1,pedagogy_schema=graph_frame_schema(),
                learning_profile=deepcopy(GRAPH_LEARNING_CATALOG["construction"]),
                vertex_instruction_model=True,incident_caller_model=bool(translate_incident_arcs and success),execution_started=success,highlight_semantics="just-executed",C_instruction_events=events,
                instruction_scope="Vertex C function plus optional exact caller incident-arc fragment after return; API publication/rejection are non-C. Symbolic model, native QA separate.")
    validate_graph_logical_trace(trace)
    return trace
