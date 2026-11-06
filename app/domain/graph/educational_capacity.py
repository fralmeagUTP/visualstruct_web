"""Educational application capacity; downloadable C algorithms stay unbounded."""
MAX_VERTICES = 15

class GraphCapacityError(ValueError):
    """Reject before any graph, query outcome, history or RNG mutation."""

def check_capacity(graph, operation, payload, require_vertex, require_int):
    count=graph.cantidad_vertices()
    message=f"El límite educativo es de {MAX_VERTICES} vértices. No se modificó el grafo ni el historial."
    if count>MAX_VERTICES and (operation in {'insert_vertex','insert_edge'} or operation.startswith('run_')):
        raise GraphCapacityError(message+" Esta sesión anterior conserva todos sus datos; elimina vértices o limpia el grafo para volver al límite.")
    try:
        if operation=='generate_random_graph':
            requested=require_int(payload,'vertices_count','cantidad de vértices')
            if requested>MAX_VERTICES:raise GraphCapacityError(message)
        elif operation=='insert_vertex':
            vertex=require_vertex(payload,'vertex','vertice')
            if count+int(not graph.existe_vertice(vertex))>MAX_VERTICES:raise GraphCapacityError(message)
        elif operation=='insert_edge':
            vertices={require_vertex(payload,'origin','origen'),require_vertex(payload,'target','destino')}
            if count+sum(not graph.existe_vertice(vertex) for vertex in vertices)>MAX_VERTICES:raise GraphCapacityError(message)
    except GraphCapacityError:raise
    except (ValueError,TypeError,KeyError):
        # Preserve the existing detailed payload validation/error path.
        return
