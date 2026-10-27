"""Application caller of the canonical C graph; projections are not algorithms.

Each operation owns one interpreter session. Storage is an insertion-order
serialization of its real heads; returned lists retain the C traversal order.
"""
from copy import deepcopy
from .book_c_subset import BookSession
from .graph_commands import materialize_random_commands
from .tad_grafo import NodoV, NodoA


FUNCTIONS = {
    'insert_vertex': ('grafo_insertar_vertice', ('vertex',)),
    'remove_vertex': ('grafo_eliminar_vertice', ('vertex',)),
    'insert_edge': ('grafo_insertar_arco', ('origin', 'target', 'weight')),
    'remove_edge': ('grafo_eliminar_arco', ('origin', 'target')),
    'exists_vertex': ('grafo_existe_vertice', ('vertex',)),
    'exists_edge': ('grafo_existe_arco', ('origin', 'target')),
    'list_vertices': ('grafo_vertices', ()),
    'list_edges': ('grafo_arcos', ()),
    'neighbors': ('grafo_sucesores', ('vertex',)),
    'edge_weight': ('grafo_costo_arco', ('origin', 'target')),
    'run_bfs': ('grafo_bfs', ('start',)),
    'run_dfs': ('grafo_dfs', ('start',)),
    'run_dijkstra': ('grafo_dijkstra', ('start', 'end')),
    'run_bellman_ford': ('grafo_bellman_ford', ('start', 'end')),
    'run_prim': ('grafo_prim', ('start',)),
    'run_kruskal': ('grafo_kruskal', ()),
}


def _publish_storage(adapter, state, directed):
    """Only copy C output. Rebuild linked serialization, never run old TAD code."""
    g = adapter.graph._g
    g._vertices = list(reversed(state['vertices']))
    g._arcos = [tuple(a) for a in reversed(state['arcs'])]
    g._marcas = dict(state['marks'])
    g.v = None
    for v in g._vertices:
        g.v = NodoV(v, g.v, g._marcas[v])
    g.a = None
    for o, d, w in g._arcos:
        g.a = NodoA(o, d, w, g.a)
    adapter.graph.dirigido = directed


def _result_projection(operation, args, call):
    """Copy the returned list/flag; path/total are folds over that exact list."""
    items = deepcopy(call['result_items'])
    ok = call['status'] in (None, 0)
    if operation in {'exists_vertex', 'exists_edge'}:
        return bool(call['returned'])
    if operation == 'edge_weight':
        return call['output'] if call['returned'] == 1 else None
    if operation in {'list_vertices', 'list_edges', 'neighbors', 'run_bfs', 'run_dfs'}:
        return items
    if operation in {'run_dijkstra', 'run_bellman_ford'}:
        path = ([args[0]] + [a[1] for a in items]) if ok else []
        return {'start':args[0], 'end':args[1], 'path':path,
                'path_edges':[[a[0],a[1]] for a in items], 'path_arcs':items,
                'reachable':ok, 'distance_to_destination':sum(a[2] for a in items) if ok else None,
                'has_negative_cycle':call['status'] == 4}
    if operation in {'run_prim', 'run_kruskal'}:
        result = {'mst_edges':items, 'total_weight':sum(a[2] for a in items) if ok else None,
                  'connected':ok, 'kind':'mst' if ok else 'error'}
        if operation == 'run_prim':result['start'] = args[0]
        return result
    return None


def execute_book_operation(adapter, operation, payload):
    """Validate host inputs, execute canonical calls, and publish exact C state."""
    directed = adapter.graph.dirigido
    commands = None
    seed = None
    if operation == 'create_graph':
        directed = adapter._parse_bool(payload.get('directed', False))
    elif operation == 'generate_random_graph':
        seed, commands = materialize_random_commands(payload, directed)
    elif operation not in FUNCTIONS and operation != 'clear_graph':
        raise ValueError(f'Operacion no soportada: {operation}.')
    args = []
    if operation in FUNCTIONS:
        for key in FUNCTIONS[operation][1]:
            value = adapter._parse_weight(payload) if key == 'weight' else adapter._require_vertex(payload, key, key)
            if not -(1 << 31) <= value < (1 << 31):
                raise ValueError(f'{key} debe estar en el rango int32 del C canónico.')
            args.append(value)
    failure = payload.get('fail_allocation')
    if failure is not None and (type(failure) is not int or failure < 1):
        raise ValueError('fail_allocation debe ser un índice positivo relativo a esta operación.')
    g = adapter.graph._g
    session = BookSession(g._vertices, g._arcos, g._marcas, trace=False,
                          callback=getattr(adapter, '_book_callback', None), fail_allocation=failure,
                          event_limit=getattr(adapter, '_book_event_limit', None))
    calls = []
    primary = None
    def invoke(function, values=()):
        nonlocal primary
        raw = session.call(function, values)
        compact = {key:deepcopy(value) for key,value in raw.items()
                   if key not in {'memory','events','transitions','source_code'}}
        calls.append(compact)
        if raw['ownership'] == 'owned':
            session.free_result(raw['returned'], raw['return_type'])
            compact['caller_cleanup'] = 'grafo_liberar_vertices' if raw['return_type'] == 'ListaVertice' else 'grafo_liberar_arcos'
            compact['released_by_caller'] = True
        primary = compact
        return compact
    def insertion(op, values):
        first = invoke(FUNCTIONS[op][0], values)
        if op == 'insert_edge' and not directed and values[0] != values[1] and first['status'] == 0:
            invoke('grafo_insertar_arco', (values[1], values[0], values[2]))
        return first
    if operation in {'create_graph', 'clear_graph', 'generate_random_graph'}:
        invoke('grafo_destruir')
        invoke('grafo_crear')
        if commands is not None:
            # Record the actual seed for replay. Preparation is not a TAD algorithm.
            payload['seed'] = seed
            for command in commands:
                op = command['operation']; p = command['payload']
                insertion(op, [p[k] for k in FUNCTIONS[op][1]])
                # Like the generated main, later independent commands still execute.
    elif operation in {'insert_vertex','insert_edge'}:
        insertion(operation, args)
    else:
        invoke(FUNCTIONS[operation][0], args)
        if operation == 'remove_edge' and not directed and args[0] != args[1]:
            invoke('grafo_eliminar_arco', (args[1], args[0]))
    state = session.graph_state()
    _publish_storage(adapter, state, directed)
    failed = next((call for call in calls if call['status'] not in (None,0)), None)
    outcome = failed or primary
    result = _result_projection(operation, args, primary) if operation in FUNCTIONS else None
    if commands is not None:
        result = {'vertices_count':len(state['vertices']), 'edges_count':adapter.graph.cantidad_aristas(), 'seed':seed}
    success = failed is None
    # An absent cost is a real int-returning query, not an invented GrafoEstado.
    if operation == 'edge_weight' and primary['returned'] != 1:success = False
    status_text = outcome['status_name'] or 'sin salida GrafoEstado'
    message = f"{outcome['function']}: {status_text}."
    if operation == 'edge_weight':
        message = f"grafo_costo_arco: retorno {primary['returned']}; " + (f"costo {primary['output']}." if success else 'no escribe la salida porque no existe el arco.')
    if failed and len(calls)>1:
        message += ' Se conserva el efecto real de cada llamada; no hay reversión automática.'
    answer = {'success':success, 'message':message, 'result':result,
              'c_status':outcome['status'], 'c_status_name':outcome['status_name'],
              'c_return':outcome['returned'], 'output':outcome['output'],
              'ownership':outcome['ownership'], 'source_contract':'graph-book/v1'}
    adapter._last_book_execution = {'calls':calls, 'source_code':session.source,
        'source_contract':'graph-book/v1', 'source_sha256':outcome['source_sha256'],
        'graph_after':state, 'memory_after':session.machine.snapshot() if session.capture_result_memory else None,
        'event_count':session.machine.event_count,
        'result':deepcopy(answer), 'stdout':session.machine.stdout, 'transitions':[]}
    return answer
