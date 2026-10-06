"""Source-bound Graph queries and construction callers; isolated from Graph6.

This symbolic statement model evaluates literal downloaded definitions. Random
generation is represented only by its materialized C caller, never a C RNG.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import re
from typing import Any
from .c_algorithm_subset import Program, GraphMachine, Token, Node, UNINIT, NULL
from .numeric_instruction import variables
from .pedagogy import build_graph_frame, validate_graph_frame, graph_frame_schema, GRAPH_LEARNING_CATALOG
from .snapshot_pool import validate_graph_logical_trace, SnapshotPool, GraphLogicalTrace
from app.services.c_code_service import CCodeService

OPERATIONS = frozenset({'create_graph','clear_graph','insert_edge','remove_edge','exists_vertex','exists_edge','edge_weight','list_vertices','list_edges','generate_random_graph'})
QUERY_FUNCTIONS = {'exists_vertex':'grafo_existe_vertice','exists_edge':'grafo_existe_arco','edge_weight':'grafo_costo_arco','list_vertices':'grafo_vertices','list_edges':'grafo_arcos'}
SUPPORTED_BODIES = {'grafo_crear': 'af096fd86a848127a188d85c303c6500416f419170beddf8333830383ee47008', 'grafo_insertar_vertice': '20661fb4e1c1e2be9e1f36625657e57328895b693f0b390daf22f5ee82458b6f', 'grafo_insertar_arco': 'ceda32c53ecc0611fd0fba33fafc10c9afe5dc70ab1a53ddcaa9febb1fa5d2d6', 'grafo_eliminar_arco': 'f569ecd8e97f8bcf59de3e7618cb9660e691950bb83d4eb2b4603fb2dea0dad2', 'grafo_existe_vertice': '9351929b8e22ac886588d13b08ce0f0645dacafc06fec73954ff6b9b49ced43d', 'grafo_existe_arco': 'd64a2e0588b04c39633515ca5afe4682c6dad69f9b8f21022abb27f0a8539a1d', 'grafo_costo_arco': '3141356721d6cb111bc5a0b0d32178f0e8178dc60cdb8692e091f2b59dab1ba0', 'grafo_vertices': 'c06b7fda1eb765ecd6c3cab2c962cebd86d06ed7026690f2fa3838c607ede251', 'grafo_arcos': '70ead96ca6f818475fd10ae13e48e1426057ac30363839567dc5853b1d9f6e41'}
CONSTRUCTION_FUNCTIONS = frozenset(SUPPORTED_BODIES) | {"audit_graph_operation"}

class ConstructionProgram(Program):
    """Accept only the ten-operation definitions and the explicit caller."""
    def __init__(self, source: str):
        self.source = source
        pattern = r'/\*.*?\*/|//[^\n]*|"(?:\\.|[^"\\])*"|\d+|[A-Za-z_]\w*|->|\+\+|--|<=|>=|==|!=|&&|\|\||[{}()[\],;:.+*/%<>=!&-]'
        self.tokens = []
        cursor = 0
        for m in re.finditer(pattern, source, re.S):
            gap = source[cursor:m.start()]
            if gap.strip():
                raise ValueError(f"Unsupported C token at {cursor}: {gap!r}")
            cursor = m.end()
            if m.group().startswith(('/*', '//')):
                continue
            self.tokens.append(Token(m.group(), m.start(), m.end(), source.count('\n', 0, m.start())))
        if source[cursor:].strip():
            raise ValueError("Unsupported trailing C syntax")
        self.at = 0
        self.functions = {}
        while self.at < len(self.tokens):
            typ = self.type_name()
            name = self.pop()
            if name.text not in CONSTRUCTION_FUNCTIONS:
                raise ValueError(f"Function outside graph trace scope: {name.text}")
            self.need('(')
            params = []
            if self.peek() == 'void' and self.peek(1) == ')': self.pop()
            while self.peek() != ')':
                ptyp = self.type_name(); param = self.pop()
                params.append((param.text, ptyp))
                if self.peek() != ',':
                    break
                self.pop()
            self.need(')')
            body = self.statement()
            self.functions[name.text] = dict(name=name.text, type=typ, parameters=params,
                                            body=body, token=name)


class ConstructionMachine(GraphMachine):
    """Own graph nodes for mutating callers; preserve guarded C evaluation."""
    def statement(self, node: Node) -> None:
        if node.kind == 'decl' and all(d['type'] == 'Grafo' for d in node.data['declarations']):
            for declaration in node.data['declarations']:
                if declaration['init'] is None:
                    scope = self.frames[-1]['scopes'][-1]
                    self.emit(declaration['token'], 'declare', declaration['name'],
                              {'v':UNINIT,'a':UNINIT}, lambda:scope['variables'].__setitem__(
                                  declaration['name'], {'type':'Grafo','value':{'v':UNINIT,'a':UNINIT}}))
                else:
                    super().statement(type(node)(node.kind,node.token,node.end,
                        {**node.data,'declarations':[declaration]}))
            return
        super().statement(node)

    def _eval(self, node: Node) -> Any:
        if node.kind == 'call' and node.data['function'].data['name'] == 'printf':
            args = [self.eval(arg) for arg in node.data['args']]
            self.emit(node,'call','printf')
            text = args[0] % tuple(args[1:]) if len(args)>1 else args[0]
            self.emit(node,'stdout','printf',text,lambda:setattr(self,'stdout',self.stdout+text))
            return len(text)
        return super()._eval(node)

    def _snapshot_heap(self):
        # Construction nodes have flat scalar fields. Read every field/order;
        # reuse only an exactly unchanged encoded heap, never live C objects.
        fingerprint=tuple((key,tuple((name,tuple(value.items()) if isinstance(value,dict) else value)
            for name,value in node.items())) for key,node in self.heap.items())
        cached=getattr(self,'_heap_snapshot_cache',None)
        if cached is None or cached[0]!=fingerprint:
            encoded=self.encoded(list(self.heap.values()))
            snapshot_pool=getattr(self,'_snapshot_pool',None)
            if snapshot_pool is not None:encoded=snapshot_pool.intern(encoded)
            cached=(fingerprint,encoded)
            self._heap_snapshot_cache=cached
        return cached[1]

    def snapshot(self) -> dict[str, Any]:
        state = super().snapshot()
        if self.frames and self.frames[0]['function']=='audit_graph_operation':
            state['graph']=deepcopy(self.frames[0]['parameter_cells']['g']['value'])
        retired = {node['id'] for node in self.retired}
        def historical(value):
            if isinstance(value,str) and value in retired:
                return {'historical_identity':value,'usable':False,'value_status':'indeterminate_after_free'}
            if isinstance(value,dict):return {key:historical(v) for key,v in value.items()}
            if isinstance(value,list):return [historical(v) for v in value]
            return value
        for key in ['frames','graph','returned']:
            state[key]=historical(state[key])
        return state


def _raw_arcs(state: dict[str, Any]) -> list[tuple[int, int, int]]:
    arcs=[]
    for edge in state.get('edges',[]):
        o,d,w=int(edge['source']),int(edge['target']),int(edge['weight'])
        arcs.append((o,d,w))
        if not state.get('directed') and o!=d:arcs.append((d,o,w))
    return arcs


def _visual(memory: dict[str, Any], before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    """Project initialized linked nodes; API publication remains a distinct event."""
    state=deepcopy(before);state['last_result']=None;state['last_operation']=None
    heap={n['id']:n for n in memory['heap_nodes']}; graph=memory['graph']
    templates={int(n['id']):n for n in [*before.get('nodes',[]),*after.get('nodes',[])]}
    vertices=[];pointer=graph['v'];seen=set()
    while isinstance(pointer,str) and pointer in heap and pointer not in seen:
        seen.add(pointer);fields=heap[pointer]['fields'];value=fields.get('dato',UNINIT)
        if value!=UNINIT:
            node=deepcopy(templates.get(value,{'id':str(value),'label':str(value),'marked':0}))
            node['marked']=fields.get('marcado',0);vertices.append(node)
        pointer=fields.get('sig',NULL)
    state['nodes']=list(reversed(vertices));edges=[];pointer=graph['a'];seen=set()
    while isinstance(pointer,str) and pointer in heap and pointer not in seen:
        seen.add(pointer);fields=heap[pointer]['fields']
        if all(fields.get(k,UNINIT)!=UNINIT for k in ['origen','destino','costo']):
            edges.append((fields['origen'],fields['destino'],fields['costo']))
        pointer=fields.get('sig',NULL)
    edges.reverse();unique=[];keys=set()
    for o,d,w in edges:
        key=(o,d) if state.get('directed') else tuple(sorted((o,d)))
        if key in keys:continue
        keys.add(key);unique.append({'source':str(o),'target':str(d),'weight':w})
    state['edges']=unique
    state['metadata']={'vertices_count':len(state['nodes']),'edges_count':len(unique),'is_empty':not state['nodes']}
    return state


def build_graph_construction_trace(*, operation_name: str, payload: dict[str,Any],
        source_code: str, code_title: str, before_state: dict[str,Any],
        after_state: dict[str,Any], success: bool, message: str) -> dict[str,Any]:
    """Evaluate only executed statements of the authorized query/construction body."""
    if operation_name not in OPERATIONS:raise ValueError('Operation outside Graph10')
    raw=CCodeService._safe_read(CCodeService._DOCS_TADS_C/'tad_grafo.c')
    if operation_name in QUERY_FUNCTIONS:
        names=[QUERY_FUNCTIONS[operation_name]]
    elif operation_name=='remove_edge':names=['grafo_eliminar_arco']
    elif operation_name in {'insert_edge','generate_random_graph'}:
        names=['grafo_insertar_vertice','grafo_insertar_arco']
        if operation_name=='generate_random_graph':names.insert(0,'grafo_crear')
    else:names=['grafo_crear']
    bodies=[]
    for name in names:
        body=CCodeService._extract_function_with_comment(raw,name)
        normalized=re.sub(r'\s+','',re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S))
        if hashlib.sha256(normalized.encode()).hexdigest()!=SUPPORTED_BODIES[name]:
            raise ValueError('Graph10 C body changed: revalidate '+name)
        bodies.append(body)
    source_code='\n\n'.join(bodies)
    query=operation_name in QUERY_FUNCTIONS
    if not query:
        caller=['/* Caller equivalente de la operacion; el TAD no posee bandera directed ni generador aleatorio. */',
                'Grafo audit_graph_operation(Grafo g) {']
        if operation_name in {'create_graph','clear_graph','generate_random_graph'}:
            caller += ['    while (g.a != NULL) {','        ListaArco next = g.a->sig;',
                       '        free(g.a);','        g.a = next;','    }',
                       '    while (g.v != NULL) {','        ListaVertice next = g.v->sig;',
                       '        free(g.v);','        g.v = next;','    }','    g = grafo_crear();']
        if operation_name=='generate_random_graph' and success:
            # Exactly the accepted materialized order, without re-executing RNG.
            for node in after_state.get('nodes',[]):
                caller.append(f"    g = grafo_insertar_vertice(g, {int(node['id'])});")
            for o,d,w in _raw_arcs(after_state):
                caller.append(f'    g = grafo_insertar_arco(g, {o}, {d}, {w});')
        elif operation_name in {'insert_edge','remove_edge'} and success:
            o,d=int(payload['origin']),int(payload['target'])
            fn='grafo_insertar_arco' if operation_name=='insert_edge' else 'grafo_eliminar_arco'
            extra=', '+str(int(payload.get('weight',1))) if operation_name=='insert_edge' else ''
            caller.append(f'    g = {fn}(g, {o}, {d}{extra});')
            if not before_state.get('directed') and o!=d:
                caller.append(f'    g = {fn}(g, {d}, {o}{extra});')
        caller+=['    return g;','}'];source_code+='\n\n'+'\n'.join(caller)
    source_code+='\n/* Publicacion API: orden logico y resultado API; rechazo previo no invoca C. */'
    lines=source_code.splitlines();steps=[];pool=SnapshotPool(preserve_tuples=True)
    trace=GraphLogicalTrace(snapshot_pool=pool,structure_id='graph',operation_name=operation_name,payload=deepcopy(payload),
        success=success,mutates=not query,message=message,code_title=code_title,
        source_code=source_code,steps=steps,final_state=deepcopy(after_state),
        pedagogy_schema_version=1,pedagogy_schema=graph_frame_schema(),
        learning_profile=deepcopy(GRAPH_LEARNING_CATALOG['construction']),
        construction_instruction_model=True,highlight_semantics='just-executed',
        instruction_scope='Literal Graph10 definitions and equivalent owning/materialized caller; API publication/rejection explicitly non-C.')
    visual_cache = {};frame_cache = {}
    def callback(event,old,new):
        old=pool.intern(old);new=pool.intern(new)
        visual_key=(id(new["heap_nodes"]),id(new["graph"]))
        if visual_key not in visual_cache:visual_cache[visual_key]=pool.intern(_visual(new,before_state,after_state))
        index=event['line_index'];phase=event['phase'];note={
            'declare':'Declara almacenamiento; no anticipa inicializacion.',
            'write':'Completa esta escritura con el estado actual.',
            'return':'Retorna ahora; las instrucciones posteriores de la funcion se omiten.',
            'condition':'Evalua la guarda real; el corto circuito omite operandos.',
            'operand':'Evalua solo este operando del corto circuito.',
            'allocate':'Reserva propia; campos aun sin inicializar.',
            'free':'Libera un nodo propio; aliases retirados solo son registros historicos.',
            'stdout':'Emite ahora el diagnostico C con sus argumentos.',
            'call':'Prepara esta llamada; el retorno no se ha recibido.'}.get(phase,'Ambito y parametros de la invocacion actual.')
        step=dict(step_index=len(steps),line_index=index,line_text=lines[index],event_type='line',phase=phase,
            delay_ms=170,state_snapshot=steps[-1]['state_after'] if steps else before_state,
            state_after=visual_cache[visual_key],console=[event['value']] if phase=='stdout' else [],
            debug={'stage':phase,'note':note})
        frame_key=(index,phase,id(step['state_snapshot']),id(step['state_after']))
        if frame_key not in frame_cache:
            frame_cache[frame_key]=pool.intern(build_graph_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success))
        frame={**frame_cache[frame_key]}
        for field in ('memory','source','phase','invariant'):frame[field]=dict(frame[field])
        previous=variables(old);current=variables(new);frame['variables']=[]
        for key in dict.fromkeys([*previous,*current]):
            record=deepcopy(current.get(key) or previous[key]);a=previous.get(key,{}).get('value','fuera de ambito');b=current.get(key,{}).get('value','fuera de ambito')
            record.update(previous=a,value=b,changed=a!=b,meaning='Valor tipado del ambito; alias retirado no utilizable.');frame['variables'].append(record)
        frame['call_stack']=[dict(function=f['function'],frame_id=f['id'],scope_status='terminado (retorno)' if f.get('status')=='returning' else 'activo' if i==len(new['frames'])-1 else 'suspendido',parameters=f['parameters'],scopes=f['scopes']) for i,f in enumerate(new['frames'])]
        frame['condition']=dict(source=event['name'],substituted=event['name']+' => '+str(event['value']),result=bool(event['value']),consequence='Solo la rama real.',evaluated_nodes=event.get('evaluated_nodes',[])) if phase in {'condition','operand'} else None
        oldheap={n['id']:n for n in old['heap_nodes']};newheap={n['id']:n for n in new['heap_nodes']}
        frame['memory'].update(objects_before=old['heap_nodes'],objects_after=new['heap_nodes'],allocated=[n for k,n in newheap.items() if k not in oldheap],freed=[n for k,n in oldheap.items() if k not in newheap],dangling_references=[])
        frame.update(query_operation=query,construction_operation=not query,concept=phase,
            memory_state=new,instruction_state_before=old,instruction_state_after=new,
            instruction_event={**event,'C_executed':True,'origin':'caller' if event['function']=='audit_graph_operation' else 'callee'},
            highlight_semantics='just-executed',narration={level:note for level in ['basic','intermediate','advanced']},
            state_before=step['state_snapshot'],state_after=step['state_after'])
        frame['source']['function']=event['function'];frame['phase'].update(label=phase,goal=note)
        frame['invariant'].update(holds=None,symbol='?',evidence='Estado parcial de instrucciones, no resultado futuro.')
        if not steps:
            initial=deepcopy(frame);initial.update(variables=[],call_stack=[],condition=None,memory_state=old,concept='initial',state_before=deepcopy(before_state),state_after=deepcopy(before_state),instruction_event={'C_executed':False,'phase':'initial'})
            initial['phase'].update(label='Estado inicial',goal='Antes de invocar C; sin locales ni resultado futuro.')
            initial['source']['function']=None
            initial['instruction_event'].update(function=None)
            frame['initial_frame']=initial
        validate_graph_frame(frame,source_code=source_code);step['pedagogy']=frame;steps.append(pool.intern(step))
    vertices=[int(n['id']) for n in before_state.get('nodes',[])]
    machine=ConstructionMachine(ConstructionProgram(source_code),vertices,_raw_arcs(before_state),
        {int(n['id']):int(n.get('marked',0)) for n in before_state.get('nodes',[])},callback=callback)
    machine._snapshot_pool=pool
    for node in machine.heap.values():node['borrowed']=query
    if success:
        fn=QUERY_FUNCTIONS[operation_name] if query else 'audit_graph_operation';args=[machine.graph]
        if operation_name=='exists_vertex':args.append(int(payload['vertex']))
        elif operation_name in {'exists_edge','edge_weight'}:args.extend([int(payload['origin']),int(payload['target'])])
        returned=machine.invoke(fn,args)
        if not query:machine.graph=deepcopy(returned)
        memory=machine.snapshot()
    else:memory=machine.snapshot()
    index=len(lines)-1;phase='api_publication' if success else 'input_validation'
    step=dict(step_index=len(steps),line_index=index,line_text=lines[index],event_type='line',phase=phase,
        state_snapshot=steps[-1]['state_after'] if steps else before_state,state_after=deepcopy(after_state),console=[],debug={'stage':phase,'note':message})
    frame=build_graph_frame(operation_name=operation_name,payload=payload,step=step,source_lines=lines,success=success)
    frame.update(query_operation=query,construction_operation=not query,concept=phase,variables=[],call_stack=[],condition=None,
        memory_state=memory,instruction_state_before=memory,instruction_state_after=memory,
        instruction_event={'C_executed':False,'function':None,'phase':phase},
        narration={level:('La API publica su orden logico; listas retornadas por C son prestadas, no copias.' if query and success else message) for level in ['basic','intermediate','advanced']})
    if not steps:
        initial=deepcopy(frame);initial.update(concept='initial',state_before=deepcopy(before_state),state_after=deepcopy(before_state))
        frame['initial_frame']=initial
    validate_graph_frame(frame,source_code=source_code);step['pedagogy']=frame;steps.append(pool.intern(step))
    trace.update(execution_started=bool(success),C_instruction_events=machine.events)
    validate_graph_logical_trace(trace)
    return trace
