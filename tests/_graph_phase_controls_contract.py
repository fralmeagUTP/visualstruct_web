"""Public phase controls: inspect and interact only with the visible workflow."""
PUBLIC_OPERATIONS = {
    'construccion': {'insert_vertex', 'generate_random_graph', 'remove_vertex',
        'insert_edge', 'remove_edge', 'list_vertices', 'list_edges', 'neighbors', 'edge_weight'},
    'recorridos': {'run_bfs', 'run_dfs'},
    'camino-minimo': {'run_dijkstra', 'run_bellman_ford'},
    'expansion-minima': {'run_prim', 'run_kruskal'},
}


def assert_public_graph_phase_controls(phase, selector, options, active_visible, inactive_visible):
    expected_selector = '#graph-operation-select' if phase == 'construccion' else '#graph-algorithm-select'
    assert selector == expected_selector
    assert active_visible is True and inactive_visible is False
    assert len(options) == len(set(options)), 'Repeated public operation'
    assert set(options) == PUBLIC_OPERATIONS[phase]
